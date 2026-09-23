from datetime import date, datetime, timezone

from app import db
from app.data.hub import MarketHub, closes_from_snapshot, reference_trading_day
from app.market.clock import ET
from app.models import Bar, Trade, TradingStatus

UTC = timezone.utc


def et(y, mo, d, h, mi=0, s=0):
    return datetime(y, mo, d, h, mi, s, tzinfo=ET)


async def test_trades_build_forming_bar_and_price(settings, engine):
    hub = MarketHub(settings, engine)
    await hub.handle("trade", Trade("IREN", et(2026, 9, 23, 10, 0, 5), 40.0, 100))
    await hub.handle("trade", Trade("IREN", et(2026, 9, 23, 10, 0, 30), 41.0, 50))
    await hub.handle("trade", Trade("IREN", et(2026, 9, 23, 10, 0, 50), 39.5, 25))
    st = hub.state["IREN"]
    assert st.price == 39.5
    f = st.forming
    assert (f.open, f.high, f.low, f.close, f.volume) == (40.0, 41.0, 39.5, 39.5, 175)
    await hub.handle("trade", Trade("IREN", et(2026, 9, 23, 10, 1, 1), 40.2, 10))
    assert st.forming.open == 40.2


async def test_bar_is_persisted_broadcast_and_listened(settings, engine):
    hub = MarketHub(settings, engine)
    q = hub.subscribe()
    heard = []

    async def listener(bar):
        heard.append(bar)

    hub.add_bar_listener(listener)
    bar = Bar("IREN", et(2026, 9, 23, 10, 0), 40, 41, 39, 40.5, 1000, feed="iex")
    await hub.handle("bar", bar)
    assert db.load_bars(engine, "IREN")[0].close == 40.5
    assert heard == [bar]
    kinds = [q.get_nowait()["type"] for _ in range(q.qsize())]
    assert "bar" in kinds and "quote" in kinds
    # updated bars are persisted but do not re-trigger the analysis listeners
    await hub.handle("updated_bar", Bar("IREN", et(2026, 9, 23, 10, 0), 40, 41, 39, 40.7, 1100, feed="iex"))
    assert db.load_bars(engine, "IREN")[0].close == 40.7
    assert len(heard) == 1


async def test_halt_status_and_resume_on_trade(settings, engine):
    hub = MarketHub(settings, engine)
    await hub.handle("status", TradingStatus("IREN", et(2026, 9, 23, 10, 0), "H", "Trading Halt", "News pending"))
    assert hub.state["IREN"].halted
    await hub.handle("trade", Trade("IREN", et(2026, 9, 23, 10, 5), 40.0, 100))
    assert not hub.state["IREN"].halted


def test_change_vs_prev_close(settings, engine):
    hub = MarketHub(settings, engine)
    st = hub.state["IREN"]
    st.price, st.prev_close = 44.0, 40.0
    j = st.to_json()
    assert j["change"] == 4.0 and j["change_pct"] == 10.0


def test_reference_trading_day():
    assert reference_trading_day(et(2026, 9, 23, 10)) == date(2026, 9, 23)  # regular
    assert reference_trading_day(et(2026, 9, 23, 5)) == date(2026, 9, 23)  # pre-market
    assert reference_trading_day(et(2026, 9, 23, 22)) == date(2026, 9, 23)  # closed at night
    assert reference_trading_day(et(2026, 9, 27, 12)) == date(2026, 9, 25)  # Sunday -> Friday
    assert reference_trading_day(et(2026, 9, 23, 2)) == date(2026, 9, 22)  # before pre-market


def test_closes_from_snapshot():
    snap = {
        "prevDailyBar": {"t": "2026-09-22T04:00:00Z", "c": 40.0},
        "dailyBar": {"t": "2026-09-23T04:00:00Z", "c": 42.0},
    }
    assert closes_from_snapshot(snap, date(2026, 9, 23)) == (40.0, 42.0)
    # pre-market next day: dailyBar is still yesterday's
    assert closes_from_snapshot(snap, date(2026, 9, 24)) == (42.0, None)


def test_prev_close_from_db(settings, engine):
    hub = MarketHub(settings, engine)
    db.upsert_bars(engine, [
        Bar("IREN", et(2026, 9, 22, 15, 59), 40, 40, 40, 40.0, 1, feed="iex"),
        Bar("IREN", et(2026, 9, 22, 17, 0), 41, 41, 41, 41.0, 1, feed="iex"),  # after-hours, ignored
        Bar("IREN", et(2026, 9, 23, 10, 0), 42, 42, 42, 42.0, 1, feed="iex"),
    ])
    assert hub.prev_close_from_db("IREN", et(2026, 9, 23, 10, 5)) == 40.0
