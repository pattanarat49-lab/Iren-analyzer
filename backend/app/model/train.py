"""Walk-forward training, calibration and honest evaluation of the up/down models.

For each horizon:
1. Walk-forward validation: the last part of the timeline is split into consecutive test blocks.
   Each block is predicted by a model trained only on rows whose *label was already known*
   before the block starts (purging by label end time, so overlapping horizons never leak).
   Nothing is shuffled.
2. Inside every training window, the most recent 20 % is held out to fit the probability
   calibrator (isotonic, or Platt scaling when data is small), again purged by label time.
3. Out-of-sample predictions are compared with a naive baseline: always predict the training
   window's base rate of "up". The model is said to have an edge only if its Brier score is lower
   than the baseline's with 95 % confidence (day-block bootstrap), on at least 20 test days.
4. The better of logistic regression and LightGBM (by out-of-sample Brier) is refit on all data
   and saved together with its metrics.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .features import HORIZONS, build_features, build_labels, feature_columns

log = logging.getLogger(__name__)
UTC = timezone.utc

MODEL_KINDS = ("logreg", "lgbm")
P_CLIP = (0.01, 0.99)
MIN_TEST_DAYS_FOR_EDGE = 20


# ---------------------------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------------------------


def make_estimator(kind: str):  # noqa: ANN201
    if kind == "logreg":
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)),
                ("scale", StandardScaler()),
                ("lr", LogisticRegression(C=0.05, max_iter=2000)),
            ]
        )
    if kind == "lgbm":
        from lightgbm import LGBMClassifier

        return LGBMClassifier(
            n_estimators=300,
            learning_rate=0.03,
            num_leaves=15,
            min_child_samples=200,
            subsample=0.8,
            subsample_freq=1,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            verbose=-1,
            n_jobs=2,
        )
    raise ValueError(kind)


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


@dataclass
class CalibratedModel:
    kind: str
    features: list[str]
    estimator: object
    calibrator: object | None = None
    calibration: str = "none"

    def raw_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.estimator.predict_proba(X[self.features])[:, 1]

    def calibrate(self, raw: np.ndarray) -> np.ndarray:
        if self.calibrator is None:
            p = raw
        elif self.calibration == "isotonic":
            p = self.calibrator.predict(raw)
        else:  # platt
            p = self.calibrator.predict_proba(_logit(raw).reshape(-1, 1))[:, 1]
        return np.clip(p, *P_CLIP)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.calibrate(self.raw_proba(X))

    def fit_calibrator(self, raw: np.ndarray, y: np.ndarray) -> None:
        if len(y) < 200 or len(np.unique(y)) < 2:
            self.calibrator, self.calibration = None, "none"
        elif len(y) >= 2000:
            iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
            iso.fit(raw, y)
            self.calibrator, self.calibration = iso, "isotonic"
        else:
            lr = LogisticRegression(C=1e6, max_iter=1000)
            lr.fit(_logit(raw).reshape(-1, 1), y)
            self.calibrator, self.calibration = lr, "platt"

    def contributions(self, X: pd.DataFrame) -> dict[str, float]:
        """Per-feature push on the (uncalibrated) log-odds for a single row.

        LightGBM: exact TreeSHAP values (pred_contrib). Logistic regression: coefficient ×
        standardised value (the SHAP value of a linear model relative to the average row).
        """
        row = X[self.features].iloc[[-1]]
        if self.kind == "lgbm":
            contrib = self.estimator.booster_.predict(row, pred_contrib=True)[0][:-1]
            return dict(zip(self.features, map(float, contrib)))
        pre = self.estimator[:-1]
        z = pre.transform(row)[0]
        names = pre.get_feature_names_out()
        coefs = self.estimator[-1].coef_[0]
        out: dict[str, float] = {f: 0.0 for f in self.features}
        for name, zi, ci in zip(names, z, coefs):
            base = name.removeprefix("missingindicator_")
            if base in out:
                out[base] += float(zi * ci)
        return out


def fit_calibrated(kind: str, X: pd.DataFrame, y: np.ndarray, target_t: np.ndarray, features: list[str], cal_frac: float = 0.2) -> CalibratedModel:
    """Fit on the older part of the window, calibrate on the most recent `cal_frac` (purged)."""
    n = len(X)
    cal_start_i = int(n * (1 - cal_frac))
    cal_start_t = X.index[cal_start_i]
    fit_mask = target_t < cal_start_t.value  # label known before calibration slice starts
    fit_mask[cal_start_i:] = False
    est = make_estimator(kind)
    Xf, yf = X.loc[fit_mask, features], y[fit_mask]
    if len(np.unique(yf)) < 2:
        raise ValueError("training window has a single class")
    est.fit(Xf, yf)
    model = CalibratedModel(kind, features, est)
    Xc, yc = X.iloc[cal_start_i:], y[cal_start_i:]
    model.fit_calibrator(model.raw_proba(Xc), yc)
    return model


# ---------------------------------------------------------------------------------------------
# Walk-forward evaluation
# ---------------------------------------------------------------------------------------------


def _day_of(index: pd.DatetimeIndex) -> np.ndarray:
    return index.tz_convert("America/New_York").tz_localize(None).normalize().values


def walk_forward(data: pd.DataFrame, features: list[str], n_folds: int = 5, test_frac: float = 0.5, min_train: int = 2000) -> pd.DataFrame:
    """Out-of-sample predictions for every model kind plus the naive baseline.

    `data` must contain the feature columns, `y`, `fwd_ret` and `target_t`, sorted by time.
    """
    days = np.unique(_day_of(data.index))
    n_test_days = max(n_folds, int(len(days) * test_frac))
    test_days = days[-n_test_days:]
    blocks = np.array_split(test_days, n_folds)
    day_of_row = _day_of(data.index)
    target_ns = data["target_t"].values.astype("datetime64[ns]").astype(np.int64)
    y = data["y"].to_numpy().astype(int)

    parts = []
    for bi, block in enumerate(blocks):
        if len(block) == 0:
            continue
        test_mask = np.isin(day_of_row, block)
        test_start = data.index[test_mask][0].value
        train_mask = target_ns < test_start
        if train_mask.sum() < min_train:
            log.info("fold %d skipped: only %d training rows", bi, train_mask.sum())
            continue
        train = data[train_mask]
        test = data[test_mask]
        out = pd.DataFrame(index=test.index)
        out["y"] = y[test_mask]
        out["fwd_ret"] = test["fwd_ret"].to_numpy()
        out["fold"] = bi
        base_rate = float(y[train_mask].mean())
        out["p_baseline"] = base_rate
        for kind in MODEL_KINDS:
            try:
                m = fit_calibrated(kind, train, y[train_mask], target_ns[train_mask], features)
                out[f"p_{kind}"] = m.predict_proba(test)
            except ValueError as e:
                log.warning("fold %d %s failed: %s", bi, kind, e)
                out[f"p_{kind}"] = base_rate
        parts.append(out)
        log.info("fold %d: train %d rows, test %d rows (%s .. %s)", bi, len(train), len(test), block[0], block[-1])
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts)


def _brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def _logloss(p: np.ndarray, y: np.ndarray) -> float:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def reliability(p: np.ndarray, y: np.ndarray, bins: int = 10) -> list[dict]:
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    out = []
    for b in range(bins):
        m = idx == b
        if m.sum() == 0:
            continue
        out.append({"bin_low": float(edges[b]), "bin_high": float(edges[b + 1]), "mean_p": float(p[m].mean()), "observed": float(y[m].mean()), "n": int(m.sum())})
    return out


def bootstrap_brier_diff(p: np.ndarray, base: np.ndarray, y: np.ndarray, days: np.ndarray, n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Mean Brier(model) − Brier(baseline) with a 95 % CI from resampling whole days."""
    d = (p - y) ** 2 - (base - y) ** 2
    frame = pd.DataFrame({"d": d, "day": days}).groupby("day")["d"].agg(["sum", "count"])
    sums, counts = frame["sum"].to_numpy(), frame["count"].to_numpy()
    rng = np.random.default_rng(seed)
    k = len(sums)
    idx = rng.integers(0, k, size=(n_boot, k))
    boots = sums[idx].sum(axis=1) / counts[idx].sum(axis=1)
    return float(d.mean()), float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))


