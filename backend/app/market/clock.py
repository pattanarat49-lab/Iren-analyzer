"""US equity market sessions (NYSE calendar) and dual-timezone formatting (US/Eastern + Bangkok).

Session windows (US/Eastern):
    pre-market   04:00 -> regular open (09:30)
    regular      09:30 -> 16:00 (13:00 on half days)
    after-hours  regular close -> 20:00 (17:00 on half days)
    closed       everything else, weekends and exchange holidays
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo

import pandas_market_calendars as mcal

ET = ZoneInfo("America/New_York")
BKK = ZoneInfo("Asia/Bangkok")
UTC = timezone.utc

Session = Literal["pre", "regular", "after", "closed"]

PRE_OPEN = time(4, 0)
AFTER_CLOSE = time(20, 0)
AFTER_CLOSE_HALF_DAY = time(17, 0)

SESSION_LABEL_TH: dict[Session, str] = {
    "pre": "ก่อนตลาดเปิด (Pre-market)",
    "regular": "ตลาดเปิด (Regular)",
    "after": "หลังตลาดปิด (After-hours)",
    "closed": "ตลาดปิด (Closed)",
}


@dataclass(frozen=True)
class TradingDay:
    day: date
    open: datetime  # regular open, UTC
    close: datetime  # regular close, UTC (early on half days)

    @property
    def is_half_day(self) -> bool:
        return self.close.astimezone(ET).time() < time(16, 0)

    @property
    def pre_open(self) -> datetime:
        return datetime.combine(self.day, PRE_OPEN, ET).astimezone(UTC)

    @property
    def after_close(self) -> datetime:
        t = AFTER_CLOSE_HALF_DAY if self.is_half_day else AFTER_CLOSE
        return datetime.combine(self.day, t, ET).astimezone(UTC)


@dataclass(frozen=True)
class SessionState:
    session: Session
    trading_day: TradingDay | None  # the trading day the timestamp belongs to, if any
    next_regular_open: datetime
    next_regular_close: datetime  # close of the current (if not yet passed) or next session

    def to_dict(self) -> dict:
        return {
            "session": self.session,
            "label_th": SESSION_LABEL_TH[self.session],
            "is_half_day": bool(self.trading_day and self.trading_day.is_half_day),
            "next_regular_open": dual_time(self.next_regular_open),
            "next_regular_close": dual_time(self.next_regular_close),
        }


@lru_cache(maxsize=8)
def _schedule(year: int) -> dict[date, TradingDay]:
    cal = mcal.get_calendar("XNYS")
    sched = cal.schedule(start_date=f"{year}-01-01", end_date=f"{year}-12-31")
    out: dict[date, TradingDay] = {}
    for idx, row in sched.iterrows():
        d = idx.date()
        out[d] = TradingDay(
            day=d,
            open=row["market_open"].to_pydatetime().astimezone(UTC),
            close=row["market_close"].to_pydatetime().astimezone(UTC),
        )
    return out


def schedule_between(start: date, end: date) -> list[TradingDay]:
    """All trading days in [start, end], in order."""
    out: list[TradingDay] = []
    for year in range(start.year, end.year + 1):
        out.extend(td for d, td in sorted(_schedule(year).items()) if start <= d <= end)
    return out


def trading_day(d: date) -> TradingDay | None:
    return _schedule(d.year).get(d)


def next_trading_day(d: date, *, include_self: bool = False) -> TradingDay:
    cur = d if include_self else d + timedelta(days=1)
    for _ in range(30):
        td = trading_day(cur)
        if td:
            return td
        cur += timedelta(days=1)
    raise RuntimeError(f"no trading day within 30 days of {d}")


def session_at(ts: datetime) -> SessionState:
    ts = _as_utc(ts)
    today = ts.astimezone(ET).date()
    td = trading_day(today)

    if td and td.pre_open <= ts < td.after_close:
        if ts < td.open:
            session: Session = "pre"
        elif ts < td.close:
            session = "regular"
        else:
            session = "after"
    else:
        session = "closed"
        td = td if td and ts < td.pre_open else None

    if td and ts < td.open:
        nxt_open = td.open
    else:
        nxt_open = next_trading_day(today).open

    if td and ts < td.close:
        nxt_close = td.close
    else:
        nxt_close = next_trading_day(today).close

    return SessionState(session, td, nxt_open, nxt_close)


def end_of_day_target(ts: datetime) -> datetime:
    """Horizon end for the 'end of day' forecast: the next regular-session close at or after ts."""
    return session_at(ts).next_regular_close


def dual_time(ts: datetime | None) -> dict | None:
    """Format a timestamp in UTC (ISO), US/Eastern and Bangkok for display."""
    if ts is None:
        return None
    ts = _as_utc(ts)
    et = ts.astimezone(ET)
    bkk = ts.astimezone(BKK)
    return {
        "utc": ts.isoformat().replace("+00:00", "Z"),
        "et": et.strftime("%Y-%m-%d %H:%M:%S ") + et.tzname(),
        "bkk": bkk.strftime("%Y-%m-%d %H:%M:%S") + " ICT",
    }


def _as_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC)
    return ts.astimezone(UTC)
