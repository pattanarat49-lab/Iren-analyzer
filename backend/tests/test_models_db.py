from datetime import datetime, timedelta, timezone

from app import db
from app.models import Bar, parse_ts

UTC = timezone.utc


def test_parse_ts_nanoseconds_and_z():
    ts = parse_ts("2026-09-23T13:30:05.123456789Z")
    assert ts == datetime(2026, 9, 23, 13, 30, 5, 123456, tzinfo=UTC)
    assert parse_ts("2026-09-23T13:30:00Z") == datetime(2026, 9, 23, 13, 30, tzinfo=UTC)
    assert parse_ts("2026-09-23T09:30:00-04:00") == datetime(2026, 9, 23, 13, 30, tzinfo=UTC)


def _bar(i, close=10.0, sym="IREN"):
    t0 = datetime(2026, 9, 23, 13, 30, tzinfo=UTC)
    return Bar(sym, t0 + timedelta(minutes=i), close, close + 1, close - 1, close, 100, feed="iex")


def test_upsert_is_idempotent_and_updates(engine):
    db.upsert_bars(engine, [_bar(0), _bar(1), _bar(2)])
    db.upsert_bars(engine, [_bar(1, close=11.0)])
    rows = db.load_bars(engine, "IREN")
    assert [b.close for b in rows] == [10.0, 11.0, 10.0]
    assert all(b.ts.tzinfo is not None for b in rows)


def test_load_limit_returns_newest_ascending(engine):
    db.upsert_bars(engine, [_bar(i, close=float(i + 1)) for i in range(10)])
    rows = db.load_bars(engine, "IREN", limit=3)
    assert [b.close for b in rows] == [8.0, 9.0, 10.0]
    assert db.latest_bar_ts(engine, "IREN") == rows[-1].ts
    assert db.latest_bar_ts(engine, "NVDA") is None


def test_load_range(engine):
    db.upsert_bars(engine, [_bar(i) for i in range(10)])
    start = datetime(2026, 9, 23, 13, 33, tzinfo=UTC)
    rows = db.load_bars(engine, "IREN", start=start, end=start + timedelta(minutes=2))
    assert [b.ts for b in rows] == [start, start + timedelta(minutes=1)]