def evaluate(oos: pd.DataFrame) -> dict:
    y = oos["y"].to_numpy().astype(float)
    days = _day_of(oos.index)
    base = oos["p_baseline"].to_numpy()
    base_pred = (base > 0.5).astype(float)
    res: dict = {
        "n": int(len(oos)),
        "n_days": int(len(np.unique(days))),
        "up_rate": float(y.mean()),
        "baseline": {
            "accuracy": float((base_pred == y).mean()),
            "brier": _brier(base, y),
            "logloss": _logloss(base, y),
        },
        "models": {},
    }
    for kind in MODEL_KINDS:
        p = oos[f"p_{kind}"].to_numpy()
        pred = (p > 0.5).astype(float)
        try:
            auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
        except ValueError:
            auc = None
        diff, lo, hi = bootstrap_brier_diff(p, base, y, days)
        conf = (p >= 0.55) | (p <= 0.45)
        fwd = oos["fwd_ret"].to_numpy()
        signed = np.where(p >= 0.5, fwd, -fwd)
        res["models"][kind] = {
            "accuracy": float((pred == y).mean()),
            "brier": _brier(p, y),
            "logloss": _logloss(p, y),
            "auc": auc,
            "brier_skill": 1 - _brier(p, y) / res["baseline"]["brier"] if res["baseline"]["brier"] > 0 else None,
            "brier_diff": diff,
            "brier_diff_ci": [lo, hi],
            "confident_share": float(conf.mean()),
            "confident_accuracy": float((pred[conf] == y[conf]).mean()) if conf.any() else None,
            "mean_signed_fwd_ret_bp": float(np.nanmean(signed) * 1e4),
            "reliability": reliability(p, y),
        }
    best = min(MODEL_KINDS, key=lambda k: res["models"][k]["brier"])
    bm = res["models"][best]
    edge = (
        res["n_days"] >= MIN_TEST_DAYS_FOR_EDGE
        and bm["brier_diff_ci"][1] < 0
        and bm["accuracy"] > res["baseline"]["accuracy"]
    )
    res["best_model"] = best
    res["edge"] = bool(edge)
    res["edge_reason"] = edge_reason(res, best)
    return res


