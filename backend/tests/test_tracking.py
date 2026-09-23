from datetime import datetime, timedelta, timezone

import pytest

from app import db
from app.market.clock import ET
from app.model.scheduler import next_retrain_time
from app.model.tracking import resolve_due, snapshot_rows, target_time, track_record
from app.models import Bar

UTC = timezone.utc


def et(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=ET)


def pred_payload(p_up=0.6, price=40.0):
    h = {"available": True, "p_up": p_up, "model": "lgbm", "trained_at": "x", "edge": False, "base_rate": 0.5}
    return {"available": True, "price": price, "horizons": {"5m": dict(h), "15m": dict(h), "1h": dict(h), "eod": dict(h)}}


def test_target_times():
    t = et(2026, 9, 23, 10, 0)
    assert target_time(t, "5m") == t + timedelta(minutes=5)
    assert target_time(t, "eod").astimezone(ET) == et(2026, 9, 23, 16, 0)
    assert target_time(et(2026, 9, 23, 19, 30), "1h") is None  # would end after 20:00 ET
    assert target_time(et(2026, 9, 23, 19, 30), "15m") is not None
    assert target_time(et(2026, 9, 23, 17, 0), "eod").astimezone(ET) == et(2026, 9, 24, 16, 0)
    assert target_time(et(2026, 9, 26, 12, 0), "5m") is None  # Saturday


def test_snapshot_rows_skip_stale_and_unscoreable():
    made = et(2026, 9, 23, 19, 30)
    rows = snapshot_rows(pred_payload(), made, "demo", now=made + timedelta(seconds=5))
    assert {r["horizon"] for r in rows} == {"5m", "15m", "eod"}  # 1h would end after hours
    assert snapshot_rows(pred_payload(), made, "demo", now=made + timedelta(minutes=10)) == []


def _bar(t_et, close):
    return Bar("IREN", t_et - timedelta(minutes=1), close, close, close, close, 100, feed="iex")  # ends at t_et


def test_log_resolve_and_score(engine):
    made = et(2026, 9, 23, 10, 0)
    rows = snapshot_rows(pred_payload(p_up=0.7, price=40.0), made, "demo", now=made)
    assert db.insert_predictions(engine, rows) == 4
    assert db.insert_predictions(engine, rows) == 0  # same bar again: ignored

    # bars: price at 10:05 = 41 (up), at 10:15 = 39 (down); data reaches 10:20
    db.upsert_bars(engine, [_bar(made, 40.0), _bar(made + timedelta(minutes=5), 41.0),
                            _bar(made + timedelta(minutes=15), 39.0), _bar(made + timedelta(minutes=20), 39.5)])
    counts = resolve_due(engine, "IREN", now=made + timedelta(minutes=30))
    assert counts == {"resolved": 2, "void": 0, "waiting": 0}  # 1h and eod not due yet

    rec = track_record(engine, "demo", days=3650, now=made + timedelta(minutes=30))
    h5, h15 = rec["horizons"]["5m"], rec["horizons"]["15m"]
    assert h5["n"] == 1 and h5["hit_rate"] == 1.0 and h5["brier"] == pytest.approx(0.09)
    assert h15["n"] == 1 and h15["hit_rate"] == 0.0 and h15["brier"] == pytest.approx(0.49)
    assert h15["baseline_brier"] == pytest.approx(0.25)
    assert rec["horizons"]["1h"]["pending"] == 1 and rec["horizons"]["eod"]["pending"] == 1


def test_waits_for_data_then_voids(engine):
    made = et(2026, 9, 23, 10, 0)
    db.insert_predictions(engine, [r for r in snapshot_rows(pred_payload(), made, "demo", now=made) if r["horizon"] == "5m"])
    db.upsert_bars(engine, [_bar(made, 40.0)])  # no data beyond the decision time
    assert resolve_due(engine, "IREN", now=made + timedelta(minutes=10))["waiting"] == 1
    assert resolve_due(engine, "IREN", now=made + timedelta(days=4))["void"] == 1


def test_outcome_needs_same_day_price(engine):
    made = et(2026, 9, 23, 19, 50)
    db.insert_predictions(engine, [r for r in snapshot_rows(pred_payload(), made, "demo", now=made) if r["horizon"] == "5m"])
    db.upsert_bars(engine, [_bar(made, 40.0), _bar(et(2026, 9, 24, 4, 1), 45.0)])  # next print is next day
    # the last print at 19:55 is still the 19:50 bar (same day) -> resolved as "not up"
    assert resolve_due(engine, "IREN", now=et(2026, 9, 24, 5, 0))["resolved"] == 1
    rec = track_record(engine, "demo", days=3650, now=et(2026, 9, 24, 5, 0))
    assert rec["horizons"]["5m"]["up_rate"] == 0.0


def test_next_retrain_time():
    assert next_retrain_time(et(2026, 9, 23, 12, 0)).astimezone(ET) == et(2026, 9, 23, 20, 30)
    assert next_retrain_time(et(2026, 9, 23, 21, 0)).astimezone(ET) == et(2026, 9, 24, 20, 30)
    assert next_retrain_time(et(2026, 9, 25, 21, 0)).astimezone(ET) == et(2026, 9, 28, 20, 30)  # Fri -> Mon
    assert next_retrain_time(et(2026, 11, 27, 9, 0)).astimezone(ET) == et(2026, 11, 27, 17, 30)  # half day


def test_live_verdict_needs_enough_days(engine):
    made = et(2026, 9, 23, 10, 0)
    db.insert_predictions(engine, snapshot_rows(pred_payload(p_up=0.9), made, "demo", now=made))
    db.upsert_bars(engine, [_bar(made, 40.0), _bar(made + timedelta(minutes=5), 41.0), _bar(made + timedelta(minutes=20), 41.0)])
    resolve_due(engine, "IREN", now=made + timedelta(minutes=30))
    rec = track_record(engine, "demo", days=3650, now=made + timedelta(minutes=30))
    assert rec["horizons"]["5m"]["verdict"] == "insufficient"  # 1 day is never enough to claim anything
