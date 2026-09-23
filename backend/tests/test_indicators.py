"""Indicator math: known values, independent reference implementations and no-look-ahead."""

import numpy as np
import pandas as pd
import pytest

from app.analysis import indicators as ind

# StockCharts' published RSI(14) example (closes and expected RSI values).
SC_CLOSES = [44.3389, 44.0902, 44.1497, 43.6124, 44.3278, 44.8264, 45.0955, 45.4245, 45.8433, 46.0826,
             45.8931, 46.0328, 45.6140, 46.2820, 46.2820, 46.0028, 46.0328, 46.4116, 46.2222, 45.6439]
SC_RSI = {14: 70.53, 15: 66.32, 16: 66.55, 17: 69.41, 18: 66.36, 19: 57.97}


def ohlcv(closes, start="2026-09-22 13:30", freq="1min", spread=0.5, volume=1000.0):
    idx = pd.date_range(start, periods=len(closes), freq=freq, tz="UTC")
    c = pd.Series(closes, index=idx, dtype=float)
    o = c.shift(1).fillna(c.iloc[0])
    return pd.DataFrame(
        {"open": o, "high": np.maximum(o, c) + spread, "low": np.minimum(o, c) - spread, "close": c,
         "volume": volume},
        index=idx,
    )


def random_walk(n=600, seed=1):
    rng = np.random.default_rng(seed)
    return 40 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))


# ---- reference implementations (deliberately naive loops) ----

def ref_ema(x, n):
    out = [np.nan] * len(x)
    a = 2 / (n + 1)
    prev = sum(x[:n]) / n
    out[n - 1] = prev
    for i in range(n, len(x)):
        prev = a * x[i] + (1 - a) * prev
        out[i] = prev
    return np.array(out)


def ref_atr(h, l, c, n):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    out = [np.nan] * len(c)
    prev = sum(tr[:n]) / n
    out[n - 1] = prev
    for i in range(n, len(c)):
        prev = (prev * (n - 1) + tr[i]) / n
        out[i] = prev
    return np.array(out)


# ---- EMA ----

def test_ema_seed_and_linear_lag():
    s = pd.Series(np.arange(1.0, 11.0))
    e = ind.ema(s, 3)
    assert e.iloc[:2].isna().all()
    assert e.iloc[2] == 2.0  # SMA seed of 1,2,3
    # For a linear series, EMA(3) settles exactly one step behind the price.
    np.testing.assert_allclose(e.iloc[3:], s.iloc[3:] - 1)


def test_ema_matches_reference():
    x = random_walk()
    np.testing.assert_allclose(ind.ema(pd.Series(x), 21), ref_ema(list(x), 21), equal_nan=True)


# ---- RSI ----

def test_rsi_matches_stockcharts_example():
    r = ind.rsi(pd.Series(SC_CLOSES), 14)
    assert r.iloc[:14].isna().all()
    for i, expected in SC_RSI.items():
        assert r.iloc[i] == pytest.approx(expected, abs=0.01), i


def test_rsi_extremes():
    up = ind.rsi(pd.Series(np.arange(1.0, 40.0)), 14)
    down = ind.rsi(pd.Series(np.arange(40.0, 1.0, -1)), 14)
    flat = ind.rsi(pd.Series(np.full(40, 5.0)), 14)
    assert up.iloc[-1] == 100 and down.iloc[-1] == 0 and flat.iloc[-1] == 50
    r = ind.rsi(pd.Series(random_walk()), 14).dropna()
    assert ((r >= 0) & (r <= 100)).all()


# ---- MACD ----

def test_macd_definition():
    s = pd.Series(random_walk())
    m = ind.macd(s)
    line = ref_ema(list(s), 12) - ref_ema(list(s), 26)
    np.testing.assert_allclose(m["macd"], line, equal_nan=True)
    valid = line[~np.isnan(line)]
    sig = ref_ema(list(valid), 9)
    np.testing.assert_allclose(m["signal"].dropna(), sig[~np.isnan(sig)])
    np.testing.assert_allclose(m["hist"], m["macd"] - m["signal"], equal_nan=True)
    assert m["signal"].first_valid_index() == 25 + 8


# ---- Bollinger ----

