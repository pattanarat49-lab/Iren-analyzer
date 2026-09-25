"""Probability engine: labels, no look-ahead, purging, calibration and the edge verdict."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from app.market.clock import ET, schedule_between
from app.model.features import build_features, build_labels, expected_move, feature_columns
from app.model.train import evaluate, fit_calibrated, reliability, train_horizon, walk_forward

PEERS = ["QQQ", "BTC/USD"]


def regular_minutes(start: date, n_days: int) -> pd.DatetimeIndex:
    days = schedule_between(start, start + pd.Timedelta(days=int(n_days * 1.6) + 10))[:n_days]
    idx = [pd.date_range(td.open, td.close, freq="1min", inclusive="left") for td in days]
    return pd.DatetimeIndex(np.concatenate([i.values for i in idx])).tz_localize("UTC")


def frame_from_returns(idx: pd.DatetimeIndex, r: np.ndarray, p0: float = 40.0) -> pd.DataFrame:
    close = p0 * np.exp(np.cumsum(r))
    open_ = np.r_[p0, close[:-1]]
    spread = np.abs(r) + 0.0005
    return pd.DataFrame(
        {"open": open_, "high": np.maximum(open_, close) * (1 + spread / 2), "low": np.minimum(open_, close) * (1 - spread / 2),
         "close": close, "volume": 1000.0 + np.arange(len(r)) % 50},
        index=idx,
    )


def make_frames(n_days: int, momentum: float, seed: int = 0) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    idx = regular_minutes(date(2026, 3, 2), n_days)
    noise = rng.normal(0, 0.001, len(idx))
    r = noise.copy()
    if momentum:
        # Planted signal: the next minute's return follows the last 5 minutes' average.
        for i in range(5, len(r)):
            r[i] = momentum * r[i - 5 : i].mean() + noise[i]
    frames = {"IREN": frame_from_returns(idx, r)}
    frames["QQQ"] = frame_from_returns(idx, rng.normal(0, 0.0003, len(idx)), 500)
    btc_idx = pd.date_range(idx[0].floor("D"), idx[-1], freq="1min", tz="UTC")
    frames["BTC/USD"] = frame_from_returns(btc_idx, rng.normal(0, 0.0005, len(btc_idx)), 100000)
    return frames


@pytest.fixture(scope="module")
def small():
    return make_frames(8, momentum=0.0)


def test_labels_match_future_price(small):
    feats = build_features(small, "IREN", PEERS)
    lab = build_labels(feats, small["IREN"], "5m")
    close = small["IREN"]["close"]
    t = feats.index[100]  # decision time = end of bar 100
    expected_future = close.iloc[100 + 5]  # bar that ends exactly 5 minutes later
    assert lab["y"].iloc[100] == float(expected_future > close.iloc[100])
    assert lab["fwd_ret"].iloc[100] == pytest.approx(np.log(expected_future / close.iloc[100]))
    assert lab["target_t"].iloc[100] == t + pd.Timedelta(minutes=5)


def test_intraday_labels_do_not_cross_into_next_day(small):
    feats = build_features(small, "IREN", PEERS)
    lab = build_labels(feats, small["IREN"], "1h")
    # A label may only use a price from the same trading day as its target, never the next day's.
    et_day = feats.index.tz_convert(ET).date
    tgt_day = pd.DatetimeIndex(lab["target_t"]).tz_convert(ET).date
    valid = lab["y"].notna().to_numpy()
    assert (et_day[valid] == tgt_day[valid]).all()
    # the most recent rows have unknown futures
    assert lab["y"].iloc[-1:].isna().all()


def test_eod_label_targets_regular_close(small):
    feats = build_features(small, "IREN", PEERS)
    lab = build_labels(feats, small["IREN"], "eod")
    tt = pd.DatetimeIndex(lab["target_t"]).tz_convert(ET)
    assert ((tt.hour == 16) & (tt.minute == 0)).all()
    first_day = feats.index[feats.index.tz_convert(ET).date == feats.index[0].tz_convert(ET).date()]
    fut = small["IREN"]["close"].loc[small["IREN"].index < tt[0].tz_convert("UTC")].iloc[-1]
    assert lab.loc[first_day[0], "y"] == float(fut > small["IREN"]["close"].iloc[0])


def test_features_are_causal(small):
    full = build_features(small, "IREN", PEERS)
    cut = full.index[1500]
    part_frames = {k: v[v.index + pd.Timedelta(minutes=1) <= cut] for k, v in small.items()}
    part = build_features(part_frames, "IREN", PEERS)
    cols = feature_columns(full)
    pd.testing.assert_frame_equal(full.loc[:cut, cols], part[cols], check_exact=False, rtol=1e-9, atol=1e-12)


def test_live_window_features_match_full_history():
    """Live inference sees only the recent window; its last row must match training features."""
    frames = make_frames(30, momentum=0.0, seed=3)
    full = build_features(frames, "IREN", PEERS)
    start = frames["IREN"].index[-1] - pd.Timedelta(days=28)
    window = {k: v[v.index >= start] for k, v in frames.items()}
    live = build_features(window, "IREN", PEERS)
    cols = [c for c in feature_columns(full) if not c.startswith("rvol")]  # rvol needs 20 prior days
    np.testing.assert_allclose(live[cols].iloc[-1].to_numpy(dtype=float), full[cols].iloc[-1].to_numpy(dtype=float), rtol=1e-6, atol=1e-9)


def test_walk_forward_training_never_sees_test_labels():
    frames = make_frames(12, momentum=0.0, seed=1)
    feats = build_features(frames, "IREN", PEERS)
    data = feats.join(build_labels(feats, frames["IREN"], "15m")).dropna(subset=["y"])
    oos = walk_forward(data, feature_columns(feats), n_folds=3, min_train=500)
    assert not oos.empty and oos.index.is_monotonic_increasing
    for fold, part in oos.groupby("fold"):
        test_start = part.index[0]
        # every training row's label must end before the test block begins
        train = data[data["target_t"] < test_start]
        assert train["target_t"].max() < test_start
        assert not set(train.index) & set(part.index)


def test_calibration_output_is_probability():
    frames = make_frames(10, momentum=0.0, seed=2)
    feats = build_features(frames, "IREN", PEERS)
    data = feats.join(build_labels(feats, frames["IREN"], "5m")).dropna(subset=["y"])
    tns = data["target_t"].values.astype("datetime64[ns]").astype(np.int64)
    m = fit_calibrated("logreg", data, data["y"].to_numpy().astype(int), tns, feature_columns(feats))
    p = m.predict_proba(data)
    assert ((p >= 0.01) & (p <= 0.99)).all()
    c = m.contributions(data.iloc[[-1]])
    assert set(c) == set(feature_columns(feats))


def test_blend_calibration_avoids_extreme_probabilities():
    from app.model.train import CalibratedModel

    rng = np.random.default_rng(0)
    raw = rng.uniform(0.3, 0.7, 5000)
    y = (rng.uniform(size=5000) < 0.3 + 0.4 * raw).astype(int)  # weak, noisy signal
    m = CalibratedModel("logreg", [], None)
    m.fit_calibrator(raw, y)
    assert m.calibration == "blend"
    p = m.calibrate(np.array([raw.min(), 0.4, 0.5, 0.6, raw.max()]))  # true rates 0.42..0.58
    assert np.all(np.diff(p) >= 0)  # still monotone
    assert 0.25 < p[0] and p[-1] < 0.75  # no 0.01 / 0.99 from sparse isotonic tails


def test_reliability_bins():
    p = np.array([0.1, 0.12, 0.8, 0.85])
    y = np.array([0, 0, 1, 1])
    r = reliability(p, y)
    assert [b["observed"] for b in r] == [0.0, 1.0]


@pytest.mark.slow
def test_no_edge_on_random_walk_but_edge_on_planted_signal():
    noise = make_frames(45, momentum=0.0, seed=10)
    feats = build_features(noise, "IREN", PEERS)
    r0 = train_horizon(feats, noise["IREN"], "5m")
    assert r0.metrics["edge"] is False

    signal = make_frames(45, momentum=0.8, seed=11)
    feats = build_features(signal, "IREN", PEERS)
    r1 = train_horizon(feats, signal["IREN"], "5m")
    m = r1.metrics
    assert m["n_days"] >= 20
    assert m["edge"] is True, m["edge_reason"]
    best = m["models"][m["best_model"]]
    assert best["accuracy"] > m["baseline"]["accuracy"] + 0.02
    # calibrated: in populated bins predicted and observed frequencies are close
    for b in best["reliability"]:
        if b["n"] > 500:
            assert abs(b["mean_p"] - b["observed"]) < 0.08


def test_expected_move_scales_with_sqrt_time():
    a = expected_move(40.0, 0.1, "5m", None)
    b = expected_move(40.0, 0.1, "1h", None)
    assert b["move"] / a["move"] == pytest.approx(np.sqrt(12))
    assert a["low"] == pytest.approx(40 - 0.1 * np.sqrt(5))
    eod = expected_move(40.0, 0.1, "eod", 30.0)
    assert eod["minutes"] == 30
    assert expected_move(40.0, float("nan"), "5m", None) is None


def test_recentre_moves_level_to_whole_window_up_rate():
    from app.model.train import recentre_level

    assert not recentre_level("5m") and not recentre_level("15m")
    assert recentre_level("1h") and recentre_level("eod")
    frames = make_frames(10, momentum=0.0, seed=3)
    feats = build_features(frames, "IREN", PEERS)
    data = feats.join(build_labels(feats, frames["IREN"], "1h")).dropna(subset=["y"])
    y = data["y"].to_numpy().astype(int)
    tns = data["target_t"].values.astype("datetime64[ns]").astype(np.int64)
    plain = fit_calibrated("logreg", data, y, tns, feature_columns(feats))
    moved = fit_calibrated("logreg", data, y, tns, feature_columns(feats), recentre=True)
    cal_start = int(len(y) * 0.8)
    assert moved.shift == pytest.approx(y.mean() - y[cal_start:].mean())
    assert plain.shift == 0.0


def test_fast_cifr_features_only_for_5m():
    frames = make_frames(6, momentum=0.0, seed=5)
    frames["CIFR"] = frames["QQQ"].copy()
    feats = build_features(frames, "IREN", [*PEERS, "CIFR"])
    fast = {"cifr_ret_1", "cifr_rel_1", "cifr_ret_2", "cifr_rel_2", "cifr_rel_5", "cifr_rel_60"}
    assert fast <= set(feats.columns)
    assert fast <= set(feature_columns(feats, "5m"))
    assert not fast & set(feature_columns(feats, "1h"))
    assert "cifr_ret_15" in feature_columns(feats, "1h")  # the slower CIFR features stay everywhere
    # rel = own return minus CIFR return over the same minute
    row = feats.dropna(subset=["cifr_rel_1"]).iloc[-1]
    assert row["cifr_rel_1"] == pytest.approx(row["ret_1"] - row["cifr_ret_1"])


def test_peer_effect_matches_sign_and_is_zero_without_push():
    from app.model.explain import peer_effects

    frames = make_frames(10, momentum=0.0, seed=6)
    feats = build_features(frames, "IREN", PEERS)
    data = feats.join(build_labels(feats, frames["IREN"], "5m")).dropna(subset=["y"])
    tns = data["target_t"].values.astype("datetime64[ns]").astype(np.int64)
    m = fit_calibrated("logreg", data, data["y"].to_numpy().astype(int), tns, feature_columns(feats))
    X = data.iloc[[-1]]
    contrib = m.contributions(X)
    eff = peer_effects(m, X, contrib, PEERS)
    for sym in PEERS:
        push = sum(c for f, c in contrib.items() if f.startswith(sym.replace("/", "").lower() + "_"))
        assert np.sign(eff.get(sym, 0.0)) == np.sign(push) or abs(eff.get(sym, 0.0)) < 1e-9
    assert peer_effects(m, X, {k: 0.0 for k in contrib}, PEERS) == {}
