"""AnalysisEngine: keeps recent bars in memory and recomputes the analysis on every new bar."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from .. import db
from ..market.clock import dual_time
from ..models import Bar
from . import indicators as ind
from .relative import compare
from .signals import build_signals, summarize

log = logging.getLogger(__name__)
UTC = timezone.utc

COLUMNS = ["open", "high", "low", "close", "volume"]
TIMEFRAMES = (1, 5, 15)


def bars_to_frame(bars: list[Bar]) -> pd.DataFrame:
    if not bars:
        return pd.DataFrame(columns=COLUMNS, index=pd.DatetimeIndex([], tz="UTC"), dtype=float)
    df = pd.DataFrame(
        [(b.ts, b.open, b.high, b.low, b.close, b.volume) for b in bars], columns=["ts", *COLUMNS]
    )
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    return df.set_index("ts").sort_index()


def resample(df: pd.DataFrame, minutes: int) -> pd.DataFrame:
    """Aggregate 1-minute bars into N-minute bars (left-labelled, only intervals with trades)."""
    if minutes == 1 or df.empty:
        return df
    agg = df.resample(f"{minutes}min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    return agg.dropna(subset=["close"])


def epoch_seconds(index: pd.DatetimeIndex) -> list[int]:
    """Unix seconds, independent of the index's storage unit (ns in pandas 2, often us in pandas 3)."""
    return ((index - pd.Timestamp(0, tz="UTC")) // pd.Timedelta(seconds=1)).tolist()


def _clean(x):  # noqa: ANN001, ANN202
    if isinstance(x, (float, np.floating)):
        return None if np.isnan(x) else float(x)
    if isinstance(x, dict):
        return {k: _clean(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_clean(v) for v in x]
    return x


class AnalysisEngine:
    def __init__(self, hub, history_days: int = 30, max_rows: int = 60_000) -> None:  # noqa: ANN001
        self.hub = hub
        self.s = hub.s
        self.primary = self.s.primary_symbol.upper()
        self.history_days = history_days
        self.max_rows = max_rows
        self.frames: dict[str, pd.DataFrame] = {}
        self.latest: dict[int, dict] = {}
        self._pending: asyncio.Task | None = None
        self._dirty = False
        self.predictor = None  # set by main when models are available
        self.prediction: dict | None = None

    # ---- data ------------------------------------------------------------------------------

    def load_frames(self) -> dict[str, pd.DataFrame]:
        start = datetime.now(UTC) - timedelta(days=self.history_days)
        return {sym: bars_to_frame(db.load_bars(self.hub.engine, sym, start=start)) for sym in self.s.all_symbols}

    async def reload_async(self) -> None:
        """Reload from the DB (in a worker thread), then swap frames in on the event loop.

        Bars are written to the DB before listeners run, so any bar that arrives while loading is
        either in the loaded data or re-applied below from the old frame's tail.
        """
        frames = await asyncio.to_thread(self.load_frames)
        for sym, old in self.frames.items():
            new = frames.get(sym)
            if new is not None and not old.empty:
                newer = old[old.index > (new.index[-1] if not new.empty else old.index[0] - pd.Timedelta(1))]
                if not newer.empty:
                    frames[sym] = pd.concat([new, newer])
        self.frames = frames
        log.info("analysis loaded %s", {s: len(f) for s, f in self.frames.items()})
        self._dirty = True
        if self._pending is None or self._pending.done():
            self._pending = asyncio.create_task(self._recompute_soon(0))

    def add_bar(self, bar: Bar) -> None:
        df = self.frames.get(bar.symbol)
        if df is None:
            return
        ts = pd.Timestamp(bar.ts)
        row = [bar.open, bar.high, bar.low, bar.close, bar.volume]
        if not df.empty and ts <= df.index[-1]:
            df.loc[ts] = row  # correction or late bar
            if not df.index.is_monotonic_increasing:
                df.sort_index(inplace=True)
        else:
            df.loc[ts] = row
        if len(df) > self.max_rows:
            self.frames[bar.symbol] = df.iloc[-self.max_rows :]

    async def on_bar(self, bar: Bar) -> None:
        self.add_bar(bar)
        self._dirty = True
        # Bars for all symbols arrive together at each minute; debounce into one recompute.
        if self._pending is None or self._pending.done():
            self._pending = asyncio.create_task(self._recompute_soon())

    async def _recompute_soon(self, delay: float = 0.5) -> None:
        await asyncio.sleep(delay)
        while self._dirty:
            self._dirty = False
            t0 = time.perf_counter()
            try:
                result = await self.compute_async(1)
            except Exception:  # noqa: BLE001
                log.exception("analysis failed")
                return
            self.latest[1] = result
            self.hub.broadcast({"type": "analysis", "analysis": result})
            log.debug("analysis recomputed in %.0f ms", (time.perf_counter() - t0) * 1000)
            await self.update_prediction()

    async def update_prediction(self) -> None:
        if self.predictor is None:
            return
        from ..model.predictor import clean_json

        st = self.hub.state.get(self.primary)
        live = st.price if st else None
        try:
            self.predictor.load()  # cheap: only reloads files whose mtime changed
            pred = await asyncio.to_thread(self.predictor.predict, self.snapshot(), live)
        except Exception:  # noqa: BLE001
            log.exception("prediction failed")
            return
        self.prediction = clean_json(pred)
        self.hub.broadcast({"type": "prediction", "prediction": self.prediction})
        await self._log_prediction(self.prediction)

    async def _log_prediction(self, pred: dict) -> None:
        """Save one snapshot per horizon per bar for the live track record."""
        from ..model.tracking import snapshot_rows

        made_at = pred.get("made_at")
        if not made_at:
            return
        rows = snapshot_rows(pred, datetime.fromisoformat(made_at), self.s.resolved_source)
        if rows:
            try:
                await asyncio.to_thread(db.insert_predictions, self.hub.engine, rows)
            except Exception:  # noqa: BLE001
                log.exception("failed to store prediction snapshot")

    # ---- analysis --------------------------------------------------------------------------

    def snapshot(self) -> dict[str, pd.DataFrame]:
        """Copy of the in-memory frames, taken on the event loop so worker threads never race
        with incoming bars."""
        return {s: f.copy() for s, f in self.frames.items()}

    async def compute_async(self, tf: int = 1) -> dict:
        return await asyncio.to_thread(self.compute, tf, self.snapshot())

    async def chart_async(self, symbol: str, tf: int = 1, limit: int = 500) -> dict:
        frame = self.frames.get(symbol)
        frames = {symbol: frame.copy()} if frame is not None else {}
        return await asyncio.to_thread(self.chart, symbol, tf, limit, frames)

    def _live_price(self, sym: str, df: pd.DataFrame) -> float | None:
        st = self.hub.state.get(sym)
        if st and st.price:
            return float(st.price)
        return float(df["close"].iloc[-1]) if not df.empty else None

    def compute(self, tf: int = 1, frames: dict[str, pd.DataFrame] | None = None) -> dict:
        if tf not in TIMEFRAMES:
            raise ValueError(f"tf must be one of {TIMEFRAMES}")
        frames = self.frames if frames is None else frames
        now = datetime.now(UTC)
        base = frames.get(self.primary)
        if base is None or base.empty:
            return {"symbol": self.primary, "tf": tf, "ready": False, "as_of": dual_time(now),
                    "message": "ยังไม่มีข้อมูลราคา กำลังรอข้อมูลแท่งเทียน"}
        df = resample(base, tf)
        values = ind.compute_all(df)
        price = self._live_price(self.primary, df)
        st = self.hub.state.get(self.primary)
        prev_close = st.prev_close if st else None
        day_change = (price / prev_close - 1) if price and prev_close else None
        iex_only = self.s.resolved_source == "alpaca" and self.s.alpaca_stock_feed == "iex"

        sigs = build_signals(price, values, day_change=day_change, iex_only=iex_only, bar_minutes=tf)
        last = values.iloc[-1]
        today_ref = {s: (self.hub.state[s].prev_close if s in self.hub.state else None) for s in self.s.all_symbols}
        closes = {s: frames[s]["close"] for s in self.s.all_symbols if s in frames}
        # Use live prices as the latest point so "today" performance is current.
        for s, series in closes.items():
            lp = self.hub.state[s].price if s in self.hub.state else None
            if lp and not series.empty:
                closes[s] = pd.concat([series, pd.Series([lp], index=[pd.Timestamp(now)])])
        rel = [
            compare(self.primary, closes[self.primary], sym, closes[sym], today_ref=today_ref, now=pd.Timestamp(now))
            for sym in self.s.all_symbols
            if sym != self.primary and sym in closes
        ]
        return _clean({
            "symbol": self.primary,
            "tf": tf,
            "ready": True,
            "as_of": dual_time(now),
            "bar_time": dual_time(df.index[-1].to_pydatetime()),
            "price": price,
            "bars_used": len(df),
            "iex_only": iex_only,
            "indicators": [s.to_json() for s in sigs],
            "summary": summarize(sigs),
            "values": {k: last[k] for k in values.columns},
            "relative": rel,
        })

    def chart(self, symbol: str, tf: int = 1, limit: int = 500, frames: dict[str, pd.DataFrame] | None = None) -> dict:
        """Bars plus indicator series for the candlestick chart (Lightweight Charts format)."""
        if tf not in TIMEFRAMES:
            raise ValueError(f"tf must be one of {TIMEFRAMES}")
        frames = self.frames if frames is None else frames
        base = frames.get(symbol)
        if base is None or base.empty:
            return {"symbol": symbol, "tf": tf, "bars": [], "series": {}}
        df = resample(base, tf)
        values = ind.compute_all(df)
        # Compute on the full history (so EMA/RSI are warmed up), then return the tail.
        df, values = df.tail(limit), values.tail(limit)
        t = epoch_seconds(df.index)
        bars = [
            {"time": ti, "open": o, "high": h, "low": lo, "close": c, "volume": v}
            for ti, o, h, lo, c, v in zip(t, df["open"], df["high"], df["low"], df["close"], df["volume"])
        ]
        keys = ["ema9", "ema21", "ema50", "vwap", "bb_upper", "bb_mid", "bb_lower", "rsi14", "macd", "signal", "hist"]
        series = {
            k: [{"time": ti, "value": float(v)} for ti, v in zip(t, values[k]) if not np.isnan(v)] for k in keys
        }
        return {"symbol": symbol, "tf": tf, "bars": bars, "series": series}
