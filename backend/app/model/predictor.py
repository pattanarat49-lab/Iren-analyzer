"""Live inference: loads the saved per-horizon models and scores the latest bar."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from ..market.clock import dual_time
from .explain import top_factors
from .features import HORIZON_TH, HORIZONS, build_features, expected_move

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
                "expected_move": expected_move(price, row.get("atr") or float("nan"), h, row.get("mins_to_eod")),
                "trained_at": b.get("trained_at"),
                "source": b.get("source"),
            }
        return {
            **base,
            "available": True,
            "bar_time": dual_time(feats.index[-1].to_pydatetime()),
            "made_at": feats.index[-1].isoformat(),  # decision time (UTC) used for the track record
            "price": price,
            "live_price": live_price,
            "horizons": out,
        }


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