def edge_reason(res: dict, best: str) -> str:
    bm = res["models"][best]
    if res["n_days"] < MIN_TEST_DAYS_FOR_EDGE:
        return f"ข้อมูลทดสอบมีเพียง {res['n_days']} วัน (ต้องมีอย่างน้อย {MIN_TEST_DAYS_FOR_EDGE} วัน) จึงยังสรุปไม่ได้ว่าโมเดลมีความได้เปรียบ"
    if bm["brier_diff_ci"][1] >= 0:
        return "Brier score ของโมเดลไม่ได้ดีกว่าการเดาแบบง่าย (base rate) อย่างมีนัยสำคัญทางสถิติ"
    if bm["accuracy"] <= res["baseline"]["accuracy"]:
        return "ความแม่นยำของโมเดลไม่สูงกว่าการเดาแบบง่าย"
    return "โมเดลดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญในการทดสอบย้อนหลังแบบ walk-forward"


# ---------------------------------------------------------------------------------------------
# End-to-end
# ---------------------------------------------------------------------------------------------


@dataclass
class HorizonResult:
    horizon: str
    metrics: dict
    model: CalibratedModel | None
    meta: dict = field(default_factory=dict)


def prepare(frames: dict[str, pd.DataFrame], primary: str, peers: list[str]) -> pd.DataFrame:
    return build_features(frames, primary, peers)


def train_horizon(feats: pd.DataFrame, primary_frame: pd.DataFrame, horizon: str, n_folds: int = 5) -> HorizonResult:
    labels = build_labels(feats, primary_frame, horizon)
    data = feats.join(labels).dropna(subset=["y"])
    features = feature_columns(feats)
    # Drop features that are entirely missing (e.g. a peer with no history in the database).
    features = [f for f in features if data[f].notna().any()]
    meta = {
        "horizon": horizon,
        "n_rows": int(len(data)),
        "data_start": data.index[0].isoformat() if len(data) else None,
        "data_end": data.index[-1].isoformat() if len(data) else None,
        "features": features,
    }
    if len(data) < 5000:
        return HorizonResult(horizon, {"error": f"ข้อมูลน้อยเกินไป ({len(data)} แถว)"}, None, meta)
    oos = walk_forward(data, features, n_folds=n_folds)
    if oos.empty:
        return HorizonResult(horizon, {"error": "walk-forward ไม่มี fold ที่ใช้ได้"}, None, meta)
    metrics = evaluate(oos)
    target_ns = data["target_t"].values.astype("datetime64[ns]").astype(np.int64)
    final = fit_calibrated(metrics["best_model"], data, data["y"].to_numpy().astype(int), target_ns, features)
    return HorizonResult(horizon, metrics, final, meta)


def train_all(frames: dict[str, pd.DataFrame], primary: str, peers: list[str], out_dir: Path, source: str, horizons: list[str] | None = None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    feats = prepare(frames, primary, peers)
    report = {"trained_at": datetime.now(UTC).isoformat(), "source": source, "primary": primary, "peers": peers, "horizons": {}}
    for h in horizons or list(HORIZONS):
        log.info("training horizon %s", h)
        r = train_horizon(feats, frames[primary], h)
        report["horizons"][h] = {"metrics": r.metrics, "meta": {k: v for k, v in r.meta.items() if k != "features"}}
        if r.model is not None:
            joblib.dump({"model": r.model, "metrics": r.metrics, "meta": r.meta, "source": source, "trained_at": report["trained_at"]}, out_dir / f"{h}.joblib")
    (out_dir / "report.json").write_text(json.dumps(_jsonable(report), ensure_ascii=False, indent=2))
    return report


def _jsonable(x):  # noqa: ANN001, ANN202
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if math.isnan(float(x)) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x
