from datetime import datetime, timedelta, timezone

import numpy as np

from app import db
from app.analysis.engine import AnalysisEngine, bars_to_frame, resample
from app.data.hub import MarketHub
from app.models import Bar

UTC = timezone.utc


def make_bars(sym, n, start, p0=40.0, seed=0):
    rng = np.random.default_rng(seed)
    p = p0 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))
    return [
        Bar(sym, start + timedelta(minutes=i), p[i], p[i] * 1.001, p[i] * 0.999, p[i], 1000 + i, feed="demo")
        for i in range(n)
    ]


def test_resample_5min_ohlcv():
    start = datetime(2026, 9, 23, 13, 30, tzinfo=UTC)
    df = bars_to_frame(make_bars("IREN", 10, start))
    r = resample(df, 5)
    assert len(r) == 2
    first = df.iloc[:5]
    assert r.iloc[0]["open"] == first["open"].iloc[0]
    assert r.iloc[0]["high"] == first["high"].max()
    assert r.iloc[0]["low"] == first["low"].min()
    assert r.iloc[0]["close"] == first["close"].iloc[-1]
    assert r.iloc[0]["volume"] == first["volume"].sum()


async def test_engine_end_to_end(settings, engine):
    hub = MarketHub(settings, engine)
    start = datetime.now(UTC).replace(second=0, microsecond=0) - timedelta(minutes=300)
    for i, sym in enumerate(settings.all_symbols):
        db.upsert_bars(engine, make_bars(sym, 300, start, p0=40 + 10 * i, seed=i))
    eng = AnalysisEngine(hub)
    await eng.reload_async()
    res = eng.compute(1)
    assert res["ready"] and res["bars_used"] == 300
    assert [i["key"] for i in res["indicators"]] == ["ema9", "ema21", "ema50", "vwap", "rsi14", "macd", "bb", "atr14", "rvol"]
    assert {r["symbol"] for r in res["relative"]} == {"CRWV", "NBIS", "NVDA", "QQQ", "BTC/USD"}
    assert res["summary"]["overall"] in ("bullish", "bearish", "neutral")

    # A new bar is appended and triggers a recompute + broadcast.
    q = hub.subscribe()
    nb = make_bars("IREN", 1, start + timedelta(minutes=300), seed=9)[0]
    await eng.on_bar(nb)
    await eng._pending
    assert eng.latest[1]["bars_used"] == 301
    assert any(q.get_nowait()["type"] == "analysis" for _ in range(q.qsize()))

    ch = eng.chart("IREN", tf=5, limit=20)
    assert len(ch["bars"]) == 20 and "ema9" in ch["series"] and "rsi14" in ch["series"]


async def test_engine_without_data_is_not_ready(settings, engine):
    eng = AnalysisEngine(MarketHub(settings, engine))
    await eng.reload_async()
    res = eng.compute(1)
    assert res["ready"] is False


def test_epoch_seconds_independent_of_unit():
    import pandas as pd

    from app.analysis.engine import epoch_seconds

    idx = pd.DatetimeIndex(["2026-09-23 13:30:00"], tz="UTC")
    assert epoch_seconds(idx) == [1790170200]
    assert epoch_seconds(idx.as_unit("us")) == [1790170200]
