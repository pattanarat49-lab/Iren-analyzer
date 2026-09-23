"""Feature matrix and labels for the probability models.

One row per completed 1-minute bar of the primary symbol. The **decision time** of a row is the
bar's end (open time + 1 min): that is when its close is known and a prediction can be made.

Every feature uses only information available at the decision time (no look-ahead). The same
`build_features` function is used for training and for live inference, so the model always sees
identically computed inputs. Prices "at" a time are the last trade price at that time (the close of
the most recent bar that ended at or before it), for both features and labels.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..analysis import indicators as ind
from ..market.clock import ET, schedule_between

ONE_MIN = pd.Timedelta(minutes=1)

HORIZONS: dict[str, int | None] = {"5m": 5, "15m": 15, "1h": 60, "eod": None}
HORIZON_TH = {"5m": "5 นาที", "15m": "15 นาที", "1h": "1 ชั่วโมง", "eod": "จบวัน (ราคาปิด)"}

RET_LOOKBACKS = (1, 5, 15, 30, 60)
PEER_LOOKBACKS = (5, 15, 60)
# A peer price older than this at decision time is treated as missing (e.g. a thin pre-market).
PEER_STALE = pd.Timedelta(minutes=30)


@dataclass
class PriceIndex:
    """Fast 'last price at time t' lookups for one symbol."""

    end_ns: np.ndarray  # bar end times (int64 ns, ascending)
    close: np.ndarray

    @classmethod
    def from_frame(cls, df: pd.DataFrame) -> PriceIndex:
        ends = (df.index + ONE_MIN).as_unit("ns").asi8
        return cls(ends, df["close"].to_numpy(dtype=float))

    def at(self, t_ns: np.ndarray, max_age: pd.Timedelta | None = None) -> tuple[np.ndarray, np.ndarray]:
        """(price, end time of the bar used) for each query time; NaN where no bar yet / too old."""
        idx = np.searchsorted(self.end_ns, t_ns, side="right") - 1
        ok = idx >= 0
        price = np.full(len(t_ns), np.nan)
        used = np.full(len(t_ns), np.iinfo(np.int64).min, dtype=np.int64)
        price[ok] = self.close[idx[ok]]
        used[ok] = self.end_ns[idx[ok]]
        if max_age is not None:
            stale = ok & (t_ns - used > max_age.value)
            price[stale] = np.nan
        return price, used


@dataclass
class Calendar:
    """Vectorised session boundaries (UTC ns) for a date range."""

    days: np.ndarray  # datetime64[D] ET dates of trading days
    open_ns: np.ndarray
    close_ns: np.ndarray
    after_ns: np.ndarray  # end of after-hours (20:00 ET, 17:00 on half days)

    @classmethod
    def build(cls, start: pd.Timestamp, end: pd.Timestamp) -> Calendar:
        tds = schedule_between(
            (start - pd.Timedelta(days=10)).tz_convert(ET).date(), (end + pd.Timedelta(days=10)).tz_convert(ET).date()
        )
        return cls(
            days=np.array([np.datetime64(td.day) for td in tds]),
            open_ns=np.array([pd.Timestamp(td.open).value for td in tds], dtype=np.int64),
            close_ns=np.array([pd.Timestamp(td.close).value for td in tds], dtype=np.int64),
            after_ns=np.array([pd.Timestamp(td.after_close).value for td in tds], dtype=np.int64),
        )

    def lookup_day(self, et_dates: np.ndarray) -> np.ndarray:
        """Index of each ET date in the trading-day list, or -1 if it is not a trading day."""
        idx = np.searchsorted(self.days, et_dates)
        idx = np.clip(idx, 0, len(self.days) - 1)
        return np.where(self.days[idx] == et_dates, idx, -1)

    def next_close_after(self, t_ns: np.ndarray) -> np.ndarray:
        """Next regular close strictly after t (the 'end of day' target)."""
        idx = np.searchsorted(self.close_ns, t_ns, side="right")
        idx = np.clip(idx, 0, len(self.close_ns) - 1)
        return self.close_ns[idx]

    def prev_close_before(self, t_ns: np.ndarray) -> np.ndarray:
        idx = np.searchsorted(self.close_ns, t_ns, side="left") - 1
        return np.where(idx >= 0, self.close_ns[np.clip(idx, 0, None)], np.iinfo(np.int64).min)


def _et_dates(index: pd.DatetimeIndex) -> np.ndarray:
    return index.tz_convert(ET).tz_localize(None).normalize().values.astype("datetime64[D]")


def build_features(frames: dict[str, pd.DataFrame], primary: str, peers: list[str]) -> pd.DataFrame:
    """Feature matrix indexed by decision time (UTC). `frames` are 1-min OHLCV frames (UTC index)."""
    df = frames[primary]
    if df.empty:
        return pd.DataFrame()
    df = df.sort_index()
    t = df.index + ONE_MIN  # decision times
    t_ns = t.as_unit("ns").asi8
    close = df["close"].to_numpy(dtype=float)
    cal = Calendar.build(df.index[0], df.index[-1])
    px = PriceIndex.from_frame(df)
    X: dict[str, np.ndarray] = {}

    # --- returns of the primary over clock-time lookbacks ---
    for k in RET_LOOKBACKS:
        past, _ = px.at(t_ns - pd.Timedelta(minutes=k).value)
        X[f"ret_{k}"] = np.log(close / past)

    # --- indicators (normalised so they are comparable across price levels) ---
    iv = ind.compute_all(df)
    X["dist_ema9"] = close / iv["ema9"].to_numpy() - 1
    X["dist_ema21"] = close / iv["ema21"].to_numpy() - 1
    X["dist_ema50"] = close / iv["ema50"].to_numpy() - 1
    X["ema9_21"] = iv["ema9"].to_numpy() / iv["ema21"].to_numpy() - 1
    X["dist_vwap"] = close / iv["vwap"].to_numpy() - 1
    X["rsi14"] = iv["rsi14"].to_numpy() / 100 - 0.5
    X["macd"] = iv["macd"].to_numpy() / close
    X["macd_signal"] = iv["signal"].to_numpy() / close
    X["macd_hist"] = iv["hist"].to_numpy() / close
    X["bb_pctb"] = iv["bb_pct_b"].to_numpy()
    X["bb_bandwidth"] = iv["bb_bandwidth"].to_numpy()
    atr = iv["atr14"].to_numpy()
    X["atr_pct"] = atr / close
    X["rvol_cum"] = np.log1p(iv["rvol_cum"].to_numpy())
    X["rvol_bar"] = np.log1p(iv["rvol_bar"].to_numpy())

    # --- volatility regime ---
    r1 = pd.Series(np.log(close), index=df.index).diff()
    vol30 = r1.rolling(30, min_periods=20).std().to_numpy()
    vol120 = r1.rolling(120, min_periods=60).std().to_numpy()
    X["vol_30"] = vol30
    X["vol_120"] = vol120
    with np.errstate(divide="ignore", invalid="ignore"):
        X["vol_ratio"] = vol30 / vol120
        X["atr_ratio"] = atr / pd.Series(atr).rolling(390, min_periods=60).mean().to_numpy()

    # --- day context: change vs previous regular close, position in today's range ---
    et_day = _et_dates(df.index)
    day_start_ns = (pd.DatetimeIndex(et_day).tz_localize(ET) + pd.Timedelta(hours=4)).as_unit("ns").asi8
    prev_close_t = cal.prev_close_before(day_start_ns)
    prev_close, _ = px.at(prev_close_t)
    X["ret_day"] = np.log(close / prev_close)
    hi = df["high"].groupby(et_day).cummax().to_numpy()
    lo = df["low"].groupby(et_day).cummin().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        X["day_range_pos"] = np.where(hi > lo, (close - lo) / (hi - lo), 0.5)

    # --- time of day / session ---
    et_idx = df.index.tz_convert(ET)
    tod = (et_idx.hour * 60 + et_idx.minute).to_numpy(dtype=float)
    X["tod_sin"] = np.sin(2 * np.pi * tod / 1440)
    X["tod_cos"] = np.cos(2 * np.pi * tod / 1440)
    X["dow"] = et_idx.dayofweek.to_numpy(dtype=float)
    di = cal.lookup_day(et_day)
    bar_ns = df.index.as_unit("ns").asi8
    open_ns = np.where(di >= 0, cal.open_ns[np.clip(di, 0, None)], 0)
    close_ns_day = np.where(di >= 0, cal.close_ns[np.clip(di, 0, None)], 0)
    X["is_pre"] = ((di >= 0) & (bar_ns < open_ns)).astype(float)
    X["is_regular"] = ((di >= 0) & (bar_ns >= open_ns) & (bar_ns < close_ns_day)).astype(float)
    X["is_after"] = ((di >= 0) & (bar_ns >= close_ns_day)).astype(float)
    X["mins_to_eod"] = (cal.next_close_after(t_ns) - t_ns) / 60e9

    # --- peers / context tickers ---
    ret15 = X["ret_15"]
    for sym in peers:
        pdf = frames.get(sym)
        tag = sym.replace("/", "").lower()
        if pdf is None or pdf.empty:
            for k in PEER_LOOKBACKS:
                X[f"{tag}_ret_{k}"] = np.full(len(df), np.nan)
            X[f"{tag}_rel_15"] = np.full(len(df), np.nan)
            continue
        ppx = PriceIndex.from_frame(pdf.sort_index())
        now_p, _ = ppx.at(t_ns, max_age=PEER_STALE)
        for k in PEER_LOOKBACKS:
            past_p, _ = ppx.at(t_ns - pd.Timedelta(minutes=k).value, max_age=PEER_STALE + pd.Timedelta(minutes=k))
            X[f"{tag}_ret_{k}"] = np.log(now_p / past_p)
        X[f"{tag}_rel_15"] = ret15 - X[f"{tag}_ret_15"]

    out = pd.DataFrame(X, index=t)
    out.index.name = "t"
    out["price"] = close  # not a feature: used for labels and expected-move ranges
    out["atr"] = atr  # not a feature
    return out.replace([np.inf, -np.inf], np.nan)


NON_FEATURES = ("price", "atr")


def feature_columns(feats: pd.DataFrame) -> list[str]:
    return [c for c in feats.columns if c not in NON_FEATURES]


def build_labels(feats: pd.DataFrame, primary_frame: pd.DataFrame, horizon: str) -> pd.DataFrame:
    """Label each decision time: 1 if the last price at t + horizon is strictly above the price at t.

    Rows whose horizon ends outside the same trading session (after 20:00 ET for intraday horizons)
    or whose future is not yet known get NaN and are dropped from training.
    Returns columns: y (0/1/NaN), fwd_ret (log return to horizon), target_t (UTC).
    """
    t_ns = feats.index.as_unit("ns").asi8
    px = PriceIndex.from_frame(primary_frame.sort_index())
    cal = Calendar.build(primary_frame.index[0], primary_frame.index[-1])
    last_end = px.end_ns[-1] if len(px.end_ns) else np.iinfo(np.int64).min

    minutes = HORIZONS[horizon]
    if minutes is None:
        target = cal.next_close_after(t_ns)
        valid = np.ones(len(t_ns), dtype=bool)
    else:
        target = t_ns + pd.Timedelta(minutes=minutes).value
        di = cal.lookup_day(_et_dates(feats.index - ONE_MIN))
        after_end = np.where(di >= 0, cal.after_ns[np.clip(di, 0, None)], 0)
        valid = (di >= 0) & (target <= after_end)

    fut, used = px.at(target)
    # The future price must come from the target's own trading day (not yesterday's last print).
    has_bar = used != np.iinfo(np.int64).min
    used_safe = np.where(has_bar, used, target)
    same_day = has_bar & (
        _et_dates(pd.DatetimeIndex(used_safe, tz="UTC")) == _et_dates(pd.DatetimeIndex(target, tz="UTC"))
    )
    known = target <= last_end  # we have data at least up to the target
    valid &= same_day & known & ~np.isnan(fut)

    price = feats["price"].to_numpy()
    fwd = np.log(fut / price)
    y = np.where(valid, (fut > price).astype(float), np.nan)
    return pd.DataFrame(
        {"y": y, "fwd_ret": np.where(valid, fwd, np.nan), "target_t": pd.DatetimeIndex(target, tz="UTC")},
        index=feats.index,
    )


def expected_move(price: float, atr_1m: float, horizon: str, mins_to_eod: float | None) -> dict | None:
    """ATR-based expected move: ±ATR(1-min) × sqrt(minutes), a random-walk scaling of typical range."""
    if not (np.isfinite(price) and np.isfinite(atr_1m)) or price <= 0 or atr_1m <= 0:
        return None
    minutes = HORIZONS[horizon]
    if minutes is None:
        if mins_to_eod is None or not np.isfinite(mins_to_eod):
            return None
        # Only regular-session minutes carry most of the variance; cap overnight at one session.
        minutes = float(min(max(mins_to_eod, 1.0), 390.0))
    move = atr_1m * float(np.sqrt(minutes))
    return {
        "minutes": minutes,
        "move": move,
        "move_pct": move / price * 100,
        "low": price - move,
        "high": price + move,
    }
