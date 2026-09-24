from datetime import datetime, timedelta, timezone

from scripts.live_snapshot import mark_validity

UTC = timezone.utc


def _pred(made_at: datetime) -> dict:
    return {
        "available": True,
        "made_at": made_at.isoformat(),
        "horizons": {h: {"available": True, "p_up": 0.5} for h in ("5m", "1h", "eod")},
    }


def test_regular_session_forecasts_are_valid():
    made = datetime(2026, 9, 23, 18, 0, tzinfo=UTC)  # Wed 14:00 ET
    p = mark_validity(_pred(made), made + timedelta(minutes=2))
    assert all(h["valid"] for h in p["horizons"].values())
    assert p["horizons"]["5m"]["target_at"]["utc"].startswith("2026-09-23T18:05")


def test_horizon_ending_after_extended_session_is_invalid():
    made = datetime(2026, 9, 23, 23, 30, tzinfo=UTC)  # Wed 19:30 ET
    h = mark_validity(_pred(made), made + timedelta(minutes=1))["horizons"]
    assert h["5m"]["valid"] and not h["1h"]["valid"] and h["eod"]["valid"]


def test_stale_bar_is_invalid():
    made = datetime(2026, 9, 23, 18, 0, tzinfo=UTC)
    h = mark_validity(_pred(made), made + timedelta(hours=2))["horizons"]
    assert not any(x["valid"] for x in h.values())


def test_last_valid_decision_skips_bars_whose_horizon_ends_after_the_session():
    import pandas as pd

    from scripts.live_snapshot import last_valid_decision

    # Bars (start times) up to 19:59 ET on Wed 2026-09-23 (23:59 UTC).
    idx = pd.date_range("2026-09-23 23:00", "2026-09-23 23:59", freq="1min", tz="UTC")
    assert last_valid_decision(idx, "5m") == datetime(2026, 9, 23, 23, 55, tzinfo=UTC)
    # Every 1h forecast from these bars would end after 20:00 ET.
    assert last_valid_decision(idx, "1h") is None
    wider = pd.date_range("2026-09-23 22:00", "2026-09-23 23:59", freq="1min", tz="UTC")
    assert last_valid_decision(wider, "1h") == datetime(2026, 9, 23, 23, 0, tzinfo=UTC)
    assert last_valid_decision(idx, "eod") == datetime(2026, 9, 24, 0, 0, tzinfo=UTC)


def test_track_record_logs_only_valid_forecasts_once_and_scores_them(tmp_path):
    from app import db
    from app.market.clock import ET
    from app.models import Bar
    from scripts.live_snapshot import update_track_record

    made = datetime(2026, 9, 23, 10, 0, tzinfo=ET)
    bars = db.make_engine(f"sqlite:///{tmp_path / 'bars.db'}")
    db.upsert_bars(bars, [Bar("IREN", made + timedelta(minutes=m - 1), 41.0, 41.0, 41.0, 41.0, 100, feed="iex") for m in range(1, 21)])
    pred = {
        "available": True,
        "made_at": made.astimezone(UTC).isoformat(),
        "price": 40.0,
        "horizons": {
            "5m": {"available": True, "valid": True, "p_up": 0.7, "model": "lgbm", "edge": False, "base_rate": 0.5},
            "1h": {"available": True, "valid": False, "p_up": 0.2, "model": "lgbm", "edge": False, "base_rate": 0.5},
        },
    }
    track = tmp_path / "track.db"
    update_track_record(track, bars, pred, "IREN", "alpaca")
    rec = update_track_record(track, bars, pred, "IREN", "alpaca")  # same bar again: not logged twice
    h5 = rec["horizons"]["5m"]
    assert h5["n"] == 1 and h5["hit_rate"] == 1.0  # said up (0.7), price 40 -> 41
    assert rec["horizons"]["1h"]["n"] == 0 and rec["horizons"]["1h"]["pending"] == 0  # invalid: never logged
