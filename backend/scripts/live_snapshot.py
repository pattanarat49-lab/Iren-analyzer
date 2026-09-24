"""Write one live snapshot (quotes, indicators, P(up) per horizon) to a JSON file.

Used by the GitHub Pages workflow to refresh the static site every few minutes; it is the same
analysis and prediction code the live server runs, evaluated once on the newest bars.

Usage (from backend/):
    python -m scripts.live_snapshot --out ../_site/live.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from app import db
from app.analysis.engine import AnalysisEngine
from app.config import get_settings
from app.data.alpaca_rest import AlpacaAuthError, AlpacaRest, is_crypto
from app.data.hub import SymbolState, closes_from_snapshot, reference_trading_day
from app.market.clock import ET, dual_time, session_at
from app.model.predictor import Predictor, clean_json, model_dir
from app.model.tracking import target_time
from app.models import parse_ts
from scripts.backfill import backfill_symbol

UTC = timezone.utc
HISTORY_DAYS = 30  # same window the live server keeps in memory
# Bars arrive late on the free IEX feed and the job runs every few minutes; older than this is stale.
MAX_BAR_AGE = timedelta(minutes=20)
ONE_MIN = pd.Timedelta(minutes=1)


async def refresh_bars(rest: AlpacaRest, engine, symbols: list[str], feed: str) -> None:  # noqa: ANN001
    end = datetime.now(UTC)
    start = end - timedelta(days=HISTORY_DAYS)
    for sym in symbols:
        await backfill_symbol(rest, engine, sym, start, end, "crypto" if is_crypto(sym) else feed)


async def quote_state(rest: AlpacaRest, symbols: list[str], primary: str) -> dict[str, SymbolState]:
    """Latest trade and previous close per symbol, as the live server's snapshot loop sets them."""
    state = {s: SymbolState(s) for s in symbols}
    snaps = await rest.snapshots(symbols)
    now = datetime.now(UTC)
    ref_day = reference_trading_day(now)
    session = session_at(now).session
    for sym, snap in snaps.items():
        st = state.get(sym)
        if st is None:
            continue
        if is_crypto(sym):
            prev = (snap.get("prevDailyBar") or {}).get("c")
            st.prev_close = float(prev) if prev else None
        else:
            st.prev_close, same = closes_from_snapshot(snap, ref_day)
            st.session_close = same if session in ("after", "closed") else None
        lt = snap.get("latestTrade")
        if lt and lt.get("p"):
            st.price, st.price_ts = float(lt["p"]), parse_ts(lt["t"])
        lq = snap.get("latestQuote")
        if lq and sym == primary:
            st.bid, st.ask = (lq.get("bp") or None), (lq.get("ap") or None)
    return state


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    s = get_settings()
    now = datetime.now(UTC)
    out: dict = {"generated_at": dual_time(now), "session": session_at(now).to_dict(), "ok": False}
    if not s.has_alpaca_keys:
        out["error"] = "ยังไม่ได้ตั้งค่าคีย์ Alpaca"
        return _write(args.out, out, 2)

    primary = s.primary_symbol.upper()
    peers = [x for x in s.all_symbols if x != primary]
    engine = db.make_engine(s.database_url)
    rest = AlpacaRest(s)
    try:
        await refresh_bars(rest, engine, s.all_symbols, s.alpaca_stock_feed)
        state = await quote_state(rest, s.all_symbols, primary)
    except AlpacaAuthError as e:
        out["error"] = f"Alpaca ไม่รับคีย์: {e}"
        return _write(args.out, out, 1)
    finally:
        await rest.aclose()

    analysis = AnalysisEngine(SimpleNamespace(s=s, engine=engine, state=state), history_days=HISTORY_DAYS)
    analysis.frames = analysis.load_frames()
    predictor = Predictor(model_dir(s.models_dir, s.resolved_source), primary, peers)
    predictor.load()
    frames = analysis.snapshot()
    spark = day_chart(frames[primary])

    out.update({
        "ok": True,
        "primary": primary,
        "stock_feed": s.alpaca_stock_feed,
        "quotes": {sym: st.to_json() for sym, st in state.items()},
        "analysis": analysis.compute(1, frames),
        "prediction": add_last_valid(
            mark_validity(clean_json(predictor.predict(frames, state[primary].price)), datetime.now(UTC)),
            frames, predictor, primary,
        ),
        "spark": spark,
    })
    return _write(args.out, out, 0)


