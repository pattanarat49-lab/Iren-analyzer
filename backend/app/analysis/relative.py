"""Rolling correlation, beta and relative strength of the primary symbol vs context tickers."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

# Returns spanning a gap longer than this (overnight, halts) are excluded from correlations.
MAX_GAP = pd.Timedelta(minutes=5)
RS_NEUTRAL = 0.005  # +/-0.5 % relative performance counts as "in line"


def aligned_returns(primary: pd.Series, peer: pd.Series) -> pd.DataFrame:
    """1-bar log returns of both series on the primary's timestamps, excluding gap-spanning returns.

    The peer is forward-filled onto the primary's timestamps (at most 5 minutes), which handles
    24/7 BTC vs. a stock and occasional missing minutes on thinly traded peers.
    """
    if primary.empty or peer.empty:
        return pd.DataFrame(columns=["a", "b"], dtype=float)
    peer_on_primary = peer.reindex(primary.index.union(peer.index)).ffill(limit=5).reindex(primary.index)
    df = pd.DataFrame({"a": primary, "b": peer_on_primary}).dropna()
    gap = df.index.to_series().diff()
    rets = np.log(df).diff()
    rets = rets[gap <= MAX_GAP]
    return rets.dropna()


def corr_last(rets: pd.DataFrame, n: int) -> float | None:
    tail = rets.tail(n)
    if len(tail) < max(20, n // 3) or tail["a"].std() == 0 or tail["b"].std() == 0:
        return None
    c = float(tail["a"].corr(tail["b"]))
    return None if math.isnan(c) else c


def beta_last(rets: pd.DataFrame, n: int) -> float | None:
    tail = rets.tail(n)
    if len(tail) < max(20, n // 3):
        return None
    var = tail["b"].var()
    if not var:
        return None
    return float(tail["a"].cov(tail["b"]) / var)


def pct_change_since(s: pd.Series, since: pd.Timestamp) -> float | None:
    before = s[s.index < since]
    if before.empty or s.empty:
        return None
    ref = before.iloc[-1]
    return float(s.iloc[-1] / ref - 1) if ref else None


def relative_strength(r_primary: float | None, r_peer: float | None) -> float | None:
    if r_primary is None or r_peer is None or r_peer <= -1:
        return None
    return (1 + r_primary) / (1 + r_peer) - 1


def _corr_word(c: float | None) -> str:
    if c is None:
        return "ยังคำนวณไม่ได้"
    a = abs(c)
    level = "สูง" if a >= 0.7 else ("ปานกลาง" if a >= 0.4 else "ต่ำ")
    way = "ไปทางเดียวกัน" if c > 0 else "สวนทางกัน"
    return f"{c:+.2f} ({level}, มักเคลื่อนไหว{way})" if a >= 0.4 else f"{c:+.2f} ({level})"


def compare(
    primary_sym: str,
    primary: pd.Series,
    peer_sym: str,
    peer: pd.Series,
    *,
    today_ref: dict[str, float | None],
    now: pd.Timestamp,
) -> dict:
    """One context-ticker row: correlations, beta, today's / 1-hour performance and relative strength."""
    rets = aligned_returns(primary, peer)
    c60, c390 = corr_last(rets, 60), corr_last(rets, 390)
    beta = beta_last(rets, 390)

    def today(sym: str, s: pd.Series) -> float | None:
        ref = today_ref.get(sym)
        if ref and not s.empty:
            return float(s.iloc[-1] / ref - 1)
        return None

    rp_today, rq_today = today(primary_sym, primary), today(peer_sym, peer)
    since = now - pd.Timedelta(minutes=60)
    rp_1h, rq_1h = pct_change_since(primary, since), pct_change_since(peer, since)
    rs_today = relative_strength(rp_today, rq_today)
    rs_1h = relative_strength(rp_1h, rq_1h)

    rs = rs_today if rs_today is not None else rs_1h
    label = "วันนี้" if rs_today is not None else "ใน 1 ชั่วโมง"
    if rs is None:
        signal, text = "neutral", f"ข้อมูล {peer_sym} ยังไม่พอสำหรับเปรียบเทียบ"
    else:
        rp = rp_today if rs_today is not None else rp_1h
        rq = rq_today if rs_today is not None else rq_1h
        if rs > RS_NEUTRAL:
            signal, verdict = "bullish", f"{primary_sym} แข็งแกร่งกว่า {rs:+.2%}"
        elif rs < -RS_NEUTRAL:
            signal, verdict = "bearish", f"{primary_sym} อ่อนแอกว่า {rs:+.2%}"
        else:
            signal, verdict = "neutral", f"{primary_sym} เคลื่อนไหวใกล้เคียงกัน ({rs:+.2%})"
        text = (
            f"{label} {primary_sym} {rp:+.2%} เทียบกับ {peer_sym} {rq:+.2%} → {verdict};"
            f" correlation 1 ชม. = {_corr_word(c60)}"
        )
    return {
        "symbol": peer_sym,
        "price": float(peer.iloc[-1]) if not peer.empty else None,
        "change_today": rq_today,
        "change_1h": rq_1h,
        "corr_60": c60,
        "corr_390": c390,
        "beta_390": beta,
        "rs_today": rs_today,
        "rs_1h": rs_1h,
        "signal": signal,
        "explanation": text,
    }
