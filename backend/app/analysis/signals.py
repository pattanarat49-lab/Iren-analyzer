"""Turn indicator values into bullish / bearish / neutral signals with a one-sentence Thai explanation.

These are descriptive readings of the chart, not predictions. The probability engine (Phase 4)
learns from the raw indicator values; it does not use these hand-written rules.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd

Signal = Literal["bullish", "bearish", "neutral"]

# Price within this fraction of a line counts as "at" the line (neutral).
NEAR = 0.0005  # 0.05 %


@dataclass
class IndicatorSignal:
    key: str
    name: str  # English indicator name (kept in English in the UI)
    value: float | None
    display: str
    signal: Signal
    explanation: str  # Thai, one sentence
    extra: dict | None = None

    def to_json(self) -> dict:
        return asdict(self)


def _ok(*xs: float | None) -> bool:
    return all(x is not None and not (isinstance(x, float) and math.isnan(x)) for x in xs)


def _f(x: float | None) -> float | None:
    if x is None:
        return None
    x = float(x)
    return None if math.isnan(x) else x


def _price(p: float) -> str:
    return f"{p:,.2f}" if p >= 1 else f"{p:.4f}"


def _missing(key: str, name: str, why: str = "ข้อมูลยังไม่พอสำหรับคำนวณ") -> IndicatorSignal:
    return IndicatorSignal(key, name, None, "–", "neutral", why)


def ema_signal(n: int, price: float, ind: pd.DataFrame) -> IndicatorSignal:
    key, name = f"ema{n}", f"EMA {n}"
    e = _f(ind[key].iloc[-1])
    if not _ok(price, e):
        return _missing(key, name)
    d = (price - e) / e
    if abs(d) < NEAR:
        sig: Signal = "neutral"
        text = f"ราคา {_price(price)} แทบเท่ากับ EMA {n} ({_price(e)}) จึงยังไม่มีทิศทางชัดเจนในกรอบนี้"
    elif d > 0:
        sig = "bullish"
        text = f"ราคาอยู่เหนือ EMA {n} ({_price(e)}) {d:+.2%} แสดงว่าฝั่งซื้อยังคุมทิศทางในกรอบนี้"
    else:
        sig = "bearish"
        text = f"ราคาอยู่ต่ำกว่า EMA {n} ({_price(e)}) {d:+.2%} แสดงว่าฝั่งขายยังได้เปรียบในกรอบนี้"

    extra: dict = {}
    if n == 9:
        cross = _recent_cross(ind["ema9"] - ind["ema21"], lookback=5)
        if cross == "up":
            text += " และ EMA 9 เพิ่งตัดขึ้นเหนือ EMA 21 (สัญญาณเริ่มต้นขาขึ้น)"
        elif cross == "down":
            text += " และ EMA 9 เพิ่งตัดลงต่ำกว่า EMA 21 (สัญญาณเริ่มต้นขาลง)"
        extra["cross_9_21"] = cross
    if n == 50:
        e9, e21 = _f(ind["ema9"].iloc[-1]), _f(ind["ema21"].iloc[-1])
        if _ok(e9, e21):
            if e9 > e21 > e:
                text += " โดยเส้น EMA เรียงตัวแบบขาขึ้น (9 > 21 > 50)"
                extra["stack"] = "bullish"
            elif e9 < e21 < e:
                text += " โดยเส้น EMA เรียงตัวแบบขาลง (9 < 21 < 50)"
                extra["stack"] = "bearish"
            else:
                extra["stack"] = "mixed"
    return IndicatorSignal(key, name, e, _price(e), sig, text, extra or None)


def vwap_signal(price: float, ind: pd.DataFrame) -> IndicatorSignal:
    v = _f(ind["vwap"].iloc[-1])
    if not _ok(price, v):
        return _missing("vwap", "VWAP")
    d = (price - v) / v
    if abs(d) < NEAR:
        sig: Signal = "neutral"
        text = f"ราคาอยู่ใกล้ VWAP ({_price(v)}) มาก ผู้ซื้อวันนี้โดยเฉลี่ยเท่าทุน ยังไม่มีฝั่งไหนได้เปรียบ"
    elif d > 0:
        sig = "bullish"
        text = f"ราคาอยู่เหนือ VWAP ({_price(v)}) {d:+.2%} ผู้ที่ซื้อวันนี้โดยเฉลี่ยกำลังได้กำไร ฝั่งซื้อจึงได้เปรียบ"
    else:
        sig = "bearish"
        text = f"ราคาอยู่ต่ำกว่า VWAP ({_price(v)}) {d:+.2%} ผู้ที่ซื้อวันนี้โดยเฉลี่ยกำลังขาดทุน ฝั่งขายจึงได้เปรียบ"
    return IndicatorSignal("vwap", "VWAP", v, _price(v), sig, text)


def rsi_signal(ind: pd.DataFrame) -> IndicatorSignal:
    r = _f(ind["rsi14"].iloc[-1])
    if not _ok(r):
        return _missing("rsi14", "RSI(14)")
    if r >= 70:
        sig: Signal = "bearish"
        text = f"RSI {r:.1f} สูงกว่า 70 คือถูกซื้อมากเกินไป (overbought) มีโอกาสย่อตัวในระยะสั้น"
    elif r <= 30:
        sig = "bullish"
        text = f"RSI {r:.1f} ต่ำกว่า 30 คือถูกขายมากเกินไป (oversold) มีโอกาสเด้งกลับในระยะสั้น"
    elif r >= 55:
        sig = "bullish"
        text = f"RSI {r:.1f} อยู่ช่วง 55–70 โมเมนตัมเป็นบวกแต่ยังไม่ร้อนแรงเกินไป"
    elif r <= 45:
        sig = "bearish"
        text = f"RSI {r:.1f} อยู่ช่วง 30–45 โมเมนตัมเป็นลบ แต่ยังไม่ถึงจุดขายมากเกินไป"
    else:
        sig = "neutral"
        text = f"RSI {r:.1f} อยู่ใกล้ 50 โมเมนตัมยังเป็นกลาง"
    return IndicatorSignal("rsi14", "RSI(14)", r, f"{r:.1f}", sig, text)


def macd_signal(price: float, ind: pd.DataFrame) -> IndicatorSignal:
    m, s, h = (_f(ind[c].iloc[-1]) for c in ("macd", "signal", "hist"))
    name = "MACD(12,26,9)"
    if not _ok(m, s, h):
        return _missing("macd", name)
    extra = {"macd": m, "signal": s, "hist": h}
    display = f"{m:+.3f} / {s:+.3f}"
    cross = _recent_cross(ind["hist"], lookback=3)
    hist = ind["hist"].dropna()
    rising = len(hist) >= 2 and hist.iloc[-1] > hist.iloc[-2]
    tiny = abs(h) < price * 0.00002
    if cross == "up":
        sig: Signal = "bullish"
        text = "MACD เพิ่งตัดขึ้นเหนือเส้น Signal เป็นสัญญาณว่าโมเมนตัมเริ่มเปลี่ยนเป็นบวก"
    elif cross == "down":
        sig = "bearish"
        text = "MACD เพิ่งตัดลงต่ำกว่าเส้น Signal เป็นสัญญาณว่าโมเมนตัมเริ่มเปลี่ยนเป็นลบ"
    elif tiny:
        sig = "neutral"
        text = "MACD แทบทับเส้น Signal โมเมนตัมยังไม่มีทิศทางชัดเจน"
    elif h > 0 and rising:
        sig = "bullish"
        text = "MACD อยู่เหนือเส้น Signal และ histogram กำลังขยายตัว โมเมนตัมขาขึ้นแข็งแรงขึ้น"
    elif h > 0:
        sig = "neutral"
        text = "MACD ยังอยู่เหนือเส้น Signal แต่ histogram หดตัว โมเมนตัมขาขึ้นเริ่มอ่อนแรง"
    elif not rising:
        sig = "bearish"
        text = "MACD อยู่ต่ำกว่าเส้น Signal และ histogram ติดลบมากขึ้น โมเมนตัมขาลงแข็งแรงขึ้น"
    else:
        sig = "neutral"
        text = "MACD ยังอยู่ต่ำกว่าเส้น Signal แต่ histogram เริ่มหดตัว แรงขายเริ่มอ่อนลง"
    extra["cross"] = cross
    return IndicatorSignal("macd", name, h, display, sig, text, extra)


def bollinger_signal(price: float, ind: pd.DataFrame) -> IndicatorSignal:
    up, lo, mid = (_f(ind[c].iloc[-1]) for c in ("bb_upper", "bb_lower", "bb_mid"))
    name = "Bollinger Bands(20,2)"
    if not _ok(price, up, lo, mid) or up == lo:
        return _missing("bb", name)
    pb = (price - lo) / (up - lo)
    extra = {"upper": up, "mid": mid, "lower": lo, "pct_b": pb}
    if pb > 1:
        sig: Signal = "bearish"
        text = f"ราคาทะลุเหนือแบนด์บน ({_price(up)}) ถือว่ายืดตัวมากเกินไป มักมีแรงดึงกลับเข้าหาเส้นกลาง"
    elif pb < 0:
        sig = "bullish"
        text = f"ราคาหลุดต่ำกว่าแบนด์ล่าง ({_price(lo)}) ถือว่าถูกขายมากเกินไป มักมีแรงเด้งกลับเข้าหาเส้นกลาง"
    elif pb >= 0.6:
        sig = "bullish"
        text = f"ราคาอยู่ครึ่งบนของแบนด์ (%B = {pb:.2f}) แนวโน้มระยะสั้นค่อนข้างแข็งแรง"
    elif pb <= 0.4:
        sig = "bearish"
        text = f"ราคาอยู่ครึ่งล่างของแบนด์ (%B = {pb:.2f}) แนวโน้มระยะสั้นค่อนข้างอ่อนแรง"
    else:
        sig = "neutral"
        text = f"ราคาอยู่ใกล้เส้นกลางของแบนด์ ({_price(mid)}) ยังไม่มีทิศทางชัดเจน"
    bw = ind["bb_bandwidth"].dropna().tail(200)
    if len(bw) >= 50 and bw.iloc[-1] <= bw.quantile(0.1):
        text += " ขณะนี้แบนด์บีบตัวแคบ (squeeze) ซึ่งมักเกิดก่อนราคาเคลื่อนไหวแรง"
        extra["squeeze"] = True
    return IndicatorSignal("bb", name, pb, f"%B {pb:.2f}", sig, text, extra)


def atr_signal(price: float, ind: pd.DataFrame, bar_minutes: int = 1) -> IndicatorSignal:
    a = _f(ind["atr14"].iloc[-1])
    if not _ok(price, a) or price <= 0:
        return _missing("atr14", "ATR(14)")
    pct = a / price
    hist = ind["atr14"].dropna().tail(390)
    ratio = a / hist.mean() if len(hist) >= 30 and hist.mean() > 0 else None
    if ratio is None:
        level = ""
    elif ratio >= 1.3:
        level = f" ความผันผวนสูงกว่าปกติ ({ratio:.1f} เท่าของค่าเฉลี่ย)"
    elif ratio <= 0.7:
        level = f" ความผันผวนต่ำกว่าปกติ ({ratio:.1f} เท่าของค่าเฉลี่ย)"
    else:
        level = " ความผันผวนใกล้เคียงปกติ"
    text = (
        f"ราคาแกว่งเฉลี่ยประมาณ ${a:.3f} ({pct:.2%}) ต่อแท่ง {bar_minutes} นาที{level}"
        " โดย ATR บอกขนาดการแกว่ง ไม่ได้บอกทิศทาง"
    )
    return IndicatorSignal("atr14", "ATR(14)", a, f"{a:.3f}", "neutral", text, {"pct": pct, "ratio": ratio})


def rvol_signal(ind: pd.DataFrame, day_change: float | None, iex_only: bool) -> IndicatorSignal:
    r = _f(ind["rvol_cum"].iloc[-1])
    name = "Relative Volume"
    note = " (นับเฉพาะปริมาณจากตลาด IEX)" if iex_only else ""
    if not _ok(r):
        return _missing("rvol", name, "ต้องมีข้อมูลย้อนหลังอย่างน้อย 5 วันทำการจึงจะเทียบปริมาณซื้อขายได้")
    bar = _f(ind["rvol_bar"].iloc[-1])
    extra = {"rvol_cum": r, "rvol_bar": bar}
    if r >= 1.5 and day_change is not None and day_change > 0:
        sig: Signal = "bullish"
        text = f"ปริมาณซื้อขายวันนี้สูงกว่าปกติ {r:.1f} เท่า ขณะที่ราคาขึ้น แสดงว่ามีแรงซื้อจริงสนับสนุน{note}"
    elif r >= 1.5 and day_change is not None and day_change < 0:
        sig = "bearish"
        text = f"ปริมาณซื้อขายวันนี้สูงกว่าปกติ {r:.1f} เท่า ขณะที่ราคาลง แสดงว่ามีแรงขายจริงกดดัน{note}"
    elif r >= 1.5:
        sig = "neutral"
        text = f"ปริมาณซื้อขายวันนี้สูงกว่าปกติ {r:.1f} เท่า แต่ราคายังไม่เลือกทาง{note}"
    elif r <= 0.7:
        sig = "neutral"
        text = f"ปริมาณซื้อขายต่ำกว่าปกติ ({r:.1f} เท่า) การเคลื่อนไหวตอนนี้จึงอาจยังไม่น่าเชื่อถือ{note}"
    else:
        sig = "neutral"
        text = f"ปริมาณซื้อขายใกล้เคียงปกติ ({r:.1f} เท่าของค่าเฉลี่ย ณ เวลาเดียวกัน){note}"
    return IndicatorSignal("rvol", name, r, f"{r:.2f}x", sig, text, extra)


def build_signals(
    price: float,
    ind: pd.DataFrame,
    *,
    day_change: float | None,
    iex_only: bool,
    bar_minutes: int = 1,
) -> list[IndicatorSignal]:
    return [
        ema_signal(9, price, ind),
        ema_signal(21, price, ind),
        ema_signal(50, price, ind),
        vwap_signal(price, ind),
        rsi_signal(ind),
        macd_signal(price, ind),
        bollinger_signal(price, ind),
        atr_signal(price, ind, bar_minutes),
        rvol_signal(ind, day_change, iex_only),
    ]


def summarize(signals: list[IndicatorSignal]) -> dict:
    counts = {"bullish": 0, "bearish": 0, "neutral": 0}
    for s in signals:
        counts[s.signal] += 1
    directional = counts["bullish"] + counts["bearish"]
    if counts["bullish"] > counts["bearish"]:
        overall: Signal = "bullish"
        text = f"สัญญาณทางเทคนิคส่วนใหญ่เป็นบวก ({counts['bullish']} จาก {directional} ตัวที่มีทิศทาง)"
    elif counts["bearish"] > counts["bullish"]:
        overall = "bearish"
        text = f"สัญญาณทางเทคนิคส่วนใหญ่เป็นลบ ({counts['bearish']} จาก {directional} ตัวที่มีทิศทาง)"
    else:
        overall = "neutral"
        text = "สัญญาณทางเทคนิคขัดแย้งกันหรือเป็นกลาง ยังไม่มีทิศทางชัดเจน"
    text += " ทั้งนี้เป็นการอ่านกราฟ ไม่ใช่ความน่าจะเป็น"
    return {"overall": overall, "counts": counts, "explanation": text}


def _recent_cross(diff: pd.Series, lookback: int) -> Literal["up", "down"] | None:
    """Did `diff` change sign within the last `lookback` bars? Returns the most recent direction."""
    d = diff.dropna().tail(lookback + 1)
    if len(d) < 2:
        return None
    sign = d.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)).to_numpy()
    for i in range(len(sign) - 1, 0, -1):
        if sign[i] != sign[i - 1] and sign[i] != 0:
            return "up" if sign[i] > 0 else "down"
    return None
