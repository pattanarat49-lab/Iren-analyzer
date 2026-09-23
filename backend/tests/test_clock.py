from datetime import datetime, timezone

from app.market.clock import ET, dual_time, end_of_day_target, session_at

UTC = timezone.utc


def et(y, mo, d, h, mi=0):
    return datetime(y, mo, d, h, mi, tzinfo=ET)


def test_regular_session_bounds():
    assert session_at(et(2026, 9, 23, 9, 29)).session == "pre"
    assert session_at(et(2026, 9, 23, 9, 30)).session == "regular"
    assert session_at(et(2026, 9, 23, 15, 59)).session == "regular"
    assert session_at(et(2026, 9, 23, 16, 0)).session == "after"
    assert session_at(et(2026, 9, 23, 19, 59)).session == "after"
    assert session_at(et(2026, 9, 23, 20, 0)).session == "closed"
    assert session_at(et(2026, 9, 23, 3, 59)).session == "closed"
    assert session_at(et(2026, 9, 23, 4, 0)).session == "pre"


def test_weekend_and_holiday_closed():
    assert session_at(et(2026, 9, 26, 12)).session == "closed"  # Saturday
    ss = session_at(et(2026, 11, 26, 12))  # Thanksgiving
    assert ss.session == "closed"
    assert ss.next_regular_open.astimezone(ET) == et(2026, 11, 27, 9, 30)


def test_half_day_after_thanksgiving():
    ss = session_at(et(2026, 11, 27, 12, 30))
    assert ss.session == "regular" and ss.trading_day.is_half_day
    assert ss.next_regular_close.astimezone(ET) == et(2026, 11, 27, 13, 0)
    assert session_at(et(2026, 11, 27, 13, 30)).session == "after"
    assert session_at(et(2026, 11, 27, 17, 0)).session == "closed"


def test_end_of_day_target():
    # during regular hours -> today's close
    assert end_of_day_target(et(2026, 9, 23, 10)).astimezone(ET) == et(2026, 9, 23, 16)
    # pre-market -> today's close
    assert end_of_day_target(et(2026, 9, 23, 5)).astimezone(ET) == et(2026, 9, 23, 16)
    # after-hours Friday -> Monday's close
    assert end_of_day_target(et(2026, 9, 25, 17)).astimezone(ET) == et(2026, 9, 28, 16)


def test_next_open_after_close():
    ss = session_at(et(2026, 9, 23, 21))
    assert ss.next_regular_open.astimezone(ET) == et(2026, 9, 24, 9, 30)
    ss = session_at(et(2026, 9, 23, 2))
    assert ss.next_regular_open.astimezone(ET) == et(2026, 9, 23, 9, 30)


def test_dual_time_bangkok_is_utc_plus_7():
    d = dual_time(datetime(2026, 9, 23, 13, 30, tzinfo=UTC))
    assert d["utc"] == "2026-09-23T13:30:00Z"
    assert d["et"] == "2026-09-23 09:30:00 EDT"
    assert d["bkk"] == "2026-09-23 20:30:00 ICT"
    # Winter: ET is UTC-5, Bangkok has no DST
    d = dual_time(datetime(2026, 12, 1, 14, 30, tzinfo=UTC))
    assert d["et"] == "2026-12-01 09:30:00 EST"
    assert d["bkk"] == "2026-12-01 21:30:00 ICT"
