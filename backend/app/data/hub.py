"""MarketHub: the single place that owns live market state.

- Consumes a data source (Alpaca stream + REST, or the demo simulator).
- Persists completed 1-minute bars to the database.
- Keeps per-symbol state (last price, change vs previous close, bid/ask, halt flag, forming bar).
- Falls back to REST polling while the WebSocket is down, and back-fills gaps after reconnecting.
- Broadcasts events to browser WebSocket clients and to in-process bar listeners (analysis engine).
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy.engine import Engine

from .. import db
from ..config import Settings
from ..market.clock import ET, dual_time, session_at, trading_day
from ..models import Bar, Quote, Trade, TradingStatus, parse_ts
from .alpaca_rest import AlpacaAuthError, AlpacaError, AlpacaRest, is_crypto

log = logging.getLogger(__name__)
UTC = timezone.utc

BarListener = Callable[[Bar], Awaitable[None]]

# Minimum seconds between "tick" broadcasts per symbol, so the browser is not flooded.
TICK_THROTTLE_S = 0.25


@dataclass
class SymbolState:
    symbol: str
    price: float | None = None
    price_ts: datetime | None = None
    prev_close: float | None = None
    session_close: float | None = None  # today's regular close, once known (after-hours change)
    bid: float | None = None
    ask: float | None = None
    halted: bool = False
    halt_reason: str = ""
    forming: Bar | None = None  # the current, not-yet-completed minute bar built from trades
    last_bar: Bar | None = None
    last_tick_sent: float = 0.0

    def to_json(self) -> dict:
        change = pct = None
        if self.price is not None and self.prev_close:
            change = self.price - self.prev_close
            pct = change / self.prev_close * 100
        ah_change = ah_pct = None
        if self.price is not None and self.session_close:
            ah_change = self.price - self.session_close
            ah_pct = ah_change / self.session_close * 100
        return {
            "symbol": self.symbol,
            "price": self.price,
            "prev_close": self.prev_close,
            "change": change,
            "change_pct": pct,
            "after_hours_change": ah_change,
            "after_hours_change_pct": ah_pct,
            "bid": self.bid,
            "ask": self.ask,
            "halted": self.halted,
            "halt_reason": self.halt_reason,
            "updated": dual_time(self.price_ts),
            "forming_bar": self.forming.to_json() if self.forming else None,
        }


@dataclass
class HubStatus:
    mode: str = "starting"  # starting | live | polling | demo | error
    detail: str = ""
    stream_states: dict[str, str] = field(default_factory=dict)


class MarketHub:
    def __init__(self, settings: Settings, engine: Engine, rest: AlpacaRest | None = None) -> None:
        self.s = settings
        self.engine = engine
        self.rest = rest
        self.state: dict[str, SymbolState] = {s: SymbolState(s) for s in settings.all_symbols}
        self.status = HubStatus()
        self._clients: set[asyncio.Queue] = set()
        self._bar_listeners: list[BarListener] = []
        self._tasks: list[asyncio.Task] = []
        self._streams: list[Any] = []
        self._stream_down_since: float | None = time.monotonic()
        self._needs_gap_fill = False
        self._last_trade_mono: dict[str, float] = {}

    # ---- subscribers -----------------------------------------------------------------------

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._clients.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._clients.discard(q)

    def add_bar_listener(self, fn: BarListener) -> None:
        self._bar_listeners.append(fn)

    def broadcast(self, event: dict) -> None:
        for q in list(self._clients):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                # Slow client: drop its oldest event rather than blocking the hub.
                try:
                    q.get_nowait()
                    q.put_nowait(event)
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    pass

    # ---- snapshot for new clients / REST API ----------------------------------------------

    def snapshot(self) -> dict:
        now = datetime.now(UTC)
        return {
            "type": "snapshot",
            "server_time": dual_time(now),
            "market": session_at(now).to_dict(),
            "status": self.status_json(),
            "quotes": {s: st.to_json() for s, st in self.state.items()},
        }

    def status_json(self) -> dict:
        return {
            "mode": self.status.mode,
            "detail": self.status.detail,
            "streams": self.status.stream_states,
            **self.s.public(),
        }

    def _set_mode(self, mode: str, detail: str = "") -> None:
        if (mode, detail) == (self.status.mode, self.status.detail):
            return
        self.status.mode, self.status.detail = mode, detail
        now = datetime.now(UTC)
        try:
            db.log_event(self.engine, now, mode, detail or None)
        except Exception:  # noqa: BLE001
            log.exception("failed to log event")
        self.broadcast({"type": "status", "status": self.status_json()})

    # ---- inbound data (called by sources) --------------------------------------------------

    async def handle(self, kind: str, payload: Any) -> None:
        if kind == "trade":
            self._on_trade(payload)
        elif kind == "quote":
            self._on_quote(payload)
        elif kind in ("bar", "updated_bar"):
            await self.on_bar(payload, updated=kind == "updated_bar")
        elif kind == "status":
            self._on_status(payload)
        elif kind == "warning":
            self._set_mode(self.status.mode, str(payload))

    def _on_trade(self, t: Trade) -> None:
        st = self.state.get(t.symbol)
        if st is None or t.price <= 0:
            return
        if st.price_ts is None or t.ts >= st.price_ts:
            st.price, st.price_ts = t.price, t.ts
        self._last_trade_mono[t.symbol] = time.monotonic()
        if st.halted and not is_crypto(t.symbol):
            # A trade printing means trading has resumed even if we missed the status message.
            st.halted, st.halt_reason = False, ""

        minute = t.ts.replace(second=0, microsecond=0)
        f = st.forming
        if f is None or minute > f.ts:
            st.forming = Bar(t.symbol, minute, t.price, t.price, t.price, t.price, t.size, feed="live")
        elif minute == f.ts:
            f.high, f.low, f.close = max(f.high, t.price), min(f.low, t.price), t.price
            f.volume += t.size
        self._maybe_tick(st)

    def _on_quote(self, q: Quote) -> None:
        st = self.state.get(q.symbol)
        if st is None:
            return
        st.bid, st.ask = (q.bid or None), (q.ask or None)
        self._maybe_tick(st)

    def _on_status(self, s: TradingStatus) -> None:
        st = self.state.get(s.symbol)
        if st is None:
            return
        st.halted = s.halted
        st.halt_reason = f"{s.message} {s.reason}".strip() if s.halted else ""
        self.broadcast({"type": "quote", "quote": st.to_json()})
        try:
            db.log_event(self.engine, s.ts, "halt" if s.halted else "resume", f"{s.symbol} {s.code} {st.halt_reason}")
        except Exception:  # noqa: BLE001
            log.exception("failed to log status event")

    def _maybe_tick(self, st: SymbolState) -> None:
        now = time.monotonic()
        if now - st.last_tick_sent >= TICK_THROTTLE_S:
            st.last_tick_sent = now
            self.broadcast({"type": "quote", "quote": st.to_json()})

    async def on_bar(self, bar: Bar, *, updated: bool = False, persist: bool = True) -> None:
        st = self.state.get(bar.symbol)
        if st is None:
            return
        if persist:
            await asyncio.to_thread(db.upsert_bars, self.engine, [bar])
        if st.last_bar is None or bar.ts >= st.last_bar.ts:
            st.last_bar = bar
            # Bars are stamped with their open time; the close is ~1 min later.
            bar_end = bar.ts + timedelta(minutes=1)
            if st.price_ts is None or bar_end > st.price_ts:
                st.price, st.price_ts = bar.close, min(bar_end, datetime.now(UTC))
            if st.forming is not None and st.forming.ts <= bar.ts:
                st.forming = None
        self.broadcast({"type": "bar", "updated": updated, "bar": bar.to_json()})
        self.broadcast({"type": "quote", "quote": st.to_json()})
        if not updated:
            for fn in self._bar_listeners:
                try:
                    await fn(bar)
                except Exception:  # noqa: BLE001
                    log.exception("bar listener failed")

    async def on_stream_state(self, name: str, state: str, detail: str) -> None:
        self.status.stream_states[name] = state
        all_up = bool(self._streams) and all(getattr(s, "connected", False) for s in self._streams)
        if all_up:
            if self._stream_down_since is not None:
                self._needs_gap_fill = True
            self._stream_down_since = None
            self._set_mode("live", "")
        else:
            if self._stream_down_since is None:
                self._stream_down_since = time.monotonic()
            if state == "error":
                self._set_mode("error", f"{name}: {detail}")
            elif self.status.mode in ("starting", "live"):
                self._set_mode("polling", f"{name} {state}; using REST polling")
        self.broadcast({"type": "status", "status": self.status_json()})

    # ---- lifecycle ------------------------------------------------------------------------

    def load_recent_from_db(self) -> None:
        """Seed last price/bar from the DB without overwriting anything newer seen live."""
        for sym, st in self.state.items():
            bars = db.load_bars(self.engine, sym, limit=1)
            if not bars:
                continue
            b = bars[-1]
            if st.last_bar is None or b.ts > st.last_bar.ts:
                st.last_bar = b
            end = b.ts + timedelta(minutes=1)
            if st.price_ts is None or end > st.price_ts:
                st.price, st.price_ts = b.close, end

    def start_task(self, coro) -> asyncio.Task:  # noqa: ANN001
        t = asyncio.create_task(coro)
        self._tasks.append(t)
        return t

    async def stop(self) -> None:
        for s in self._streams:
            s.stop()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()


# ---------------------------------------------------------------------------------------------
# Alpaca wiring
# ---------------------------------------------------------------------------------------------


def reference_trading_day(now: datetime) -> date:
    """The trading day whose price change we display (the current or most recently finished one)."""
    ss = session_at(now)
    if ss.trading_day and ss.session != "closed":
        return ss.trading_day.day
    d = now.astimezone(ET).date()
    for _ in range(30):
        td = trading_day(d)
        if td and td.close <= now:
            return d
        d -= timedelta(days=1)
    return now.astimezone(ET).date()


def closes_from_snapshot(snap: dict, ref_day: date) -> tuple[float | None, float | None]:
    """(previous close, reference-day close if the regular session has ended) from a stock snapshot."""
    daily: list[tuple[date, float]] = []
    for key in ("prevDailyBar", "dailyBar"):
        b = snap.get(key)
        if b and b.get("t") and b.get("c"):
            daily.append((parse_ts(b["t"]).astimezone(ET).date(), float(b["c"])))
    daily.sort()
    prev = next((c for d, c in reversed(daily) if d < ref_day), None)
    same = next((c for d, c in daily if d == ref_day), None)
    return prev, same


async def run_alpaca(hub: MarketHub) -> None:
    from .alpaca_stream import AlpacaStream

    s = hub.s
    rest = hub.rest
    assert rest is not None
    primary = s.primary_symbol.upper()

    def regular_now() -> bool:
        return session_at(datetime.now(UTC)).session == "regular"

    stock_stream = AlpacaStream(
        url=f"{s.alpaca_stream_url}/v2/{s.alpaca_stock_feed}",
        key=s.alpaca_api_key_id,
        secret=s.alpaca_api_secret_key,
        subscriptions=[
            {"trades": s.stock_symbols, "quotes": [primary], "bars": s.stock_symbols, "updatedBars": s.stock_symbols},
            {"statuses": s.stock_symbols},
        ],
        feed_tag=s.alpaca_stock_feed,
        on_message=hub.handle,
        on_state=lambda st, d: hub.on_stream_state("stocks", st, d),
        is_expected_active=regular_now,
        stale_after_s=s.stream_stale_s,
        name="stocks",
    )
    streams = [stock_stream]
    if s.crypto_symbol_list:
        streams.append(
            AlpacaStream(
                url=f"{s.alpaca_stream_url}/v1beta3/crypto/us",
                key=s.alpaca_api_key_id,
                secret=s.alpaca_api_secret_key,
                subscriptions=[{"trades": s.crypto_symbol_list, "bars": s.crypto_symbol_list, "updatedBars": s.crypto_symbol_list}],
                feed_tag="crypto",
                on_message=hub.handle,
                on_state=lambda st, d: hub.on_stream_state("crypto", st, d),
                stale_after_s=s.stream_stale_s * 2,
                name="crypto",
            )
        )
    hub._streams = streams

    # Streams start immediately; history warm-up runs alongside so a slow or failing REST API
    # never delays live data.
    for st in streams:
        hub.start_task(st.run())
    hub.start_task(warm_up(hub))
    hub.start_task(_poll_loop(hub))
    hub.start_task(_snapshot_loop(hub))
    hub.start_task(_halt_watch(hub))


async def warm_up(hub: MarketHub, days: int = 7) -> None:
    """Make sure the last few days of bars are in the DB so charts/indicators have context."""
    rest = hub.rest
    assert rest is not None
    end = datetime.now(UTC)
    start_default = end - timedelta(days=days)
    stocks, cryptos = hub.s.stock_symbols, hub.s.crypto_symbol_list
    for group in (stocks, cryptos):
        if not group:
            continue
        latest = [db.latest_bar_ts(hub.engine, sym) for sym in group]
        starts = [ts + timedelta(minutes=1) if ts and ts > start_default else start_default for ts in latest]
        start = min(starts)
        if start >= end:
            continue
        try:
            n = 0
            async for page in rest.iter_bars(group, start, end, feed=hub.s.alpaca_stock_feed):
                n += await asyncio.to_thread(db.upsert_bars, hub.engine, page)
            log.info("warm-up stored %d bars for %s", n, ",".join(group))
        except AlpacaAuthError as e:
            hub._set_mode("error", f"Alpaca rejected the request: {e}")
        except AlpacaError as e:
            log.warning("warm-up failed: %s", e)
            if hub.status.mode != "live":
                hub._set_mode("error", f"ดึงข้อมูลย้อนหลังไม่สำเร็จ: {e}")
    hub.load_recent_from_db()


async def _gap_fill(hub: MarketHub) -> None:
    """After a reconnect, fetch any bars we missed while disconnected."""
    rest = hub.rest
    assert rest is not None
    end = datetime.now(UTC)
    for group in (hub.s.stock_symbols, hub.s.crypto_symbol_list):
        if not group:
            continue
        latest = [db.latest_bar_ts(hub.engine, sym) for sym in group]
        known = [ts for ts in latest if ts]
        if not known:
            continue
        start = min(known) + timedelta(minutes=1)
        if end - start > timedelta(days=7):
            start = end - timedelta(days=7)
        try:
            bars = await rest.get_bars(group, start, end, feed=hub.s.alpaca_stock_feed)
        except AlpacaError as e:
            log.warning("gap fill failed: %s", e)
            continue
        for b in sorted(bars, key=lambda b: b.ts):
            await hub.on_bar(b)
        if bars:
            log.info("gap fill: %d bars", len(bars))


async def _poll_loop(hub: MarketHub) -> None:
    """REST fallback while any stream is down; also performs gap fills after reconnects."""
    rest = hub.rest
    assert rest is not None
    grace_s = 20.0
    while True:
        await asyncio.sleep(hub.s.poll_interval_s)
        try:
            if hub._needs_gap_fill:
                hub._needs_gap_fill = False
                await _gap_fill(hub)
            down = hub._stream_down_since
            if down is None or time.monotonic() - down < grace_s:
                continue
            if hub.status.mode not in ("error", "polling"):
                hub._set_mode("polling", "WebSocket unavailable; polling REST every "
                              f"{hub.s.poll_interval_s:.0f}s")
            for b in await rest.latest_bars(hub.s.all_symbols):
                st = hub.state.get(b.symbol)
                if st and (st.last_bar is None or b.ts > st.last_bar.ts):
                    await hub.on_bar(b)
            if hub.status.mode == "error" and hub._stream_down_since is not None:
                hub._set_mode("polling", "WebSocket unavailable; polling REST every "
                              f"{hub.s.poll_interval_s:.0f}s")
        except AlpacaAuthError as e:
            hub._set_mode("error", f"Alpaca rejected the request: {e}")
            await asyncio.sleep(300)
        except Exception as e:  # noqa: BLE001
            log.warning("poll failed: %s", e)
            if hub._stream_down_since is not None:
                hub._set_mode("error", f"เชื่อมต่อ Alpaca ไม่ได้ทั้ง WebSocket และ REST: {e}")


async def _snapshot_loop(hub: MarketHub) -> None:
    """Refresh previous close / latest trade every minute (cheap: 2 requests)."""
    rest = hub.rest
    assert rest is not None
    while True:
        try:
            snaps = await rest.snapshots(hub.s.all_symbols)
            ref_day = reference_trading_day(datetime.now(UTC))
            ss = session_at(datetime.now(UTC)).session
            for sym, snap in snaps.items():
                st = hub.state.get(sym)
                if st is None:
                    continue
                if is_crypto(sym):
                    prev = (snap.get("prevDailyBar") or {}).get("c")
                    st.prev_close = float(prev) if prev else st.prev_close
                else:
                    prev, same = closes_from_snapshot(snap, ref_day)
                    st.prev_close = prev or st.prev_close
                    st.session_close = same if ss in ("after", "closed") else None
                lt = snap.get("latestTrade")
                if lt and lt.get("p"):
                    ts = parse_ts(lt["t"])
                    if st.price_ts is None or ts > st.price_ts:
                        st.price, st.price_ts = float(lt["p"]), ts
                lq = snap.get("latestQuote")
                if lq and sym == hub.s.primary_symbol.upper():
                    st.bid, st.ask = (lq.get("bp") or None), (lq.get("ap") or None)
                hub.broadcast({"type": "quote", "quote": st.to_json()})
        except AlpacaAuthError as e:
            hub._set_mode("error", f"Alpaca rejected the request: {e}")
        except Exception as e:  # noqa: BLE001
            log.warning("snapshot refresh failed: %s", e)
        await asyncio.sleep(60)


async def _halt_watch(hub: MarketHub) -> None:
    """Heuristic halt / stale-data flag for the primary symbol during the regular session."""
    sym = hub.s.primary_symbol.upper()
    limit = hub.s.halt_suspect_min * 60
    while True:
        await asyncio.sleep(30)
        st = hub.state[sym]
        if session_at(datetime.now(UTC)).session != "regular" or hub.status.mode != "live":
            continue
        last = hub._last_trade_mono.get(sym)
        quiet = last is not None and time.monotonic() - last > limit
        if quiet and not st.halted:
            st.halted, st.halt_reason = True, f"ไม่มีการซื้อขายเกิน {hub.s.halt_suspect_min} นาที (อาจถูกหยุดพักการซื้อขาย)"
            hub.broadcast({"type": "quote", "quote": st.to_json()})