def test_bollinger_population_std():
    s = pd.Series(random_walk(100))
    bb = ind.bollinger(s, 20, 2)
    w = s.iloc[-20:].to_numpy()
    assert bb["mid"].iloc[-1] == pytest.approx(w.mean())
    assert bb["upper"].iloc[-1] == pytest.approx(w.mean() + 2 * w.std(ddof=0))
    assert bb["lower"].iloc[-1] == pytest.approx(w.mean() - 2 * w.std(ddof=0))
    pb = (s.iloc[-1] - bb["lower"].iloc[-1]) / (bb["upper"].iloc[-1] - bb["lower"].iloc[-1])
    assert bb["pct_b"].iloc[-1] == pytest.approx(pb)
    assert bb["mid"].iloc[:19].isna().all()


# ---- ATR ----

def test_true_range_uses_previous_close():
    h = pd.Series([10.0, 12.0, 11.0])
    l = pd.Series([9.0, 11.5, 8.0])
    c = pd.Series([9.5, 12.0, 9.0])
    tr = ind.true_range(h, l, c)
    assert list(tr) == [1.0, 2.5, 4.0]  # gap up from 9.5 -> 12; drop to 8 from 12


def test_atr_matches_reference():
    df = ohlcv(random_walk(300))
    a = ind.atr(df["high"], df["low"], df["close"], 14)
    ref = ref_atr(df["high"].tolist(), df["low"].tolist(), df["close"].tolist(), 14)
    np.testing.assert_allclose(a, ref, equal_nan=True)


# ---- VWAP ----

def test_vwap_cumulative_and_resets_each_et_day():
    idx = pd.DatetimeIndex(
        ["2026-09-22 19:58", "2026-09-22 19:59", "2026-09-23 08:00", "2026-09-23 08:01"], tz="UTC"
    )  # 15:58/15:59 ET on the 22nd, then 04:00/04:01 ET on the 23rd
    df = pd.DataFrame(
        {"high": [11, 13, 21, 23], "low": [9, 11, 19, 21], "close": [10, 12, 20, 22], "volume": [100, 300, 50, 150]},
        index=idx, dtype=float,
    )
    v = ind.vwap(df)
    assert v.iloc[0] == pytest.approx(10)
    assert v.iloc[1] == pytest.approx((10 * 100 + 12 * 300) / 400)
    assert v.iloc[2] == pytest.approx(20)  # new day -> reset
    assert v.iloc[3] == pytest.approx((20 * 50 + 22 * 150) / 200)


def test_vwap_zero_volume_falls_back_to_typical_price():
    df = ohlcv([10.0, 11.0], volume=0.0)
    v = ind.vwap(df)
    assert v.iloc[0] == pytest.approx((df["high"].iloc[0] + df["low"].iloc[0] + 10) / 3)


# ---- Relative volume ----

def test_relative_volume_time_of_day():
    frames = []
    days = pd.bdate_range("2026-09-01", periods=7, tz="UTC")
    for i, d in enumerate(days):
        idx = pd.date_range(d + pd.Timedelta(hours=13, minutes=30), periods=30, freq="1min")
        vol = np.arange(1, 31, dtype=float) * 100 * (2 if i == 6 else 1)
        frames.append(pd.DataFrame({"high": 1.0, "low": 1.0, "close": 1.0, "volume": vol}, index=idx))
    df = pd.concat(frames)
    rv = ind.relative_volume(df, lookback_days=20, min_days=5)
    first5 = rv.loc[: days[4] + pd.Timedelta(hours=23)]
    assert first5.isna().all().all()  # need 5 prior days
    day6 = rv.loc[days[5] + pd.Timedelta(hours=13):days[5] + pd.Timedelta(hours=23)]
    np.testing.assert_allclose(day6["rvol_bar"], 1.0)
    np.testing.assert_allclose(day6["rvol_cum"], 1.0)
    last = rv.loc[days[6] + pd.Timedelta(hours=13):]
    np.testing.assert_allclose(last["rvol_bar"], 2.0)
    np.testing.assert_allclose(last["rvol_cum"], 2.0)


# ---- no look-ahead ----

def test_compute_all_is_causal():
    df = ohlcv(random_walk(400), start="2026-09-22 08:00")
    full = ind.compute_all(df)
    cut = 250
    part = ind.compute_all(df.iloc[:cut])
    pd.testing.assert_frame_equal(full.iloc[:cut], part, check_exact=False, rtol=1e-9)
