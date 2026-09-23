"""Download 1-minute history from Alpaca into the database (resumable).

Usage (from backend/):
    python -m scripts.backfill                 # 2 years (HISTORY_YEARS), all tracked symbols
    python -m scripts.backfill --years 3
    python -m scripts.backfill --symbols IREN,NVDA --feed sip

Re-running only fetches what is missing after the newest stored bar of each symbol.
Symbols that did not trade yet at the start date (e.g. CRWV before its 2025 IPO) simply return
fewer bars; that is expected.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone

from app import db
from app.config import get_settings
from app.data.alpaca_rest import AlpacaAuthError, AlpacaRest, is_crypto

UTC = timezone.utc
CHUNK = timedelta(days=30)


async def backfill_symbol(rest: AlpacaRest, engine, symbol: str, start: datetime, end: datetime, feed: str) -> int:  # noqa: ANN001
    latest = db.latest_bar_ts(engine, symbol)
    if latest and latest + timedelta(minutes=1) > start:
        start = latest + timedelta(minutes=1)
    total = 0
    cur = start
    while cur < end:
        nxt = min(cur + CHUNK, end)
        n = 0
        async for page in rest.iter_bars([symbol], cur, nxt, feed=feed):
            n += await asyncio.to_thread(db.upsert_bars, engine, page)
        total += n
        print(f"  {symbol:8s} {cur:%Y-%m-%d} → {nxt:%Y-%m-%d}: {n:>7,d} bars (total {total:,d})", flush=True)
        cur = nxt
    return total


async def main() -> int:
    s = get_settings()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--years", type=float, default=s.history_years)
    ap.add_argument("--symbols", default=",".join(s.all_symbols))
    ap.add_argument("--feed", choices=["iex", "sip"], default=s.history_feed)
    args = ap.parse_args()

    if not s.has_alpaca_keys:
        print("ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY are not set (see .env.example).", file=sys.stderr)
        return 2

    engine = db.make_engine(s.database_url)
    rest = AlpacaRest(s)
    end = datetime.now(UTC)
    if args.feed == "sip":
        # The free plan only serves SIP data older than 15 minutes.
        end -= timedelta(minutes=16)
    start = end - timedelta(days=365.25 * args.years)
    print(f"Backfilling {args.years}y of 1-min bars ({args.feed} feed) into {s.database_url}")
    grand = 0
    try:
        for sym in [x.strip().upper() for x in args.symbols.split(",") if x.strip()]:
            grand += await backfill_symbol(rest, engine, sym, start, end, "crypto" if is_crypto(sym) else args.feed)
    except AlpacaAuthError as e:
        print(f"\nAlpaca rejected the request: {e}\nCheck your keys, or use --feed iex on the free plan.", file=sys.stderr)
        return 1
    finally:
        await rest.aclose()
    print(f"Done. {grand:,d} bars stored.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
