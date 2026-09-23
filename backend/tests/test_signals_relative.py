import numpy as np
import pandas as pd
import pytest

from app.analysis import signals as sg
from app.analysis.relative import aligned_returns, compare, corr_last, relative_strength


def frame(**cols):
    n = max(len(v) for v in cols.values())
    return pd.DataFrame({k: (v if len(v) == n else [np.nan] * (n - len(v)) + list(v)) for k, v in cols.items()})


def test_ema_signal_directions():
    ind = frame(ema9=[10.0], ema21=[10.0], ema50=[10.0])
    assert sg.ema_signal(21, 10.5, ind).signal == "bullish"
    assert sg.ema_signal(21, 9.5, ind).signal == "bearish"
    assert sg.ema_signal(21, 10.001, ind).signal == "neutral"
    s = sg.ema_signal(21, 10.5, ind)
    assert "EMA 21" in s.explanation and s.name == "EMA 21"


def test_ema9_cross_and_stack_mentioned():
    ind = frame(ema9=[9.0, 9.5, 10.5], ema21=[10.0, 10.0, 10.0], ema50=[9.0, 9.0, 9.0])
    s9 = sg.ema_signal(9, 11, ind)
    assert s9.extra["cross_9_21"] == "up" and "ตัดขึ้น" in s9.explanation
    s50 = sg.ema_signal(50, 11, ind)
    assert s50.extra["stack"] == "bullish"


@pytest.mark.parametrize("r,expected", [(75, "bearish"), (25, "bullish"), (60, "bullish"), (40, "bearish"), (50, "neutral")])
def test_rsi_zones(r, expected):
    assert sg.rsi_signal(frame(rsi14=[float(r)])).signal == expected


def test_macd_cross_up_is_bullish():
    ind = frame(macd=[0.1, 0.2], signal=[0.15, 0.1], hist=[-0.05, 0.1])
    s = sg.macd_signal(40.0, ind)
    assert s.signal == "bullish" and s.extra["cross"] == "up"


def test_macd_weakening_is_neutral():
    ind = frame(macd=[0.3, 0.3], signal=[0.1, 0.2], hist=[0.2, 0.1])
    assert sg.macd_signal(40.0, ind).signal == "neutral"


@pytest.mark.parametrize("price,expected", [(12.5, "bearish"), (7.5, "bullish"), (11.5, "bullish"), (8.5, "bearish"), (10, "neutral")])
def test_bollinger_zones(price, expected):
    ind = frame(bb_upper=[12.0], bb_lower=[8.0], bb_mid=[10.0], bb_bandwidth=[0.4])
    assert sg.bollinger_signal(price, ind).signal == expected


def test_atr_is_never_directional():
    ind = frame(atr14=list(np.full(100, 0.2)))
    s = sg.atr_signal(40.0, ind)
    assert s.signal == "neutral" and "ไม่ได้บอกทิศทาง" in s.explanation


def test_rvol_needs_direction_and_flags_iex():
    ind = frame(rvol_cum=[2.0], rvol_bar=[1.8])
    assert sg.rvol_signal(ind, 0.03, False).signal == "bullish"
    assert sg.rvol_signal(ind, -0.03, False).signal == "bearish"
    assert "IEX" in sg.rvol_signal(ind, 0.03, True).explanation
    assert sg.rvol_signal(frame(rvol_cum=[np.nan], rvol_bar=[np.nan]), 0.01, False).value is None


def test_missing_values_are_neutral_not_errors():
    ind = frame(ema9=[np.nan], ema21=[np.nan], ema50=[np.nan], vwap=[np.nan], rsi14=[np.nan], macd=[np.nan],
                signal=[np.nan], hist=[np.nan], bb_upper=[np.nan], bb_lower=[np.nan], bb_mid=[np.nan],
                bb_bandwidth=[np.nan], atr14=[np.nan], rvol_cum=[np.nan], rvol_bar=[np.nan])
    sigs = sg.build_signals(40.0, ind, day_change=None, iex_only=False)
    assert len(sigs) == 9 and all(s.signal == "neutral" and s.value is None for s in sigs)
    summary = sg.summarize(sigs)
    assert summary["overall"] == "neutral" and "ไม่ใช่ความน่าจะเป็น" in summary["explanation"]


# ---- relative strength / correlation ----

def _series(values, start="2026-09-23 13:30", freq="1min"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq=freq, tz="UTC"), dtype=float)


def test_relative_strength_formula():
    assert relative_strength(0.10, 0.0) == pytest.approx(0.10)
    assert relative_strength(0.0, 0.10) == pytest.approx(1 / 1.1 - 1)
    assert relative_strength(None, 0.1) is None


def test_correlation_perfect_and_inverse():
    rng = np.random.default_rng(0)
    r = rng.normal(0, 0.002, 200)
    a = _series(40 * np.exp(np.cumsum(r)))
    b = _series(100 * np.exp(np.cumsum(2 * r)))
    c = _series(100 * np.exp(np.cumsum(-r)))
    assert corr_last(aligned_returns(a, b), 60) == pytest.approx(1.0)
    assert corr_last(aligned_returns(a, c), 60) == pytest.approx(-1.0)


def test_returns_across_overnight_gap_are_dropped():
    day1 = _series([10, 11, 12], start="2026-09-22 19:57")
    day2 = _series([20, 21], start="2026-09-23 13:30")
    a = pd.concat([day1, day2])
    rets = aligned_returns(a, a * 2)
    assert len(rets) == 3  # 2 on day 1, 1 on day 2; the overnight jump is excluded


def test_btc_24_7_aligns_to_stock_minutes():
    stock = _series(np.linspace(40, 41, 30))
    btc = _series(np.linspace(100000, 101000, 120), start="2026-09-23 13:00")
    rets = aligned_returns(stock, btc)
    assert len(rets) == 29


def test_compare_row():
    a = _series(np.linspace(40, 44, 100))
    b = _series(np.linspace(100, 101, 100))
    row = compare("IREN", a, "NVDA", b, today_ref={"IREN": 40.0, "NVDA": 100.0}, now=a.index[-1])
    assert row["signal"] == "bullish"
    assert row["rs_today"] == pytest.approx(1.1 / 1.01 - 1)
    assert "IREN" in row["explanation"] and "NVDA" in row["explanation"]
