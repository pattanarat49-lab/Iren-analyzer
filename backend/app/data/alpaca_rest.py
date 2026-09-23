"""Alpaca Market Data REST client: historical bars, latest bars and snapshots.

Handles pagination, the per-minute rate limit (429 + Retry-After), transient 5xx errors and
clear errors for bad keys / insufficient subscription.
"""

from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import AsyncIterator
from datetime import datetime

import httpx

from ..config import Settings
from ..models import Bar, parse_ts, to_utc
from .ratelimit import RateLimiter

log = logging.getLogger(__name__)


class AlpacaError(RuntimeError):
    pass


class AlpacaAuthError(AlpacaError):
    """401/403: wrong keys, or the plan does not include the requested feed (e.g. recent SIP)."""


def is_crypto(symbol: str) -> bool:
    return "/" in symbol


def parse_bar(symbol: str, d: dict, feed: str) -> Bar:
    return Bar(
        symbol=symbol,
        ts=parse_ts(d["t"]),
        open=float(d["o"]),
        high=float(d["h"]),
        low=float(d["l"]),
        close=float(d["c"]),
        volume=float(d.get("v") or 0.0),
        vwap=float(d["vw"]) if d.get("vw") is not None else None,
        trade_count=int(d["n"]) if d.get("n") is not None else None,
        feed=feed,
    )


def _iso(ts: datetime) -> str:
    return to_utc(ts).isoformat().replace("+00:00", "Z")


class AlpacaRest:
    def __init__(
        self,
        settings: Settings,
        *,
        client: httpx.AsyncClient | None = None,
        limiter: RateLimiter | None = None,
        max_retries: int = 5,
    ) -> None:
        self.s = settings
        self._client = client or httpx.AsyncClient(base_url=settings.alpaca_data_url, timeout=30.0)
        self._limiter = limiter or RateLimiter(settings.alpaca_rest_rpm)
        self._max_retries = max_retries

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict | None = None) -> dict:
        headers = {
            "APCA-API-KEY-ID": self.s.alpaca_api_key_id,
            "APCA-API-SECRET-KEY": self.s.alpaca_api_secret_key,
        }
        delay = 1.0
        for attempt in range(self._max_retries + 1):
            await self._limiter.acquire()
            try:
                r = await self._client.get(path, params=params, headers=headers)
            except httpx.TransportError as e:
                if attempt == self._max_retries:
                    raise AlpacaError(f"network error on {path}: {e}") from e
                log.warning("network error on %s (%s); retrying in %.1fs", path, e, delay)
                await asyncio.sleep(delay + random.random())
                delay = min(delay * 2, 30)
                continue

            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                self._limiter.drain()
                wait = _retry_after(r) or delay
                log.warning("rate limited on %s; waiting %.1fs", path, wait)
                await asyncio.sleep(wait)
                delay = min(delay * 2, 60)
                continue
            if r.status_code in (401, 403):
                raise AlpacaAuthError(f"{r.status_code} on {path}: {r.text[:200]}")
            if r.status_code >= 500 and attempt < self._max_retries:
                log.warning("%s on %s; retrying in %.1fs", r.status_code, path, delay)
                await asyncio.sleep(delay + random.random())
                delay = min(delay * 2, 30)
                continue
            raise AlpacaError(f"{r.status_code} on {path}: {r.text[:200]}")
        raise AlpacaError(f"giving up on {path} after {self._max_retries} retries")

    # ---- historical bars -------------------------------------------------------------------

    async def iter_bars(
        self,
        symbols: list[str],
        start: datetime,
        end: datetime,
        *,
        timeframe: str = "1Min",
        feed: str | None = None,
    ) -> AsyncIterator[list[Bar]]:
        """Yield pages of bars for stock symbols or crypto symbols (not mixed)."""
        if not symbols:
            return
        crypto = is_crypto(symbols[0])
        if any(is_crypto(s) != crypto for s in symbols):
            raise ValueError("do not mix stock and crypto symbols in one request")

        feed = feed or self.s.history_feed
        if crypto:
            path, tag = "/v1beta3/crypto/us/bars", "crypto"
            params = {"symbols": ",".join(symbols), "timeframe": timeframe}
        else:
            path, tag = "/v2/stocks/bars", feed
            params = {
                "symbols": ",".join(symbols),
                "timeframe": timeframe,
                "feed": feed,
                "adjustment": "split",
            }
        params.update({"start": _iso(start), "end": _iso(end), "limit": 10000, "sort": "asc"})

        token: str | None = None
        while True:
            p = dict(params)
            if token:
                p["page_token"] = token
            data = await self._get(path, p)
            page: list[Bar] = []
            for sym, rows in (data.get("bars") or {}).items():
                page.extend(parse_bar(sym, row, tag) for row in rows or [])
            if page:
                yield page
            token = data.get("next_page_token")
            if not token:
                break

    async def get_bars(self, symbols: list[str], start: datetime, end: datetime, **kw) -> list[Bar]:
        out: list[Bar] = []
        async for page in self.iter_bars(symbols, start, end, **kw):
            out.extend(page)
        return out

    # ---- latest / snapshots ----------------------------------------------------------------

    async def latest_bars(self, symbols: list[str]) -> list[Bar]:
        stocks = [s for s in symbols if not is_crypto(s)]
        cryptos = [s for s in symbols if is_crypto(s)]
        out: list[Bar] = []
        if stocks:
            feed = self.s.alpaca_stock_feed
            data = await self._get("/v2/stocks/bars/latest", {"symbols": ",".join(stocks), "feed": feed})
            out += [parse_bar(sym, d, feed) for sym, d in (data.get("bars") or {}).items()]
        if cryptos:
            data = await self._get("/v1beta3/crypto/us/latest/bars", {"symbols": ",".join(cryptos)})
            out += [parse_bar(sym, d, "crypto") for sym, d in (data.get("bars") or {}).items()]
        return out

    async def snapshots(self, symbols: list[str]) -> dict[str, dict]:
        """Raw snapshots keyed by symbol: latestTrade, latestQuote, minuteBar, dailyBar, prevDailyBar."""
        stocks = [s for s in symbols if not is_crypto(s)]
        cryptos = [s for s in symbols if is_crypto(s)]
        out: dict[str, dict] = {}
        if stocks:
            data = await self._get(
                "/v2/stocks/snapshots", {"symbols": ",".join(stocks), "feed": self.s.alpaca_stock_feed}
            )
            out.update({k: v for k, v in data.items() if isinstance(v, dict)})
        if cryptos:
            data = await self._get("/v1beta3/crypto/us/snapshots", {"symbols": ",".join(cryptos)})
            out.update(data.get("snapshots") or {})
        return out


def _retry_after(r: httpx.Response) -> float | None:
    v = r.headers.get("Retry-After")
    if v:
        try:
            return max(1.0, float(v))
        except ValueError:
            return None
    reset = r.headers.get("X-RateLimit-Reset")
    if reset:
        try:
            import time

            return max(1.0, float(reset) - time.time())
        except ValueError:
            return None
    return None
