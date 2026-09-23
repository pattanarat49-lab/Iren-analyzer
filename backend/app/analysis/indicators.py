"""Technical indicators on pandas Series / DataFrames.

Conventions follow TradingView / TA-Lib so values match common charting tools:
- EMA is seeded with the simple average of the first `n` values (NaN before that).
- RSI and ATR use Wilder's smoothing (RMA), seeded with a simple average.
- Bollinger Bands use the population standard deviation (ddof=0).
- VWAP is anchored at each US/Eastern calendar day (pre-market included) and uses the
  typical price (H+L+C)/3.

Every function is causal: the value at bar t depends only on bars <= t (no look-ahead).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ET = "America/New_York"


def ema(s: pd.Series, n: int) -> pd.Series:
    """Exponential moving average, alpha = 2/(n+1), seeded with SMA(n) of the first valid values."""
    return _recursive_avg(s, n, alpha=2.0 / (n + 1))


def rma(s: pd.Series, n: int) -> pd.Series:
    """Wilder's moving average, alpha = 1/n, seeded with SMA(n)."""
    return _recursive_avg(s, n, alpha=1.0 / n)


def _recursive_avg(s: pd.Series, n: int, alpha: float) -> pd.Series:
    if n < 1:
        raise ValueError("n must be >= 1")
    x = s.to_numpy(dtype=float)
    out = np.full(len(x), np.nan)
    valid = np.flatnonzero(~np.isnan(x))
    if len(valid) < n:
        return pd.Series(out, index=s.index)
    start = valid[0]
    seed_end = start + n  # SMA over the first n values from the first valid one
    if np.isnan(x[start:seed_end]).any():
        # Interior gaps in the seed window: fall back to the first n valid values.
        seed_idx = valid[:n]
        seed_end = seed_idx[-1] + 1
        prev = x[seed_idx].mean()
    else:
        prev = x[start:seed_end].mean()
    out[seed_end - 1] = prev
    for i in range(seed_end, len(x)):
        v = x[i]
        if not np.isnan(v):
            prev = prev + alpha * (v - prev)
        out[i] = prev
    return pd.Series(out, index=s.index)


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    diff = close.diff()
    gain = diff.clip(lower=0)
    loss = (-diff).clip(lower=0)
    avg_gain = rma(gain, n)
    avg_loss = rma(loss, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss
        out = 100 - 100 / (1 + rs)
    # No losses at all -> 100; no gains and no losses (flat) -> 50.
    out = out.where(avg_loss != 0, 100.0)
    out = out.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)
    return out.where(avg_gain.notna())


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig}, index=close.index)


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    mid = sma(close, n)
    sd = close.rolling(n, min_periods=n).std(ddof=0)
    upper, lower = mid + k * sd, mid - k * sd
    width = upper - lower
    with np.errstate(divide="ignore", invalid="ignore"):
        pct_b = (close - lower) / width
        bandwidth = width / mid
    return pd.DataFrame(
        {"mid": mid, "upper": upper, "lower": lower, "pct_b": pct_b, "bandwidth": bandwidth},
        index=close.index,
    )


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    pc = close.shift(1)
    tr = pd.concat([high - low, (high - pc).abs(), (low - pc).abs()], axis=1).max(axis=1)
    tr.iloc[:1] = (high - low).iloc[:1]
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, n: int = 14) -> pd.Series:
    return rma(true_range(high, low, close), n)


def session_day(index: pd.DatetimeIndex) -> pd.Series:
    """US/Eastern calendar date for each (UTC) timestamp; used to anchor daily calculations."""
    return pd.Series(index.tz_convert(ET).date, index=index)


def vwap(df: pd.DataFrame) -> pd.Series:
    """Daily-anchored VWAP. `df` needs high, low, close, volume and a tz-aware DatetimeIndex."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    day = session_day(df.index)
    pv = (tp * df["volume"]).groupby(day).cumsum()
    vol = df["volume"].groupby(day).cumsum()
    with np.errstate(divide="ignore", invalid="ignore"):
        out = pv / vol
    # Before any volume prints on a day, fall back to the typical price.
    return out.where(vol > 0, tp)


def relative_volume(df: pd.DataFrame, lookback_days: int = 20, min_days: int = 5) -> pd.DataFrame:
    """Time-of-day relative volume.

    rvol_bar:  this bar's volume / average volume of the same minute-of-day over prior days
    rvol_cum:  cumulative volume so far today / average cumulative volume at the same time of day
    Only *prior* days are used for the averages, so there is no look-ahead.
    """
    et = df.index.tz_convert(ET)
    day = pd.Series(et.date, index=df.index)
    tod = pd.Series(et.hour * 60 + et.minute, index=df.index)
    vol = df["volume"].astype(float)
    cum = vol.groupby(day).cumsum()

    frame = pd.DataFrame({"day": day, "tod": tod, "vol": vol, "cum": cum})
    days = sorted(frame["day"].unique())
    vol_tbl = frame.pivot_table(index="day", columns="tod", values="vol", aggfunc="sum").reindex(days)
    # Cumulative volume table: forward-fill within a day so minutes without a bar still count.
    cum_tbl = frame.pivot_table(index="day", columns="tod", values="cum", aggfunc="last").reindex(days)
    cum_tbl = cum_tbl.sort_index(axis=1).ffill(axis=1)
    vol_tbl = vol_tbl.fillna(0.0)

    def prior_mean(tbl: pd.DataFrame) -> pd.DataFrame:
        m = tbl.shift(1).rolling(lookback_days, min_periods=min_days).mean()
        return m

    avg_vol = prior_mean(vol_tbl)
    avg_cum = prior_mean(cum_tbl)

    def lookup(tbl: pd.DataFrame) -> np.ndarray:
        stacked = tbl.stack(future_stack=True)
        keys = pd.MultiIndex.from_arrays([frame["day"], frame["tod"]])
        return stacked.reindex(keys).to_numpy(dtype=float)

    with np.errstate(divide="ignore", invalid="ignore"):
        rvol_bar = vol.to_numpy() / lookup(avg_vol)
        rvol_cum = cum.to_numpy() / lookup(avg_cum)
    rvol_bar[~np.isfinite(rvol_bar)] = np.nan
    rvol_cum[~np.isfinite(rvol_cum)] = np.nan
    return pd.DataFrame({"rvol_bar": rvol_bar, "rvol_cum": rvol_cum}, index=df.index)


def compute_all(df: pd.DataFrame) -> pd.DataFrame:
    """All dashboard indicators for an OHLCV frame (tz-aware UTC index, ascending)."""
    c = df["close"]
    out = pd.DataFrame(index=df.index)
    out["ema9"] = ema(c, 9)
    out["ema21"] = ema(c, 21)
    out["ema50"] = ema(c, 50)
    out["vwap"] = vwap(df)
    out["rsi14"] = rsi(c, 14)
    out = out.join(macd(c, 12, 26, 9))
    bb = bollinger(c, 20, 2.0).add_prefix("bb_")
    out = out.join(bb)
    out["atr14"] = atr(df["high"], df["low"], c, 14)
    out = out.join(relative_volume(df))
    return out
