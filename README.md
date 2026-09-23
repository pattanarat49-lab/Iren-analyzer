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
| 2. Indicators + analysis | ✅ done |
| 3. Dashboard UI | ✅ done |
| 4. Probability engine | ✅ done |
| 5. Track record + auto-retrain | ✅ ready for review |
| 6. Hardening + deploy guide | ⏳ next |

---

## Quick start

### 1. Backend (Python)

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

# 3) (after the backfill) train the probability models, a few minutes
python -m scripts.train

# 4) start the server
uvicorn app.main:app --reload --port 8000
```

**No keys yet?** Skip step 1. The server starts in **demo mode** with simulated prices, which are
stored in a separate `data/iren-demo.db`, so you can explore the app immediately.

### 2. Frontend (dashboard)

You need **Node.js 20+**. Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open **http://localhost:3000**, or `http://<your-computer's-IP>:3000` on your phone
when it is on the same Wi-Fi.

### Check the backend API directly
Open these in your browser:

- http://localhost:8000/api/status shows the market session (pre / regular / after-hours /
  closed), server time in US Eastern and Bangkok, the connection mode (`live`, `polling`,
  `demo` or `error`) and recent connection events.
- http://localhost:8000/api/quotes shows the latest price, $ and % change vs previous close,
  bid/ask for IREN, and the halt flag for IREN, CIFR, NBIS, CRWV, NVDA, QQQ and BTC/USD.
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

---

## Dashboard (Phase 3)

A mobile-first, dark-mode layout with Thai UI text. Indicator names stay in English.

- **Header:** live price, $ and % change vs previous close, after-hours change, bid/ask, last
  update in both ET and Bangkok time, market session and connection status (real-time, REST
  fallback, demo, error), plus halt and demo banners.
- **Probability gauge:** Up % vs Down % with a 5 min / 15 min / 1 hour / end-of-day selector.
  It shows no numbers until the Phase 4 model exists; it never shows fake probabilities.
- **Candlestick chart:** 1 / 5 / 15-minute candles with EMA 9/21/50, VWAP and Bollinger
  overlays (toggle each), a volume histogram, and RSI and MACD panes. The live candle updates
  tick by tick. The crosshair readout shows OHLC, RSI and MACD with the time in ET and Bangkok.
- **Panels:** indicator signals with Thai explanations, context tickers (correlation and
  relative strength), and track record (Phase 5).
- **Permanent disclaimer** fixed to the bottom of every screen.
- **Resilience:** the browser WebSocket reconnects with backoff and falls back to REST polling
  every 10 s while the socket is down.

### Chart colours
Line colours come from a colour-vision-deficiency-validated palette on the dark surface:
EMA 9 blue `#3987e5`, EMA 21 orange `#d95926`, EMA 50 aqua `#199e70` and VWAP amber
`#c98500` (dashed). Bullish and bearish badges always pair colour with an icon (▲ ▼ ●) and a
Thai label.

---

## Probability engine (Phase 4)

**Question answered:** at this moment, what is the probability that IREN's last trade price at
the end of the horizon (5 min, 15 min, 1 hour, or the next regular close) is **strictly higher**
than now? P(up) + P(down) = 100%.

```bash
cd backend
python -m scripts.train      # train + save models for all horizons (models/<source>/)
python -m scripts.backtest   # out-of-sample report -> reports/backtest-<source>-<time>.md/.json
```

The running server loads new model files automatically on the next bar.

| Step | How |
|---|---|
| Features | returns over 1/5/15/30/60 min; distance to EMA 9/21/50 and VWAP; RSI; MACD; Bollinger %B and width; ATR; relative volume; volatility regime (30/120-min vol, ATR vs its average); change vs previous close; position in today's range; returns of CIFR, NBIS, CRWV, NVDA, QQQ, BTC over 5/15/60 min and IREN's 15-min relative strength vs each; time of day, day of week, session, minutes to the close |
| Models | logistic regression (baseline) and LightGBM; the one with the lower out-of-sample Brier score is used |
| Validation | expanding-window **walk-forward**: 5 consecutive test blocks over the most recent half of the days. Training rows are **purged by label end time**, so no training label overlaps the test period. Nothing is shuffled |
| Calibration | isotonic regression (Platt scaling when data is small), fitted on the most recent 20% of each training window, purged the same way |
| Baseline | always predict the training window's base rate of "up" |
| Edge rule | the model's Brier score must beat the baseline's with 95% confidence (bootstrap over whole days), accuracy must be higher, and there must be at least 20 test days. Otherwise the dashboard shows **"⚠ ยังไม่พิสูจน์ว่ามีความได้เปรียบ (no proven edge)"** with the reason. It is never hidden |
| Top factors | LightGBM: exact TreeSHAP values. Logistic regression: coefficient × standardised value. Shown in Thai as "ดันให้ขึ้น" and "กดให้ลง" |
| Expected move | ±ATR(14, 1-min) × √minutes (random-walk scaling). For end of day, minutes to the close, capped at one session |

Tests check the labels against hand-computed future prices, that features are causal, that
live-window features match training features, and that walk-forward training never sees a test
label. The pipeline must report **no edge on a pure random walk** and **find the edge when a
momentum signal is planted** in synthetic data, with calibrated probabilities.

> Realistic expectation: for a single stock at short horizons, out-of-sample accuracy is usually
> around 50–54%. "No proven edge" is a common, honest outcome, especially for 5 minutes.

Real and demo models are stored separately (`models/alpaca/` vs `models/demo/`), so models
trained on simulated data can never drive real predictions.

---

## Live track record and nightly retrain (Phase 5)

- **Snapshots:** on every new 1-minute bar the server stores one prediction per horizon in the
  `predictions` table (probability, price, target time, model and training time). A 1-hour
  forecast that would end after the extended session is not logged, the same rule the training
  labels use.
- **Outcomes:** every 30 s, predictions whose target time has passed are scored with exactly
  the training-label definition: the last trade price at the target, from the same trading day.
  If data for the target has not arrived (feed gap, server off) the prediction waits, and after
  3 days it is voided rather than guessed.
- **Track-record page** at http://localhost:3000/track-record, per horizon over 7, 30 or 90 days:
  hit rate and Brier score vs the naive baseline, a calibration chart (predicted vs observed,
  with hover and a table view), daily hit rate, and recent predictions. The live record gets the
  same statistical test as the backtest: it only says "better than the simple guess" when the
  Brier improvement is significant (day-block bootstrap, 95%) over at least 20 days. Nothing is
  filtered or cherry-picked.
- **Nightly retrain:** 30 minutes after each trading day's extended session ends (20:30 ET, or
  17:30 on half days), the server runs `scripts.backfill` (incremental, Alpaca mode only) and
  then `scripts.train` as subprocesses. The live predictor picks up the new models
  automatically. Status and next run time are shown on the track-record page and at
  `/api/models`. Turn it off with `RETRAIN_ENABLED=false`.

API: `GET /api/track-record?days=30`, `GET /api/models`, `GET /api/prediction?horizon=15m`.
