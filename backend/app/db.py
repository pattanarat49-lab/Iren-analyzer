"""Database schema and helpers (SQLite by default, Postgres via DATABASE_URL)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    event,
    select,
)
from sqlalchemy.engine import Engine

from .models import Bar, to_utc

metadata = MetaData()

# All timestamps are stored as *naive UTC* so SQLite and Postgres behave identically.


def _naive_utc(ts: datetime) -> datetime:
    return to_utc(ts).replace(tzinfo=None)


bars = Table(
    "bars",
    metadata,
    Column("symbol", String(16), primary_key=True),
    Column("ts", DateTime, primary_key=True),  # bar open time, naive UTC
    Column("open", Float, nullable=False),
    Column("high", Float, nullable=False),
    Column("low", Float, nullable=False),
    Column("close", Float, nullable=False),
    Column("volume", Float, nullable=False),
    Column("vwap", Float),
    Column("trade_count", Integer),
    Column("feed", String(8), nullable=False),
)

stream_events = Table(
    "stream_events",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("ts", DateTime, nullable=False),  # naive UTC
    Column("kind", String(32), nullable=False),  # connected / disconnected / polling / halt / error
    Column("detail", Text),
)


def make_engine(url: str) -> Engine:
    if url.startswith("sqlite:///"):
        Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, future=True, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_conn, _):  # noqa: ANN001
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.close()

    metadata.create_all(engine)
    return engine


def _insert(engine: Engine):
    if engine.dialect.name == "postgresql":
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    return insert


def upsert_bars(engine: Engine, rows: Iterable[Bar], chunk: int = 2000) -> int:
    rows = [b.to_row() for b in rows]
    if not rows:
        return 0
    insert = _insert(engine)
    n = 0
    with engine.begin() as conn:
        for i in range(0, len(rows), chunk):
            part = rows[i : i + chunk]
            stmt = insert(bars).values(part)
            stmt = stmt.on_conflict_do_update(
                index_elements=[bars.c.symbol, bars.c.ts],
                set_={c: stmt.excluded[c] for c in ("open", "high", "low", "close", "volume", "vwap", "trade_count", "feed")},
            )
            conn.execute(stmt)
            n += len(part)
    return n


def load_bars(
    engine: Engine,
    symbol: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
) -> list[Bar]:
    q = select(bars).where(bars.c.symbol == symbol)
    if start is not None:
        q = q.where(bars.c.ts >= _naive_utc(start))
    if end is not None:
        q = q.where(bars.c.ts < _naive_utc(end))
    if limit is not None:
        # newest `limit` bars, returned in ascending order
        q = q.order_by(bars.c.ts.desc()).limit(limit)
        with engine.connect() as conn:
            res = list(conn.execute(q).mappings())
        res.reverse()
    else:
        with engine.connect() as conn:
            res = list(conn.execute(q.order_by(bars.c.ts)).mappings())
    return [Bar.from_row(r) for r in res]


def latest_bar_ts(engine: Engine, symbol: str) -> datetime | None:
    b = load_bars(engine, symbol, limit=1)
    return b[0].ts if b else None


def log_event(engine: Engine, ts: datetime, kind: str, detail: str | None = None) -> None:
    with engine.begin() as conn:
        conn.execute(stream_events.insert().values(ts=_naive_utc(ts), kind=kind, detail=detail))


def recent_events(engine: Engine, limit: int = 50) -> Sequence[dict]:
    q = select(stream_events).order_by(stream_events.c.id.desc()).limit(limit)
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(q).mappings()]
