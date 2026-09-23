"""Alpaca real-time WebSocket client with auto-reconnect.

One instance per endpoint (stocks: /v2/{feed}, crypto: /v1beta3/crypto/us). Message frames are
JSON arrays of objects tagged by "T":
    t trade | q quote | b minute bar | u updated bar | s trading status
    success | subscription | error (control messages)
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from collections.abc import Awaitable, Callable
from typing import Any

import websockets

from ..models import Quote, Trade, TradingStatus, parse_ts
from .alpaca_rest import parse_bar

log = logging.getLogger(__name__)

# Error codes documented by Alpaca for the market-data stream.
AUTH_FAILED = 402
CONNECTION_LIMIT = 406
INSUFFICIENT_SUBSCRIPTION = 409

Handler = Callable[[str, Any], Awaitable[None]]  # (kind, payload)
StateHandler = Callable[[str, str], Awaitable[None]]  # (state, detail)


def parse_message(item: dict, feed: str) -> tuple[str, Any] | None:
    """Convert one stream object into (kind, model). Returns None for control/unknown messages."""
    t = item.get("T")
    sym = item.get("S", "")
    if t == "t":
        return "trade", Trade(sym, parse_ts(item["t"]), float(item["p"]), float(item.get("s") or 0), item.get("c") or [])
    if t == "q":
        return "quote", Quote(
            sym,
            parse_ts(item["t"]),
            float(item.get("bp") or 0),
            float(item.get("ap") or 0),
            float(item.get("bs") or 0),
            float(item.get("as") or 0),
        )
    if t in ("b", "u"):
        return ("bar" if t == "b" else "updated_bar"), parse_bar(sym, item, feed)
    if t == "s":
        return "status", TradingStatus(
            sym, parse_ts(item["t"]), str(item.get("sc", "")), str(item.get("sm", "")), str(item.get("rm", ""))
        )
    return None


class AlpacaStream:
    def __init__(
        self,
        *,
        url: str,
        key: str,
        secret: str,
        subscriptions: list[dict],
        feed_tag: str,
        on_message: Handler,
        on_state: StateHandler,
        is_expected_active: Callable[[], bool] = lambda: True,
        stale_after_s: float = 90.0,
        name: str = "stream",
    ) -> None:
        self.url = url
        self.key = key
        self.secret = secret
        # Sent as separate subscribe messages so an optional channel (e.g. statuses on a plan that
        # lacks it) cannot break the core trades/bars subscription.
        self.subscriptions = subscriptions
        self.feed_tag = feed_tag
        self.on_message = on_message
        self.on_state = on_state
        self.is_expected_active = is_expected_active
        self.stale_after_s = stale_after_s
        self.name = name
        self.connected = False
        self.last_message_at = 0.0
        self._stop = asyncio.Event()

    def stop(self) -> None:
        self._stop.set()

    async def run(self) -> None:
        backoff = 1.0
        while not self._stop.is_set():
            try:
                await self._session()
                backoff = 1.0
            except _FatalStreamError as e:
                await self._set_state("error", str(e))
                backoff = max(backoff, e.retry_after)
            except asyncio.CancelledError:
                raise
            except Exception as e:  # noqa: BLE001 - any failure -> reconnect
                await self._set_state("disconnected", f"{type(e).__name__}: {e}")
            if self._stop.is_set():
                break
            wait = backoff + random.uniform(0, backoff / 2)
            log.info("[%s] reconnecting in %.1fs", self.name, wait)
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=wait)
            except asyncio.TimeoutError:
                pass
            backoff = min(backoff * 2, 60.0)
        await self._set_state("disconnected", "stopped")

    async def _set_state(self, state: str, detail: str = "") -> None:
        self.connected = state == "connected"
        log.info("[%s] %s %s", self.name, state, detail)
        try:
            await self.on_state(state, detail)
        except Exception:  # noqa: BLE001
            log.exception("state handler failed")

    async def _session(self) -> None:
        async with websockets.connect(
            self.url, ping_interval=20, ping_timeout=20, open_timeout=15, max_size=2**23
        ) as ws:
            await self._expect(ws, "connected")
            await ws.send(json.dumps({"action": "auth", "key": self.key, "secret": self.secret}))
            await self._expect(ws, "authenticated")
            for sub in self.subscriptions:
                await ws.send(json.dumps({"action": "subscribe", **sub}))
            self.last_message_at = time.monotonic()
            await self._set_state("connected", self.url)

            watchdog = asyncio.create_task(self._watchdog(ws))
            stopper = asyncio.create_task(self._stop.wait())
            try:
                async for raw in ws:
                    self.last_message_at = time.monotonic()
                    await self._dispatch(raw)
                    if stopper.done():
                        break
            finally:
                watchdog.cancel()
                stopper.cancel()
        await self._set_state("disconnected", "socket closed")

    async def _expect(self, ws, msg: str) -> None:  # noqa: ANN001
        raw = await asyncio.wait_for(ws.recv(), timeout=15)
        for item in json.loads(raw):
            if item.get("T") == "error":
                raise _FatalStreamError.from_item(item)
            if item.get("T") == "success" and item.get("msg") == msg:
                return
        raise RuntimeError(f"expected '{msg}', got {raw!r:.200}")

    async def _dispatch(self, raw: str | bytes) -> None:
        try:
            items = json.loads(raw)
        except ValueError:
            log.warning("[%s] non-JSON frame: %r", self.name, raw[:200])
            return
        for item in items if isinstance(items, list) else [items]:
            kind = item.get("T")
            if kind == "error":
                code = item.get("code")
                # Optional channel rejected: log and keep going.
                if code == INSUFFICIENT_SUBSCRIPTION:
                    log.warning("[%s] subscription rejected: %s", self.name, item.get("msg"))
                    await self.on_message("warning", f"subscription rejected: {item.get('msg')}")
                    continue
                raise _FatalStreamError.from_item(item)
            if kind == "subscription":
                log.info("[%s] subscribed: %s", self.name, {k: v for k, v in item.items() if k != "T"})
                continue
            try:
                parsed = parse_message(item, self.feed_tag)
            except (KeyError, ValueError, TypeError) as e:
                log.warning("[%s] bad message %r: %s", self.name, item, e)
                continue
            if parsed:
                await self.on_message(*parsed)

    async def _watchdog(self, ws) -> None:  # noqa: ANN001
        """Force a reconnect if the socket goes silent while data is expected (e.g. regular hours)."""
        while True:
            await asyncio.sleep(min(15.0, self.stale_after_s / 3))
            silent = time.monotonic() - self.last_message_at
            if self.is_expected_active() and silent > self.stale_after_s:
                log.warning("[%s] no data for %.0fs; forcing reconnect", self.name, silent)
                await ws.close(code=4000, reason="stale")
                return


class _FatalStreamError(RuntimeError):
    def __init__(self, msg: str, retry_after: float) -> None:
        super().__init__(msg)
        self.retry_after = retry_after

    @classmethod
    def from_item(cls, item: dict) -> _FatalStreamError:
        code = item.get("code")
        msg = f"stream error {code}: {item.get('msg')}"
        if code == AUTH_FAILED:
            return cls(msg + " (check ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY)", 300.0)
        if code == CONNECTION_LIMIT:
            return cls(msg + " (another app is using this key's stream connection)", 30.0)
        return cls(msg, 5.0)
