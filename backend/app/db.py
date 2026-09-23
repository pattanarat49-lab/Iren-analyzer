"""Database schema and helpers (SQLite by default, Postgres via DATABASE_URL)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    UniqueConstraint,
    event,
    select,
    update,
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


# One row per horizon per minute: what the model said, and (later) what actually happened.
predictions = Table(
    "predictions",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True),
    Column("made_at", DateTime, nullable=False),  # decision time = end of the bar used (naive UTC)
    Column("horizon", String(8), nullable=False),
    Column("source", String(8), nullable=False),  # alpaca | demo
    Column("p_up", Float, nullable=False),
    Column("base_rate", Float),  # training up-rate: the naive baseline's forecast
    Column("price", Float, nullable=False),
    Column("target_at", DateTime, nullable=False),  # when the outcome is decided (naive UTC)
    Column("model", String(16)),
    Column("model_trained_at", String(40)),
    Column("edge", Boolean),
    Column("outcome", Integer),  # 1 = price at target > price, 0 = not, NULL = pending / void
    Column("outcome_price", Float),
    Column("status", String(8), nullable=False, default="pending"),  # pending | resolved | void
    Column("resolved_at", DateTime),
    UniqueConstraint("made_at", "horizon", "source", name="uq_prediction"),
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


# ---- predictions / track record ----------------------------------------------------------------


def insert_predictions(engine: Engine, rows: list[dict]) -> int:
    """Insert prediction snapshots; a (made_at, horizon, source) that already exists is ignored."""
    if not rows:
        return 0
    insert = _insert(engine)
    clean = [{**r, "made_at": _naive_utc(r["made_at"]), "target_at": _naive_utc(r["target_at"]), "status": "pending"} for r in rows]
    stmt = (
        insert(predictions)
        .values(clean)
        .on_conflict_do_nothing(index_elements=["made_at", "horizon", "source"])
        .returning(predictions.c.id)
    )
    with engine.begin() as conn:
        # Count returned ids: rowcount is unreliable for multi-row inserts on some drivers.
        return len(conn.execute(stmt).fetchall())


def pending_predictions(engine: Engine, due_before: datetime, limit: int = 5000) -> list[dict]:
    q = (
        select(predictions)
        .where(predictions.c.status == "pending", predictions.c.target_at <= _naive_utc(due_before))
        .order_by(predictions.c.target_at)
        .limit(limit)
    )
    with engine.connect() as conn:
        rows = [dict(r) for r in conn.execute(q).mappings()]
    for r in rows:
        r["made_at"], r["target_at"] = to_utc(r["made_at"]), to_utc(r["target_at"])
    return rows


def resolve_prediction(engine: Engine, pid: int, *, status: str, outcome: int | None, outcome_price: float | None, now: datetime) -> None:
    with engine.begin() as conn:
        conn.execute(
            update(predictions)
            .where(predictions.c.id == pid)
            .values(status=status, outcome=outcome, outcome_price=outcome_price, resolved_at=_naive_utc(now))
        )


def resolved_predictions(engine: Engine, source: str, since: datetime, horizon: str | None = None) -> list[dict]:
    q = select(predictions).where(
        predictions.c.status == "resolved", predictions.c.source == source, predictions.c.made_at >= _naive_utc(since)
    )
    if horizon:
        q = q.where(predictions.c.horizon == horizon)
    with engine.connect() as conn:
        rows = [dict(r) for r in conn.execute(q.order_by(predictions.c.made_at)).mappings()]
    for r in rows:
        r["made_at"], r["target_at"] = to_utc(r["made_at"]), to_utc(r["target_at"])
    return rows


def count_pending(engine: Engine, source: str) -> dict[str, int]:
    from sqlalchemy import func

    q = (
        select(predictions.c.horizon, func.count())
        .where(predictions.c.status == "pending", predictions.c.source == source)
        .group_by(predictions.c.horizon)
    )
    with engine.connect() as conn:
        return {h: n for h, n in conn.execute(q)}


def last_bar_ending_by(engine: Engine, symbol: str, t: datetime, lookback: timedelta = timedelta(days=4)) -> Bar | None:
    """The bar whose close is the last trade price at time t (bar end = ts + 1 min <= t)."""
    q = (
        select(bars)
        .where(
            bars.c.symbol == symbol,
            bars.c.ts <= _naive_utc(t - timedelta(minutes=1)),
            bars.c.ts >= _naive_utc(t - lookback),
        )
        .order_by(bars.c.ts.desc())
        .limit(1)
    )
    with engine.connect() as conn:
        row = conn.execute(q).mappings().first()
    return Bar.from_row(row) if row else None
