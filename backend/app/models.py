"""Plain data types shared by the data sources, the database layer and the API."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc


def to_utc(ts: datetime) -> datetime:
    return ts.replace(tzinfo=UTC) if ts.tzinfo is None else ts.astimezone(UTC)


def parse_ts(s: str) -> datetime:
    """Parse an RFC3339 timestamp (Alpaca uses nanosecond precision, e.g. ...:05.123456789Z)."""
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    # Trim fractional seconds to microseconds for datetime.fromisoformat.
    if "." in s:
        head, rest = s.split(".", 1)
        frac = ""
        i = 0
        while i < len(rest) and rest[i].isdigit():
            frac += rest[i]
            i += 1
        s = f"{head}.{frac[:6].ljust(6, '0')}{rest[i:]}"
    return to_utc(datetime.fromisoformat(s))


@dataclass
class Bar:
    symbol: str
    ts: datetime  # bar open time (UTC); 1-minute bars
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float | None = None
    trade_count: int | None = None
    feed: str = "iex"

    def __post_init__(self) -> None:
        self.ts = to_utc(self.ts)

    def to_row(self) -> dict:
        d = asdict(self)
        # Stored as naive UTC so SQLite and Postgres behave identically.
        d["ts"] = self.ts.replace(tzinfo=None)
        return d

    @classmethod
    def from_row(cls, r) -> Bar:  # noqa: ANN001 - SQLAlchemy RowMapping
        return cls(
            symbol=r["symbol"],
            ts=to_utc(r["ts"]),
            open=r["open"],
            high=r["high"],
            low=r["low"],
            close=r["close"],
            volume=r["volume"],
            vwap=r["vwap"],
            trade_count=r["trade_count"],
            feed=r["feed"],
        )

    def to_json(self) -> dict:
        d = asdict(self)
        d["ts"] = self.ts.isoformat().replace("+00:00", "Z")
        d["time"] = int(self.ts.timestamp())  # epoch seconds, for Lightweight Charts
        return d


@dataclass
class Trade:
    symbol: str
    ts: datetime
    price: float
    size: float
    conditions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.ts = to_utc(self.ts)


@dataclass
class Quote:
    symbol: str
    ts: datetime
    bid: float
    ask: float
    bid_size: float
    ask_size: float

    def __post_init__(self) -> None:
        self.ts = to_utc(self.ts)


@dataclass
class TradingStatus:
    symbol: str
    ts: datetime
    code: str  # Alpaca status code, e.g. "H" halted, "T" trading
    message: str
    reason: str = ""

    @property
    def halted(self) -> bool:
        # UTP (Nasdaq-listed): H = halt, P = volatility pause, Q = quotation only.
        # CTS (NYSE/other): 2 = trading halt.
        return self.code in {"H", "P", "Q", "2"}
