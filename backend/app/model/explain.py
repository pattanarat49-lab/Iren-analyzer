"""Human-readable (Thai) names for model features and the top up/down factors of a prediction."""

from __future__ import annotations

import math

from .features import PEER_LOOKBACKS, RET_LOOKBACKS

# Features that describe one concept are summed into a single factor.
GROUPS = {"tod_sin": "tod", "tod_cos": "tod", "is_pre": "session", "is_regular": "session", "is_after": "session"}


def _pct(v: float, digits: int = 2) -> str:
    return f"{v * 100:+.{digits}f}%"


def describe(name: str, row: dict[str, float], primary: str, peers: list[str]) -> tuple[str, str]:
    """(Thai label, formatted current value) for a feature or feature group."""
    v = row.get(name, float("nan"))
    ok = v is not None and not (isinstance(v, float) and math.isnan(v))

    def val(fmt) -> str:  # noqa: ANN001
        return fmt(v) if ok else "ไม่มีข้อมูล"

    for k in RET_LOOKBACKS:
        if name == f"ret_{k}":
            return f"ผลตอบแทน {primary} {k} นาทีล่าสุด", val(_pct)
    simple = {
        "dist_ema9": ("ระยะห่างราคาจาก EMA 9", _pct),
        "dist_ema21": ("ระยะห่างราคาจาก EMA 21", _pct),
        "dist_ema50": ("ระยะห่างราคาจาก EMA 50", _pct),
        "ema9_21": ("EMA 9 เทียบ EMA 21", _pct),
        "dist_vwap": ("ระยะห่างราคาจาก VWAP", _pct),
        "rsi14": ("RSI(14)", lambda x: f"{(x + 0.5) * 100:.1f}"),
        "macd": ("MACD (เทียบราคา)", lambda x: _pct(x, 3)),
        "macd_signal": ("MACD Signal (เทียบราคา)", lambda x: _pct(x, 3)),
        "macd_hist": ("MACD Histogram (เทียบราคา)", lambda x: _pct(x, 3)),
        "bb_pctb": ("ตำแหน่งใน Bollinger Bands (%B)", lambda x: f"{x:.2f}"),
        "bb_bandwidth": ("ความกว้าง Bollinger Bands", lambda x: f"{x * 100:.2f}%"),
        "atr_pct": ("ATR(14) เทียบราคา", lambda x: f"{x * 100:.2f}%"),
        "rvol_cum": ("Relative Volume สะสมวันนี้", lambda x: f"{math.expm1(x):.2f}x"),
        "rvol_bar": ("Relative Volume แท่งล่าสุด", lambda x: f"{math.expm1(x):.2f}x"),
        "vol_30": ("ความผันผวน 30 นาที", lambda x: f"{x * 100:.3f}%/นาที"),
        "vol_120": ("ความผันผวน 120 นาที", lambda x: f"{x * 100:.3f}%/นาที"),
        "vol_ratio": ("ความผันผวนระยะสั้นเทียบระยะยาว", lambda x: f"{x:.2f}x"),
        "atr_ratio": ("ATR เทียบค่าเฉลี่ยที่ผ่านมา", lambda x: f"{x:.2f}x"),
        "ret_day": ("เปลี่ยนแปลงจากราคาปิดก่อนหน้า", _pct),
        "day_range_pos": ("ตำแหน่งในกรอบราคาสูง-ต่ำของวันนี้", lambda x: f"{x * 100:.0f}%"),
        "dow": ("วันในสัปดาห์", lambda x: ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][int(x)]),
        "mins_to_eod": ("เวลาที่เหลือถึงตลาดปิด", lambda x: f"{x:.0f} นาที"),
    }
    if name in simple:
        label, fmt = simple[name]
        return label, val(fmt)
    if name == "tod":
        return "ช่วงเวลาของวัน", ""
    if name == "session":
        s = "ก่อนตลาดเปิด" if row.get("is_pre") else "ตลาดเปิด" if row.get("is_regular") else "หลังตลาดปิด" if row.get("is_after") else "ตลาดปิด"
        return "ช่วงตลาด", s
    for sym in peers:
        tag = sym.replace("/", "").lower()
        for k in PEER_LOOKBACKS:
            if name == f"{tag}_ret_{k}":
                return f"ผลตอบแทน {sym} {k} นาทีล่าสุด", val(_pct)
        if name == f"{tag}_rel_15":
            return f"{primary} แข็ง/อ่อนกว่า {sym} ใน 15 นาที", val(_pct)
    return name, val(lambda x: f"{x:.4g}")


def top_factors(contrib: dict[str, float], row: dict[str, float], primary: str, peers: list[str], n: int = 5) -> dict:
    grouped: dict[str, float] = {}
    for f, c in contrib.items():
        g = GROUPS.get(f, f)
        grouped[g] = grouped.get(g, 0.0) + c
    total = sum(abs(c) for c in grouped.values()) or 1.0
    items = []
    for g, c in grouped.items():
        label, value = describe(g, row, primary, peers)
        items.append({"feature": g, "label": label, "value": value, "impact": c, "share": abs(c) / total})
    up = sorted((i for i in items if i["impact"] > 0), key=lambda i: -i["impact"])[:n]
    down = sorted((i for i in items if i["impact"] < 0), key=lambda i: i["impact"])[:n]
    return {"up": up, "down": down}
