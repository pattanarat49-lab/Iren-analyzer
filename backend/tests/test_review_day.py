import joblib
import numpy as np

from app.model.features import build_features, build_labels, feature_columns
from app.model.train import fit_calibrated
from scripts.review_day import review
from tests.test_model import PEERS, make_frames


def test_review_scores_latest_day_out_of_sample(tmp_path):
    frames = make_frames(12, momentum=0.0, seed=4)
    feats = build_features(frames, "IREN", PEERS)
    data = feats.join(build_labels(feats, frames["IREN"], "5m")).dropna(subset=["y"])
    tns = data["target_t"].values.astype("datetime64[ns]").astype(np.int64)
    model = fit_calibrated("logreg", data, data["y"].to_numpy().astype(int), tns, feature_columns(feats))
    joblib.dump({"model": model, "meta": {"train_up_rate": 0.5}, "metrics": {"up_rate": 0.5}}, tmp_path / "5m.joblib")

    r = review(frames, "IREN", PEERS, tmp_path)
    last_day = max(frames["IREN"].index.tz_convert("America/New_York").date)
    assert r["day"] == last_day.isoformat()
    h = r["horizons"]["5m"]
    assert set(r["horizons"]) == {"5m"}  # only horizons with a saved model
    assert 300 < h["n"] <= 390  # regular-session minutes with a known 5-minute outcome
    assert 0 <= h["hit_rate"] <= 1 and 0.4 <= h["mean_p"] <= 0.6
    assert sum(b["n"] for b in h["by_hour"]) == h["n"]
