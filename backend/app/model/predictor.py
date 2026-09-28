"""Live inference: loads the saved per-horizon models and scores the latest bar."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ..market.clock import dual_time
from .explain import group_effects, peer_effects, top_factors
from .features import HORIZON_TH, HORIZONS, INDICATOR_GROUPS, build_features, expected_move

log = logging.getLogger(__name__)
UTC = timezone.utc


def model_dir(models_root: Path, source: str) -> Path:
    """Real and demo models are kept apart so simulated data can never drive real predictions."""
    return models_root / source


class Predictor:
    def __init__(self, directory: Path, primary: str, peers: list[str]) -> None:
        self.dir = directory
        self.primary = primary
        self.peers = peers
        self.bundles: dict[str, dict] = {}
        self.mtimes: dict[str, float] = {}

    def load(self) -> None:
        """(Re)load any model file that is new or changed (e.g. after the nightly retrain)."""
        for h in HORIZONS:
            path = self.dir / f"{h}.joblib"
            if not path.exists():
                self.bundles.pop(h, None)
                continue
            mtime = path.stat().st_mtime
            if self.mtimes.get(h) == mtime:
                continue
            try:
                self.bundles[h] = joblib.load(path)
                self.mtimes[h] = mtime
                log.info("loaded %s model (%s)", h, self.bundles[h]["model"].kind)
            except Exception:  # noqa: BLE001
                log.exception("failed to load %s", path)

    def summary(self) -> dict:
        out = {}
        for h in HORIZONS:
            b = self.bundles.get(h)
            out[h] = None if b is None else {"trained_at": b.get("trained_at"), "metrics": b["metrics"], "meta": {k: v for k, v in b["meta"].items() if k != "features"}}
        return out

    def predict(self, frames: dict[str, pd.DataFrame], live_price: float | None = None) -> dict:
        now = datetime.now(UTC)
        base = {"as_of": dual_time(now)}
        if not self.bundles:
            return {**base, "available": False, "horizons": {h: _unavailable(h) for h in HORIZONS}}
        feats = build_features(frames, self.primary, self.peers)
        if feats.empty:
            return {**base, "available": False, "horizons": {h: _unavailable(h, "ยังไม่มีข้อมูลราคา") for h in HORIZONS}}
        last = feats.iloc[[-1]]
        row = {k: (None if pd.isna(v) else float(v)) for k, v in last.iloc[0].items()}
        price = row["price"]
        out: dict[str, dict] = {}
        for h in HORIZONS:
            b = self.bundles.get(h)
            if b is None:
                out[h] = _unavailable(h)
                continue
            m = b["model"]
            metrics = b["metrics"]
            try:
                p_up = float(m.predict_proba(last)[0])
                contrib = m.contributions(last)
            except Exception as e:  # noqa: BLE001
                log.exception("prediction failed for %s", h)
                out[h] = _unavailable(h, f"คำนวณไม่สำเร็จ: {e}")
                continue
            best = metrics["models"][metrics["best_model"]]
            out[h] = {
                "horizon": h,
                "label": HORIZON_TH[h],
                "available": True,
                "p_up": p_up,
                "p_down": 1 - p_up,
                "model": m.kind,
                "calibration": m.calibration,
                "edge": metrics["edge"],
                "base_rate": b["meta"].get("train_up_rate", metrics.get("up_rate")),
                "edge_reason": metrics["edge_reason"],
                "metrics": {
                    "accuracy": best["accuracy"],
                    "brier": best["brier"],
                    "auc": best["auc"],
                    "baseline_accuracy": metrics["baseline"]["accuracy"],
                    "baseline_brier": metrics["baseline"]["brier"],
                    "brier_diff_ci": best["brier_diff_ci"],
                    "n_test": metrics["n"],
                    "n_test_days": metrics["n_days"],
                    "up_rate": metrics["up_rate"],
                    "reliability": best["reliability"],
                },
                "factors": top_factors(contrib, row, self.primary, self.peers),
                "peer_effects": peer_effects(m, last, contrib, self.peers),
                "indicator_effects": group_effects(m, last, contrib, INDICATOR_GROUPS),
                "expected_move": expected_move(price, row.get("atr") or float("nan"), h, row.get("mins_to_eod")),
                "trained_at": b.get("trained_at"),
                "source": b.get("source"),
            }
        apply_near_close(out, row.get("mins_to_eod"))
        return {
            **base,
            "available": True,
            "bar_time": dual_time(feats.index[-1].to_pydatetime()),
            "made_at": feats.index[-1].isoformat(),  # decision time (UTC) used for the track record
            "price": price,
            "live_price": live_price,
            "peer_moves": _peer_moves(row, self.primary, self.peers),
            "horizons": out,
        }


def near_close_source(mins_to_eod: float | None) -> str | None:
    """Horizon whose model should answer the end-of-day question this close to the close.

    Near the close the end-of-day model, trained mostly on decision times hours before the
    close, was worse than the naive baseline in the walk-forward (last 60 minutes: Brier
    +0.00100 vs baseline), while the 1-hour model scored on the same end-of-day outcomes was
    better (-0.00090). With 5 minutes or less left the question is the 5-minute one, so both
    cards show the same number. Overall end-of-day Brier improved from -0.00114 to -0.00142.
    """
    if mins_to_eod is None or not np.isfinite(mins_to_eod) or mins_to_eod <= 0:
        return None
    if mins_to_eod <= 5:
        return "5m"
    if mins_to_eod <= 60:
        return "1h"
    return None


def apply_near_close(out: dict[str, dict], mins_to_eod: float | None) -> None:
    """Replace the end-of-day forecast with the shorter-horizon one near the close (in place)."""
    src = near_close_source(mins_to_eod)
    eod, other = out.get("eod"), out.get(src) if src else None
    if not (eod and other and eod.get("available") and other.get("available")):
        return
    for k in ("p_up", "p_down", "factors", "peer_effects", "indicator_effects", "model"):
        eod[k] = other.get(k)
    eod["source_horizon"] = src
    eod["source_note"] = (
        f"เหลือเวลาถึงปิดตลาด {mins_to_eod:.0f} นาที จึงใช้ตัวเลขจากโมเดล {HORIZON_TH[src]} "
        "ซึ่งทดสอบย้อนหลังแล้วทายราคาปิดได้ดีกว่าโมเดลถึงปิดตลาดในช่วงนี้"
    )


def _peer_moves(row: dict, primary: str, peers: list[str]) -> dict[str, dict]:
    """Recent returns of each peer and how the primary did relative to it (log returns)."""
    out = {}
    for sym in peers:
        tag = sym.replace("/", "").lower()
        moves = {k: row.get(f"{tag}_{k}") for k in ("ret_1", "ret_5", "ret_15", "ret_60", "rel_1", "rel_5", "rel_15", "rel_60")}
        out[sym] = {k: v for k, v in moves.items() if v is not None}
    return out


def _unavailable(h: str, reason: str = "ยังไม่ได้ฝึกโมเดลสำหรับช่วงเวลานี้ (รัน python -m scripts.train)") -> dict:
    return {"horizon": h, "label": HORIZON_TH[h], "available": False, "reason": reason}


def clean_json(x):  # noqa: ANN001, ANN202
    if isinstance(x, dict):
        return {k: clean_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean_json(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x
