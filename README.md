# IREN Probability Analyzer

A real-time analysis dashboard for **IREN Limited (NASDAQ: IREN)**. It estimates the probability
that the price will be higher or lower after a chosen horizon (5 min, 15 min, 1 h, end of day),
with calibrated probabilities and a live track record.

> ⚠️ เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำทางการเงิน ความน่าจะเป็นเป็นเพียงการประมาณการ ไม่ใช่การรับประกัน
> (For education only. Not financial advice. Probabilities are estimates, not guarantees.)

See [`docs/PLAN.md`](docs/PLAN.md) for the data-provider comparison, the stack and the roadmap.

| Phase | Status |
|---|---|
| 0. Plan | ✅ done |
| 1. Live data layer (backend) | ✅ done |
| 2. Indicators + analysis | ✅ ready for review |
| 3. Dashboard UI | ⏳ next |
| 4. Probability engine | — |
| 5. Track record + auto-retrain | — |
| 6. Hardening + deploy guide | — |

---

## Quick start (backend, Phase 1)

You need **Python 3.11+**. On Windows, use `py` instead of `python3` and
`.venv\Scripts\activate` instead of `source .venv/bin/activate`.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 1) Put your keys in backend/.env (never commit this file)
cp ../.env.example .env
#    then edit .env and fill in ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY

# 2) (optional, takes a while) download 2 years of 1-minute history
python -m scripts.backfill

# 3) start the server
uvicorn app.main:app --reload --port 8000
```

**No keys yet?** Skip step 1. The server starts in **demo mode** with simulated prices, which are
stored in a separate `data/iren-demo.db`, so you can explore the app immediately.

### Check that it works
Open these in your browser:

- http://localhost:8000/api/status shows the market session (pre / regular / after-hours /
  closed), server time in US Eastern and Bangkok, the connection mode (`live`, `polling`,
  `demo` or `error`) and recent connection events.
- http://localhost:8000/api/quotes shows the latest price, $ and % change vs previous close,
  bid/ask for IREN, and the halt flag for IREN, CRWV, NBIS, NVDA, QQQ and BTC/USD.
- http://localhost:8000/api/bars?symbol=IREN&limit=100 shows stored 1-minute bars.
- http://localhost:8000/api/analysis shows every indicator with its value, a bullish / bearish /
  neutral signal and a one-sentence Thai explanation, plus correlation and relative strength vs
  the context tickers. Add `?tf=5` or `?tf=15` for 5- or 15-minute bars.
- http://localhost:8000/api/chart?symbol=IREN&tf=1&limit=500 shows candles plus
  EMA/VWAP/Bollinger/RSI/MACD series for the chart.
- `ws://localhost:8000/ws` is the live event stream the dashboard will use.

### Run the tests
```bash
cd backend && pytest
```

---

## How the live data layer works

```
Alpaca WebSocket (stocks: /v2/iex, crypto: /v1beta3/crypto/us)
   │  trades, IREN quotes, 1-min bars, corrected bars, trading status (halts)
   ▼
MarketHub ── stores completed 1-min bars ──▶ SQLite (data/iren.db) or Postgres
   │        keeps last price, change vs prev close, bid/ask, halt flag, forming candle
   ├── REST polling fallback every 10 s while the WebSocket is down
   ├── gap fill after reconnecting (fetches any bars missed while offline)
   ├── snapshot refresh every 60 s (previous close, latest trade)
   └──▶ /ws broadcast to the browser (keys never leave the server)
```

- **Auto-reconnect** uses exponential backoff with jitter (1 s up to 60 s). Bad keys (error
  402) back off for 5 minutes instead of hammering the server.
- **Silent-socket watchdog:** during regular hours, if nothing arrives for 90 s the socket is
  recycled.
- **Rate limits:** a token bucket keeps REST calls under 180/min (the free plan allows 200).
  A 429 response honours `Retry-After`.
- **Trading halts** are detected from Alpaca's status channel (H/P/Q codes). If that channel
  isn't in your plan, a heuristic flags "no trades for 5 min during regular hours".
- **Times** are stored in UTC and shown in both US/Eastern and Asia/Bangkok. Sessions follow
  the NYSE calendar, including holidays and half days.

### Free (IEX) vs paid (SIP) feed
The free plan streams IEX-exchange trades only, so live **volume, VWAP and relative volume**
cover just part of the market. Prices are accurate. Set `ALPACA_STOCK_FEED=sip` after
upgrading to Algo Trader Plus.

---

## Indicators (Phase 2)

Computed on 1-minute bars (or 5/15-minute bars via `?tf=`). The analysis is recomputed on every
new bar and pushed over `/ws` as an `analysis` event.

| Indicator | Definition | Signal rule |
|---|---|---|
| EMA 9 / 21 / 50 | EMA seeded with SMA (TradingView convention) | price above → bullish, below → bearish, within 0.05% → neutral. Also flags 9/21 crosses and the 9 > 21 > 50 stack |
| VWAP | typical price × volume, reset each US/Eastern day (pre-market included) | above → bullish, below → bearish |
| RSI(14) | Wilder smoothing | ≥70 overbought → bearish; ≤30 oversold → bullish; 55–70 bullish; 30–45 bearish; otherwise neutral |
| MACD(12,26,9) | EMA12 − EMA26, signal EMA9 | recent cross or widening histogram → that direction; shrinking histogram → neutral |
| Bollinger(20,2) | SMA20 ± 2σ (population) | above upper → bearish (stretched); below lower → bullish; upper/lower half → bullish/bearish; also flags squeezes |
| ATR(14) | Wilder smoothing of True Range | always neutral (size of moves, not direction); compared with its recent average |
| Relative volume | cumulative volume today ÷ average at the same time of day over the prior 20 days | ≥1.5× confirms the day's direction; ≤0.7× low participation |
| Correlation / RS | 1-min log-return correlation (60 and 390 bars), beta, performance vs previous close | IREN outperforming by more than 0.5% → bullish, underperforming → bearish |

All indicators are **causal**: a test checks that computing on a prefix of the data gives
identical values, so there is no look-ahead. RSI is verified against StockCharts' published
example table.
