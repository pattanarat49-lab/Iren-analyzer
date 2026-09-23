"""Nightly retrain: after each trading day's extended session ends, refresh history and retrain.

Runs `scripts.backfill` (incremental; Alpaca mode only) and then `scripts.train` as subprocesses so
the heavy work never blocks the live server. The predictor picks up the new model files by
modification time. Status is kept in memory for the API and written to the events table.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timedelta, timezone

from .. import db
from ..config import BACKEND_DIR, Settings
from ..market.clock import ET, dual_time, trading_day

log = logging.getLogger(__name__)
UTC = timezone.utc


def next_retrain_time(now: datetime, delay_min: int = 30) -> datetime:
    """`delay_min` after the end of the next extended session (20:00 ET, 17:00 on half days)."""
    d = now.astimezone(ET).date()
    for _ in range(15):
        td = trading_day(d)
        if td:
            t = td.after_close + timedelta(minutes=delay_min)
            if t > now:
                return t
        d += timedelta(days=1)
    raise RuntimeError("no trading day in the next 15 days")


class Retrainer:
    def __init__(self, settings: Settings, engine, timeout_s: float = 2 * 3600) -> None:  # noqa: ANN001
        self.s = settings
        self.engine = engine
        self.timeout_s = timeout_s
        self.state = "idle"  # idle | running | ok | failed
        self.last_started: datetime | None = None
        self.last_finished: datetime | None = None
        self.last_message = ""
        self.next_run: datetime | None = None
        self._lock = asyncio.Lock()

    def status(self) -> dict:
        return {
            "enabled": self.s.retrain_enabled,
            "state": self.state,
            "last_started": dual_time(self.last_started),
            "last_finished": dual_time(self.last_finished),
            "last_message": self.last_message,
            "next_run": dual_time(self.next_run),
        }

    async def loop(self) -> None:
        while True:
            self.next_run = next_retrain_time(datetime.now(UTC), self.s.retrain_delay_min)
            wait = (self.next_run - datetime.now(UTC)).total_seconds()
            log.info("next retrain at %s", self.next_run.astimezone(ET))
            await asyncio.sleep(max(1.0, wait))
            await self.run()

    async def _step(self, *args: str) -> tuple[int, str]:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", *args, cwd=str(BACKEND_DIR),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        )
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_s)
        except asyncio.TimeoutError:
            proc.kill()
            return -1, f"{args[0]} timed out"
        text = out.decode(errors="replace").strip().splitlines()
        return proc.returncode or 0, "\n".join(text[-12:])

    async def run(self) -> None:
        if self._lock.locked():
            return
        async with self._lock:
            self.state = "running"
            self.last_started = datetime.now(UTC)
            self._event("retrain_started", None)
            try:
                if self.s.resolved_source == "alpaca":
                    code, msg = await self._step("scripts.backfill")
                    if code != 0:
                        raise RuntimeError(f"backfill failed: {msg}")
                code, msg = await self._step("scripts.train")
                if code != 0:
                    raise RuntimeError(f"train failed: {msg}")
                self.state, self.last_message = "ok", msg
                self._event("retrain_ok", msg[-500:])
            except Exception as e:  # noqa: BLE001
                self.state, self.last_message = "failed", str(e)
                log.error("retrain failed: %s", e)
                self._event("retrain_failed", str(e)[-500:])
            finally:
                self.last_finished = datetime.now(UTC)

    def _event(self, kind: str, detail: str | None) -> None:
        try:
            db.log_event(self.engine, datetime.now(UTC), kind, detail)
        except Exception:  # noqa: BLE001
            log.exception("failed to log retrain event")
