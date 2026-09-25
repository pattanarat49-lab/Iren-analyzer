"""Score the latest trading day minute by minute with the models that were live that day.

Run it before retraining (the Daily backtest job does), so every forecast is out of sample.
Each regular-session minute is scored for every horizon with the same label rule as training,
and the result is added to a JSON history (newest first) that the Pages site shows.

Usage (from backend/):
    python -m scripts.review_day --out ../docs/day-review.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app import db
from app.config import get_settings
from app.market.clock import ET
from app.model.data import load_frames
from app.model.features import HORIZON_TH, HORIZONS, build_features, build_labels
from app.model.predictor import clean_json, model_dir

KEEP = 60  # reviews kept in the history file


def review(frames: dict[str, pd.DataFrame], primary: str, peers: list[str], models: Path) -> dict | None:
    px = frames[primary]
    if px.empty:
        return None
    feats = build_features(frames, primary, peers)
    et_dates = feats.index.tz_convert(ET).date
    regular = feats["is_regular"].to_numpy() == 1
    days = sorted(set(et_dates[regular]))
    if not days:
        return None
    day = days[-1]
    rows = feats[(et_dates == day) & regular]
    bar_dates = px.index.tz_convert(ET).date
    session = px[(bar_dates == day)].between_time("13:30", "19:59")  # regular session, UTC
    before = px[bar_dates < day]
    prev = float(before["close"].iloc[-1]) if not before.empty else None
    close = float(session["close"].iloc[-1]) if not session.empty else None
    out = {
        "day": day.isoformat(),
        "price": {
            "prev_close": prev,
            "open": float(session["open"].iloc[0]) if not session.empty else None,
            "high": float(session["high"].max()) if not session.empty else None,
            "low": float(session["low"].min()) if not session.empty else None,
            "close": close,
            "change_pct": (close / prev - 1) * 100 if prev and close else None,
        },
        "horizons": {},
    }
    day_open = datetime.combine(day, time(9, 30), tzinfo=ET)
    for h in HORIZONS:
        path = models / f"{h}.joblib"
        if not path.exists():
            continue
        bundle = joblib.load(path)
        trained = bundle.get("trained_at")
        if trained and datetime.fromisoformat(trained) > day_open:
            # Trained after the session opened (e.g. a manual re-run): it may have seen the day.
            out.setdefault("skipped", []).append(h)
            continue
        labels = build_labels(feats, px, h).loc[rows.index]
        known = labels["y"].notna().to_numpy()
        if not known.any():
            continue
        p = bundle["model"].predict_proba(rows)[known]
        y = labels["y"].to_numpy()[known]
        base = bundle["meta"].get("train_up_rate") or bundle["metrics"]["up_rate"]
        hit = (p > 0.5) == (y == 1)
        hours = rows.index[known].tz_convert(ET).hour
        by_hour = (
            pd.DataFrame({"hour": hours, "y": y, "p": p, "hit": hit})
            .groupby("hour")
            .agg(n=("y", "size"), up_rate=("y", "mean"), mean_p=("p", "mean"), hit_rate=("hit", "mean"))
            .reset_index()
            .to_dict("records")
        )
        out["horizons"][h] = {
            "label": HORIZON_TH[h],
            "model": bundle["model"].kind,
            "trained_at": bundle.get("trained_at"),
            "n": int(known.sum()),
            "up_rate": float(y.mean()),
            "hit_rate": float(hit.mean()),
            "baseline_hit_rate": float(((base > 0.5) == (y == 1)).mean()),
            "brier": float(np.mean((p - y) ** 2)),
            "baseline_brier": float(np.mean((base - y) ** 2)),
            "mean_p": float(p.mean()),
            "min_p": float(p.min()),
            "max_p": float(p.max()),
            "by_hour": by_hour,
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    s = get_settings()
    primary = s.primary_symbol.upper()
    peers = [x for x in s.all_symbols if x != primary]
    frames = load_frames(db.make_engine(s.effective_database_url), s.all_symbols, 0.25)
    result = review(frames, primary, peers, model_dir(s.models_dir, s.resolved_source))
    if result is None or not result["horizons"]:
        why = "the saved models were trained after that session opened" if result and result.get("skipped") else "no regular-session data or no saved models"
        print(f"Nothing to review ({why}); history left unchanged.")
        return 0
    history = []
    if args.out.exists():
        history = json.loads(args.out.read_text(encoding="utf-8")).get("reviews", [])
    history = [result] + [r for r in history if r.get("day") != result["day"]]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(clean_json({"reviews": history[:KEEP]}), ensure_ascii=False, indent=1), encoding="utf-8")
    for h, r in result["horizons"].items():
        print(f"{result['day']} {h:4s} n={r['n']:3d} hit {r['hit_rate']:.3f} vs {r['baseline_hit_rate']:.3f} | Brier {r['brier']:.4f} vs {r['baseline_brier']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