def day_chart(df: pd.DataFrame) -> dict | None:
    """1-minute closes of the latest trading day in the data, plus the close before it."""
    if df.empty:
        return None
    et_dates = df.index.tz_convert(ET).date
    day = et_dates[-1]
    today = df["close"][et_dates == day]
    before = df["close"][et_dates < day]
    return {
        "date": day.isoformat(),
        "ref_close": float(before.iloc[-1]) if not before.empty else None,
        "points": [[int(t.timestamp()), float(c)] for t, c in today.items()],
    }


def mark_validity(pred: dict, now: datetime) -> dict:
    """Flag each horizon whose forecast is meaningful right now.

    The models are trained only on decision times whose horizon ends inside the same extended
    session (the same rule as the live track record), so a forecast made on a stale bar, or one
    that would end after 20:00 ET, is outside what the model has learned and is marked invalid.
    """
    made_at = pred.get("made_at")
    if not pred.get("available") or not made_at:
        return pred
    made = datetime.fromisoformat(made_at)
    age = now - made
    pred["bar_age_min"] = age.total_seconds() / 60
    for h, p in (pred.get("horizons") or {}).items():
        if not p.get("available"):
            continue
        tgt = target_time(made, h)
        if age > MAX_BAR_AGE:
            p["valid"], p["invalid_reason"] = False, "ข้อมูลราคาล่าสุดเก่าเกินไป (ตลาดปิดหรือไม่มีการซื้อขาย)"
        elif tgt is None:
            p["valid"], p["invalid_reason"] = False, "ช่วงเวลานี้จะสิ้นสุดหลังตลาดปิด (20:00 ET) ซึ่งโมเดลไม่ได้เรียนรู้"
        else:
            p["valid"], p["target_at"] = True, dual_time(tgt)
    return pred


def last_valid_decision(bar_starts: pd.DatetimeIndex, horizon: str, lookback: int = 2000) -> datetime | None:
    """Latest decision time (bar start + 1 min) whose forecast the model is trained for."""
    for start in reversed(bar_starts[-lookback:]):
        made = (start + ONE_MIN).to_pydatetime()
        if target_time(made, horizon) is not None:
            return made
    return None


def add_last_valid(pred: dict, frames: dict[str, pd.DataFrame], predictor: Predictor, primary: str) -> dict:
    """For horizons that cannot be forecast right now (market closed, stale bar), score the most
    recent bar where they could be, so the page can show that figure with its reference time."""
    todo = [h for h, p in (pred.get("horizons") or {}).items() if p.get("available") and not p.get("valid")]
    if not todo or frames[primary].empty:
        return pred
    by_time: dict[datetime, list[str]] = {}
    for h in todo:
        made = last_valid_decision(frames[primary].index, h)
        if made is not None:
            by_time.setdefault(made, []).append(h)
    for made, hs in by_time.items():
        cut = {sym: f[f.index < made] for sym, f in frames.items()}
        past = clean_json(predictor.predict(cut))
        for h in hs:
            p = (past.get("horizons") or {}).get(h) or {}
            if not p.get("available"):
                continue
            pred["horizons"][h]["last_valid"] = {
                "made_at": dual_time(made),
                "price": past.get("price"),
                "p_up": p["p_up"],
                "p_down": p["p_down"],
                "expected_move": p.get("expected_move"),
                "target_at": dual_time(target_time(made, h)),
            }
    return pred


def _write(path: Path, data: dict, code: int) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_json(data), ensure_ascii=False), encoding="utf-8")
    print(f"wrote {path} (ok={data.get('ok')})")
    if data.get("error"):
        print(data["error"], file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
