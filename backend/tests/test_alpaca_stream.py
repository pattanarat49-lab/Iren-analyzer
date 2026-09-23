import asyncio
import json

import websockets

from app.data.alpaca_stream import AlpacaStream, parse_message
from app.models import Bar, Quote, Trade, TradingStatus


def test_parse_message_types():
    kind, t = parse_message({"T": "t", "S": "IREN", "p": 41.5, "s": 100, "t": "2026-09-23T13:30:01.5Z", "c": ["@"]}, "iex")
    assert kind == "trade" and isinstance(t, Trade) and t.price == 41.5
    kind, q = parse_message({"T": "q", "S": "IREN", "bp": 41.4, "ap": 41.6, "bs": 1, "as": 2, "t": "2026-09-23T13:30:01Z"}, "iex")
    assert kind == "quote" and isinstance(q, Quote) and q.ask == 41.6
    bar = {"T": "b", "S": "IREN", "o": 1, "h": 2, "l": 0.5, "c": 1.5, "v": 10, "t": "2026-09-23T13:30:00Z", "n": 2, "vw": 1.2}
    kind, b = parse_message(bar, "iex")
    assert kind == "bar" and isinstance(b, Bar) and b.feed == "iex"
    kind, _ = parse_message({**bar, "T": "u"}, "iex")
    assert kind == "updated_bar"
    kind, s = parse_message({"T": "s", "S": "IREN", "sc": "H", "sm": "Trading Halt", "rc": "T1", "rm": "News", "t": "2026-09-23T13:30:00Z"}, "iex")
    assert kind == "status" and isinstance(s, TradingStatus) and s.halted
    assert parse_message({"T": "subscription"}, "iex") is None


async def test_auth_subscribe_receive_and_reconnect():
    """Fake Alpaca server: first connection sends a trade then drops; client must reconnect."""
    connections = []
    subs_seen = []

    async def server(ws):
        connections.append(ws)
        await ws.send(json.dumps([{"T": "success", "msg": "connected"}]))
        auth = json.loads(await ws.recv())
        assert auth == {"action": "auth", "key": "k", "secret": "s"}
        await ws.send(json.dumps([{"T": "success", "msg": "authenticated"}]))
        subs_seen.append(json.loads(await ws.recv()))
        await ws.send(json.dumps([{"T": "subscription", "trades": ["IREN"]}]))
        await ws.send(json.dumps([{"T": "t", "S": "IREN", "p": 40 + len(connections), "s": 1, "t": "2026-09-23T13:30:00Z"}]))
        if len(connections) == 1:
            await ws.close()
        else:
            await ws.wait_closed()

    received, states = [], []

    async def on_message(kind, payload):
        received.append((kind, payload))

    async def on_state(state, detail):
        states.append(state)

    async with websockets.serve(server, "127.0.0.1", 0) as srv:
        port = srv.sockets[0].getsockname()[1]
        stream = AlpacaStream(
            url=f"ws://127.0.0.1:{port}",
            key="k",
            secret="s",
            subscriptions=[{"trades": ["IREN"]}],
            feed_tag="iex",
            on_message=on_message,
            on_state=on_state,
            name="test",
        )
        task = asyncio.create_task(stream.run())
        for _ in range(100):
            if len(received) >= 2:
                break
            await asyncio.sleep(0.05)
        stream.stop()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    assert [p.price for _, p in received[:2]] == [41, 42]
    assert states[:3] == ["connected", "disconnected", "connected"]
    assert subs_seen[0] == {"action": "subscribe", "trades": ["IREN"]}


async def test_auth_failure_reports_error_state():
    async def server(ws):
        await ws.send(json.dumps([{"T": "success", "msg": "connected"}]))
        await ws.recv()
        await ws.send(json.dumps([{"T": "error", "code": 402, "msg": "auth failed"}]))
        await asyncio.sleep(1)

    states = []

    async def on_state(state, detail):
        states.append((state, detail))

    async def on_message(*_):
        pass

    async with websockets.serve(server, "127.0.0.1", 0) as srv:
        port = srv.sockets[0].getsockname()[1]
        stream = AlpacaStream(
            url=f"ws://127.0.0.1:{port}", key="k", secret="bad", subscriptions=[], feed_tag="iex",
            on_message=on_message, on_state=on_state,
        )
        task = asyncio.create_task(stream.run())
        for _ in range(60):
            if states:
                break
            await asyncio.sleep(0.05)
        stream.stop()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    assert states[0][0] == "error" and "402" in states[0][1]
