"""Simulated market data, used when no Alpaca keys are configured (DATA_SOURCE=demo/auto).

Prices follow a correlated random walk (one common "AI/crypto infra" factor + idiosyncratic
noise). Everything produced here is tagged feed="demo" and stored in a separate demo database,
so it can never be mixed with real data or used for training.
"""

from __future__ import annotations

import asyncio
import math
import random
from datetime import datetime, timedelta, timezone

from .. import db
from ..market.clock import session_at
from ..models import Bar, Trade
from .hub import MarketHub

UTC = timezone.utc

SEED_PRICES = {"IREN": 40.0, "CIFR": 15.0, "CRWV": 120.0, "NBIS": 100.0, "NVDA": 180.0, "QQQ": 580.0, "BTC/USD": 110_000.0}
# (beta to common factor, idiosyncratic vol) per minute
PARAMS = {
    "IREN": (1.6, 0.0015),
    "CRWV": (1.5, 0.0015),
    "CIFR": (1.7, 0.0018),
    "NBIS": (1.4, 0.0013),
    "NVDA": (1.0, 0.0007),
    "QQQ": (0.5, 0.0002),
    "BTC/USD": (0.8, 0.0006),
}
FACTOR_VOL = 0.001


class Simulator:
    def __init__(self, symbols: list[str], seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.price = {s: SEED_PRICES.get(s, 50.0) for s in symbols}

    def step(self, dt_minutes: float) -> dict[str, float]:
        f = self.rng.gauss(0, FACTOR_VOL) * math.sqrt(dt_minutes)
        for s in self.price:
            beta, vol = PARAMS.get(s, (1.0, 0.002))
            r = beta * f + self.rng.gauss(0, vol) * math.sqrt(dt_minutes)
            self.price[s] = max(0.01, self.price[s] * math.exp(r))
        return dict(self.price)

    def minute_bar(self, symbol: str, ts: datetime, factor: float, n_ticks: int = 6) -> Bar:
        """One simulated 1-minute bar; `factor` is the common market move for this minute."""
        beta, vol = PARAMS.get(symbol, (1.0, 0.002))
        o = self.price[symbol]
        path = [o]
        for _ in range(n_ticks):
            r = (beta * factor + self.rng.gauss(0, vol)) / math.sqrt(n_ticks)
            path.append(path[-1] * math.exp(r))
        self.price[symbol] = path[-1]
        base_vol = 200_000 if symbol == "IREN" else 50_000
        v = abs(self.rng.gauss(base_vol, base_vol / 3))
        return Bar(symbol, ts, o, max(path), min(path), path[-1], v, sum(path) / len(path), n_ticks, "demo")


def seed_history(hub: MarketHub, days: int = 30, seed: int = 7) -> int:
    """Generate recent 1-minute history (extended hours for stocks, 24/7 for crypto) if empty."""
    symbols = hub.s.all_symbols
    if all(db.latest_bar_ts(hub.engine, s) for s in symbols):
        return 0
    sim = Simulator(symbols, seed=seed)
    now = datetime.now(UTC).replace(second=0, microsecond=0)
    start = now - timedelta(days=days)
    bars: list[Bar] = []
    ts = start
    while ts < now:
        ss = session_at(ts)
        factor = sim.rng.gauss(0, FACTOR_VOL)
        for s in symbols:
            if "/" in s or ss.session != "closed":
                bars.append(sim.minute_bar(s, ts, factor))
        ts += timedelta(minutes=1)
    return db.upsert_bars(hub.engine, bars)


async def run_demo(hub: MarketHub, tick_s: float = 0.5) -> None:
    hub._set_mode("demo", "ข้อมูลจำลอง (ยังไม่ได้ตั้งค่า Alpaca API key)")
    await asyncio.to_thread(seed_history, hub)
    await hub.history_loaded()
    sim = Simulator(hub.s.all_symbols)
    for s, st in hub.state.items():
        if st.price:
            sim.price[s] = st.price
        st.prev_close = st.prev_close or hub.prev_close_from_db(s) or (st.price or sim.price[s])

    minute = datetime.now(UTC).replace(second=0, microsecond=0)
    opens = dict(sim.price)
    hi, lo, vol = dict(sim.price), dict(sim.price), {s: 0.0 for s in sim.price}
    while True:
        await asyncio.sleep(tick_s)
        now = datetime.now(UTC)
        cur = now.replace(second=0, microsecond=0)
        if cur > minute:
            for s in sim.price:
                bar = Bar(s, minute, opens[s], hi[s], lo[s], sim.price[s], vol[s], None, None, "demo")
                await hub.on_bar(bar)
            minute = cur
            opens, hi, lo = dict(sim.price), dict(sim.price), dict(sim.price)
            vol = {s: 0.0 for s in sim.price}
        prices = sim.step(tick_s / 60)
        for s, p in prices.items():
            size = float(random.randint(1, 20) * 100)
            hi[s], lo[s] = max(hi[s], p), min(lo[s], p)
            vol[s] += size
            await hub.handle("trade", Trade(s, now, round(p, 4 if p < 1000 else 2), size))

