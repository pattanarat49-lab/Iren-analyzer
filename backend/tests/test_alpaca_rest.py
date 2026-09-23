import json
from datetime import datetime, timezone

import httpx
import pytest

from app.data.alpaca_rest import AlpacaAuthError, AlpacaRest
from app.data.ratelimit import RateLimiter

UTC = timezone.utc
START = datetime(2026, 9, 22, tzinfo=UTC)
END = datetime(2026, 9, 23, tzinfo=UTC)


def _bar(t, c):
    return {"t": t, "o": c, "h": c, "l": c, "c": c, "v": 100, "n": 3, "vw": c}


def make_rest(settings, handler):
    client = httpx.AsyncClient(base_url="https://data.test", transport=httpx.MockTransport(handler))
    return AlpacaRest(settings, client=client, limiter=RateLimiter(10_000))


async def test_pagination_and_headers(settings):
    calls = []

    def handler(req: httpx.Request):
        calls.append(req)
        assert req.headers["APCA-API-KEY-ID"] == "key"
        assert req.url.params["feed"] == "iex"
        if "page_token" not in req.url.params:
            body = {"bars": {"IREN": [_bar("2026-09-22T13:30:00Z", 10)]}, "next_page_token": "abc"}
        else:
            assert req.url.params["page_token"] == "abc"
            body = {"bars": {"IREN": [_bar("2026-09-22T13:31:00Z", 11)]}, "next_page_token": None}
        return httpx.Response(200, json=body)

    rest = make_rest(settings, handler)
    bars = await rest.get_bars(["IREN"], START, END)
    assert [b.close for b in bars] == [10, 11]
    assert len(calls) == 2
    assert bars[0].feed == "iex"


async def test_retries_on_429_then_succeeds(settings, monkeypatch):
    import app.data.alpaca_rest as mod

    slept = []

    async def fake_sleep(s):
        slept.append(s)

    monkeypatch.setattr(mod.asyncio, "sleep", fake_sleep)
    n = {"i": 0}

    def handler(req):
        n["i"] += 1
        if n["i"] == 1:
            return httpx.Response(429, headers={"Retry-After": "3"})
        return httpx.Response(200, json={"bars": {}, "next_page_token": None})

    rest = make_rest(settings, handler)
    assert await rest.get_bars(["IREN"], START, END) == []
    assert slept[0] == 3.0  # honoured Retry-After (later entries are the drained limiter refilling)


async def test_auth_error_is_raised(settings):
    rest = make_rest(settings, lambda req: httpx.Response(403, text="forbidden"))
    with pytest.raises(AlpacaAuthError):
        await rest.get_bars(["IREN"], START, END)


async def test_crypto_endpoint(settings):
    def handler(req):
        assert req.url.path == "/v1beta3/crypto/us/bars"
        assert "feed" not in req.url.params
        return httpx.Response(200, json={"bars": {"BTC/USD": [_bar("2026-09-22T00:00:00Z", 1)]}})

    rest = make_rest(settings, handler)
    bars = await rest.get_bars(["BTC/USD"], START, END)
    assert bars[0].symbol == "BTC/USD" and bars[0].feed == "crypto"


async def test_mixing_stock_and_crypto_rejected(settings):
    rest = make_rest(settings, lambda req: httpx.Response(200, json={}))
    with pytest.raises(ValueError):
        await rest.get_bars(["IREN", "BTC/USD"], START, END)


async def test_rate_limiter_blocks_when_empty(monkeypatch):
    import app.data.ratelimit as rl

    now = {"t": 0.0}
    waits = []

    async def fake_sleep(s):
        waits.append(s)
        now["t"] += s

    monkeypatch.setattr(rl.asyncio, "sleep", fake_sleep)
    lim = RateLimiter(60, clock=lambda: now["t"])  # 1 token/s
    for _ in range(60):
        await lim.acquire()
    assert waits == []
    await lim.acquire()
    assert waits and waits[0] == pytest.approx(1.0)
