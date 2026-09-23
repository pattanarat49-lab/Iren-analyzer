"""Live track record: log every prediction, fill in what actually happened, and score it.

Outcomes use exactly the same definition as the training labels: "up" = the last trade price at
the target time is strictly higher than the price at the decision time, where the target-time
price must come from the target's own trading day.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy.engine import Engine

from .. import db
from ..market.clock import ET, dual_time, end_of_day_target, trading_day
from .features import HORIZON_TH, HORIZONS
from .train import MIN_TEST_DAYS_FOR_EDGE, bootstrap_brier_diff, reliability

log = logging.getLogger(__name__)
UTC = timezone.utc

# Only log a prediction if its bar is this fresh (avoids logging stale bars after a restart).
MAX_BAR_AGE = timedelta(minutes=3)
# Give late / corrected bars a moment to arrive before scoring.
RESOLVE_GRACE = timedelta(minutes=2)
# A prediction whose outcome still cannot be determined after this long is voided.
VOID_AFTER = timedelta(days=3)


def target_time(made_at: datetime, horizon: str) -> datetime | None:
    """When the outcome of a prediction made at `made_at` is decided, or None if not scoreable
    (e.g. a 1-hour forecast made at 19:30 ET would end after the extended session)."""
    minutes = HORIZONS[horizon]
    if minutes is None:
        return end_of_day_target(made_at)
    bar_start = made_at - timedelta(minutes=1)
    td = trading_day(bar_start.astimezone(ET).date())
    if td is None:
        return None
    target = made_at + timedelta(minutes=minutes)
    return target if target <= td.after_close else None


def snapshot_rows(pred: dict, made_at: datetime, source: str, now: datetime | None = None) -> list[dict]:
    """Rows to insert for one prediction payload (one per available horizon)."""
    now = now or datetime.now(UTC)
    if now - made_at > MAX_BAR_AGE or not pred.get("available"):
        return []
    rows = []
    for h, p in (pred.get("horizons") or {}).items():
        if not p.get("available"):
            continue
        tgt = target_time(made_at, h)
        if tgt is None:
            continue
        rows.append(
            {
                "made_at": made_at,
                "horizon": h,
                "source": source,
                "p_up": float(p["p_up"]),
                "base_rate": p.get("base_rate"),
                "price": float(pred["price"]),
                "target_at": tgt,
                "model": p.get("model"),
                "model_trained_at": p.get("trained_at"),
                "edge": bool(p.get("edge")),
            }
        )
    return rows


def resolve_due(engine: Engine, symbol: str, now: datetime | None = None) -> dict[str, int]:
    """Fill in outcomes for every pending prediction whose target time has passed."""
    now = now or datetime.now(UTC)
    counts = {"resolved": 0, "void": 0, "waiting": 0}
    pending = db.pending_predictions(engine, now - RESOLVE_GRACE)
    if not pending:
        return counts
    latest = db.latest_bar_ts(engine, symbol)
    data_until = latest + timedelta(minutes=1) if latest else None
    for p in pending:
        tgt = p["target_at"]
        if data_until is None or data_until < tgt:
            # We have not received data up to the target yet (feed gap / server was down).
            if now - tgt > VOID_AFTER:
                db.resolve_prediction(engine, p["id"], status="void", outcome=None, outcome_price=None, now=now)
                counts["void"] += 1
            else:
                counts["waiting"] += 1
            continue
        bar = db.last_bar_ending_by(engine, symbol, tgt)
        bar_end = bar.ts + timedelta(minutes=1) if bar else None
        if bar is None or bar_end.astimezone(ET).date() != tgt.astimezone(ET).date():
            db.resolve_prediction(engine, p["id"], status="void", outcome=None, outcome_price=None, now=now)
            counts["void"] += 1
            continue
        outcome = int(bar.close > p["price"])
        db.resolve_prediction(engine, p["id"], status="resolved", outcome=outcome, outcome_price=bar.close, now=now)
        counts["resolved"] += 1
    return counts


def track_record(engine: Engine, source: str, days: int = 30, now: datetime | None = None) -> dict:
    now = now or datetime.now(UTC)
    since = now - timedelta(days=days)
    rows = db.resolved_predictions(engine, source, since)
    pending = db.count_pending(engine, source)
    by_h: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        by_h[r["horizon"]].append(r)
    out = {"as_of": dual_time(now), "source": source, "days": days, "horizons": {}}
    for h in HORIZONS:
        rs = by_h.get(h, [])
        entry: dict = {"horizon": h, "label": HORIZON_TH[h], "n": len(rs), "pending": pending.get(h, 0)}
        if rs:
            p = np.array([r["p_up"] for r in rs])
            y = np.array([r["outcome"] for r in rs], dtype=float)
            base = np.array([r["base_rate"] if r["base_rate"] is not None else 0.5 for r in rs])
            pred_up = p > 0.5
            hits = pred_up == (y == 1)
            base_hits = (base > 0.5) == (y == 1)
            conf = (p >= 0.55) | (p <= 0.45)
            day_keys = np.array([r["made_at"].astimezone(ET).date().isoformat() for r in rs])
            n_days = len(set(day_keys))
            diff, lo, hi = bootstrap_brier_diff(p, base, y, day_keys)
            if n_days < MIN_TEST_DAYS_FOR_EDGE:
                verdict = "insufficient"
            elif hi < 0:
                verdict = "better"
            elif lo > 0:
                verdict = "worse"
            else:
                verdict = "no_difference"
            daily: dict[str, list[bool]] = defaultdict(list)
            for r, hit in zip(rs, hits):
                daily[r["made_at"].astimezone(ET).date().isoformat()].append(bool(hit))
            entry.update(
                {
                    "hit_rate": float(hits.mean()),
                    "baseline_hit_rate": float(base_hits.mean()),
                    "brier": float(np.mean((p - y) ** 2)),
                    "baseline_brier": float(np.mean((base - y) ** 2)),
                    "up_rate": float(y.mean()),
                    "n_days": n_days,
                    "brier_diff": diff,
                    "brier_diff_ci": [lo, hi],
                    "verdict": verdict,
                    "avg_p_up": float(p.mean()),
                    "confident_n": int(conf.sum()),
                    "confident_hit_rate": float(hits[conf].mean()) if conf.any() else None,
                    "calibration": reliability(p, y),
                    "daily": [{"day": d, "n": len(v), "hit_rate": float(np.mean(v))} for d, v in sorted(daily.items())],
                    "recent": [
                        {
                            "made_at": dual_time(r["made_at"]),
                            "p_up": r["p_up"],
                            "price": r["price"],
                            "outcome_price": r["outcome_price"],
                            "outcome": r["outcome"],
                            "hit": bool((r["p_up"] > 0.5) == (r["outcome"] == 1)),
                        }
                        for r in rs[-15:][::-1]
                    ],
                }
            )
        out["horizons"][h] = entry
    return out
