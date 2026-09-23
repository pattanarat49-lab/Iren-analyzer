# IREN Probability Analyzer: Plan (Phase 0)

This is the pre-coding proposal. No application code gets written until the data provider
and stack below are approved.

---

## 1. Market-data provider

Requirements: real-time US stock data over WebSocket (not 15-min delayed), extended hours,
2+ years of 1-minute history for IREN, CRWV, NBIS, NVDA and QQQ, and BTC-USD.

| | **Alpaca** (recommended) | **Massive** (formerly Polygon.io) | **Finnhub** |
|---|---|---|---|
| Real-time stock WebSocket | Free: IEX exchange only. $99/mo *Algo Trader Plus*: full SIP (all exchanges) | Only on *Advanced* at **$199/mo**. Starter ($29) and Developer ($79) are 15-min delayed | Free WebSocket trades, up to 50 symbols |
| Intraday history | 1-min bars back to 2016, **free** (SIP history is free if older than 15 min) | 5 yr on Starter, 10 yr on Developer, 20+ yr on Advanced | Free tier: about 1 yr of intraday. More history on paid plans from about $50/mo per market |
| REST rate limit | 200 req/min free, 10,000 req/min paid | Unlimited on paid plans | 60 req/min free |
| BTC-USD | Real-time crypto WebSocket, free | Separate crypto plan | Crypto is limited on the free tier |
| Pre/after-hours | Yes | Yes | Partial |
| Cost to get started | **$0** | $199/mo for real-time | $0, but history is too short |

### Recommendation: Alpaca
- **Start on the free Basic plan ($0).** Live trades and 1-min bars come from IEX in real time.
  2+ years of full-market (SIP) 1-min history for training is free, and BTC/USD streams free.
- **Known limitation of the free plan:** IEX carries only a few percent of US volume. Price is
  accurate, but live **volume, VWAP and relative volume** are IEX-only numbers and will not match
  the consolidated tape. To keep training and live features consistent, the app will either
  (a) compute volume features from IEX in both training and live, or (b) switch to SIP
  everywhere once you upgrade. The UI will label which feed is active.
- **Upgrade path:** Algo Trader Plus at $99/mo gives full SIP real-time data. It's a single
  `.env` change (`ALPACA_STOCK_FEED=sip`). No code changes.
- **Optional:** add a free Finnhub key later as a polling fallback and for news/analyst sentiment.

### Data caveats for the peer tickers
- **CRWV** (CoreWeave) listed in **March 2025** and has only about 1.5 years of history.
- **NBIS** (Nebius) resumed trading in **October 2024** after a long halt.
- The models handle this. LightGBM treats missing peer features as NaN natively. Logistic
  regression gets imputed values plus an "available" flag. IREN, NVDA, QQQ and BTC cover the
  full 2+ years.

---

## 2. Proposed stack

```
Browser (Next.js, Thai UI) ──HTTPS/WS──▶ FastAPI backend ──WS/REST──▶ Alpaca
                                           │  (holds API keys)
                                           ├─ SQLite (default) / Postgres
                                           ├─ indicator engine (pandas/numpy)
                                           ├─ models: LogisticRegression + LightGBM,
                                           │          isotonic/Platt calibration, SHAP
                                           └─ scheduler: 1-min snapshots, outcome fill,
                                                         nightly retrain after close
```

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind, TradingView Lightweight Charts,
  dark mode, mobile-first, Thai text (indicator names stay in English).
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy + APScheduler. pandas/numpy for indicators,
  scikit-learn + LightGBM + SHAP for models, pytest for tests.
- **Security:** API keys live only in `backend/.env`. The browser talks only to our backend,
  which relays live data over its own WebSocket.
- **DB:** SQLite in WAL mode for local use (zero setup). Set `DATABASE_URL` to use Postgres.
- **Deploy:** frontend on Vercel. The backend needs a long-running process for the WebSocket,
  so it goes on Railway, Fly.io or Render (with a persistent volume) or a small VPS.
- **Times:** everything is stored in UTC and displayed in both US/Eastern and Asia/Bangkok
  (UTC+7, no DST). Market sessions follow the NYSE calendar via `pandas_market_calendars`,
  which covers holidays and half days.

---

## 3. Definitions (to avoid ambiguity later)

- **Up** means the last trade price at `t + horizon` is strictly greater than the price at `t`.
  Down is its complement, so P(up) + P(down) = 100%.
- **Horizons:** 5 min, 15 min and 1 h are measured in trading-time bars within the session.
  **End of day** means the next regular-session close (16:00 ET, or 13:00 on half days). Before
  the open or in after-hours, EOD refers to the next session's close.
- **Naive baseline:** always predict the training-window base rate of "up". Its accuracy is
  the majority-class rate, and its Brier score is the base rate's. The model must beat this
  out of sample, or the UI shows **"no proven edge"**.
- **Validation:** expanding-window walk-forward with a purge/embargo gap equal to the horizon,
  so labels never overlap the test fold. Calibration is fit on a held-out slice inside each
  training window only.

> **Expectation setting:** short-horizon direction for a single stock is close to a coin flip.
> Realistic out-of-sample accuracy is about 50–54%, and the 5-minute horizon may well show "no
> proven edge". The app is built to surface that honestly, not to hide it.

---

## 4. Phases (pause for review after each)

| Phase | Scope | Deliverable to review |
|---|---|---|
| **0** | Provider + stack proposal, repo scaffolding | this document |
| **1** | Live data layer: Alpaca WS stream (auto-reconnect, REST polling fallback), BTC stream, 1-min bar aggregation, DB schema, session detector (pre/regular/after/closed, halts), ET + Bangkok time, 2-year history backfill script | backend streaming live bars to a `/ws` endpoint, bars persisted |
| **2** | Indicator engine (EMA 9/21/50, VWAP, RSI14, MACD 12/26/9, BB 20/2, ATR14, RVOL), signals + Thai explanations, rolling correlation / relative strength vs peers, **unit tests** | `/api/analysis` JSON + passing tests |
| **3** | Frontend dashboard: live price/change/session, candlestick chart with overlays + RSI/MACD panes, indicator + context panels, Thai UI, dark/mobile, permanent disclaimer | runnable UI on live data |
| **4** | Probability engine: features, walk-forward CV, LR + LightGBM, calibration, accuracy/Brier vs baseline, "no proven edge" flag, SHAP top factors, ATR expected-move range, **backtest report script** | gauge wired to models + backtest report |
| **5** | Prediction logging every minute per horizon, outcome back-fill, track-record page (hit rate + calibration chart), automatic nightly retrain | track-record page |
| **6** | Hardening (rate limits, halts, missing data), README with beginner setup + deploy guide, optional news/analyst sentiment feature | final review |
