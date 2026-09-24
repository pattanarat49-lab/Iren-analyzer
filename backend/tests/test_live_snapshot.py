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
