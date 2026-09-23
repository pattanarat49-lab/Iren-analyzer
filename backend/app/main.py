"""FastAPI entry point: `uvicorn app.main:app --reload` (run from backend/)."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from . import db
from .analysis.engine import TIMEFRAMES, AnalysisEngine
from .config import get_settings
from .data.alpaca_rest import AlpacaRest
from .data.demo import run_demo
from .data.hub import MarketHub, run_alpaca
from .market.clock import dual_time, session_at
from .model.features import HORIZONS
from .model.predictor import Predictor, model_dir
from .model.scheduler import Retrainer
from .model.tracking import resolve_due, track_record

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("iren")
UTC = timezone.utc


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    engine = db.make_engine(s.effective_database_url)
    rest = AlpacaRest(s) if s.resolved_source == "alpaca" else None
    hub = MarketHub(s, engine, rest)
    analysis = AnalysisEngine(hub)
    primary = s.primary_symbol.upper()
    analysis.predictor = Predictor(model_dir(s.models_dir, s.resolved_source), primary, [x for x in s.all_symbols if x != primary])
    await asyncio.to_thread(analysis.predictor.load)
    await analysis.reload_async()
    hub.add_bar_listener(analysis.on_bar)
    hub.history_listeners.append(analysis.reload_async)
    app.state.hub = hub
    app.state.analysis = analysis
    retrainer = Retrainer(s, engine)
    app.state.retrainer = retrainer
    hub.start_task(_resolve_loop(hub))
    if s.retrain_enabled:
        hub.start_task(retrainer.loop())
    log.info("data source: %s (feed=%s)", s.resolved_source, s.alpaca_stock_feed)
    if s.resolved_source == "alpaca":
        hub.start_task(run_alpaca(hub))
    else:
        hub.start_task(run_demo(hub))
    hub.start_task(_clock_loop(hub))
    try:
        yield
    finally:
        await hub.stop()
        if rest:
            await rest.aclose()
        engine.dispose()


async def _resolve_loop(hub: MarketHub) -> None:
    """Fill in outcomes of past predictions as their horizons pass."""
    while True:
        try:
            counts = await asyncio.to_thread(resolve_due, hub.engine, hub.s.primary_symbol.upper())
            if counts["resolved"] or counts["void"]:
                log.info("track record: %s", counts)
                hub.broadcast({"type": "track_record_updated", "counts": counts})
        except Exception:  # noqa: BLE001
            log.exception("resolving predictions failed")
        await asyncio.sleep(30)


async def _clock_loop(hub: MarketHub) -> None:
    """Push the market session + server clock to clients every 15 s."""
    while True:
        now = datetime.now(UTC)
        hub.broadcast({"type": "clock", "server_time": dual_time(now), "market": session_at(now).to_dict()})
        await asyncio.sleep(15)


app = FastAPI(title="IREN Probability Analyzer", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in get_settings().cors_origins.split(",") if o.strip()],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def _hub() -> MarketHub:
    return app.state.hub


def _analysis() -> AnalysisEngine:
    return app.state.analysis


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.get("/api/status")
def status() -> dict:
    hub = _hub()
    snap = hub.snapshot()
    snap["events"] = [
        {**e, "ts": dual_time(e["ts"].replace(tzinfo=UTC))} for e in db.recent_events(hub.engine, 20)
    ]
    return snap


@app.get("/api/quotes")
def quotes() -> dict:
    return {s: st.to_json() for s, st in _hub().state.items()}


@app.get("/api/bars")
def bars(symbol: str = Query(..., examples=["IREN", "BTC/USD"]), limit: int = Query(500, ge=1, le=5000)) -> dict:
    hub = _hub()
    symbol = symbol.upper()
    if symbol not in hub.state:
        raise HTTPException(404, f"unknown symbol {symbol}; tracked: {list(hub.state)}")
    rows = db.load_bars(hub.engine, symbol, limit=limit)
    return {"symbol": symbol, "bars": [b.to_json() for b in rows]}


@app.get("/api/analysis")
async def analysis(tf: int = Query(1, description="bar size in minutes: 1, 5 or 15")) -> dict:
    if tf not in TIMEFRAMES:
        raise HTTPException(400, f"tf must be one of {TIMEFRAMES}")
    eng = _analysis()
    if tf == 1 and 1 in eng.latest:
        return eng.latest[1]
    return await eng.compute_async(tf)


@app.get("/api/prediction")
async def prediction(horizon: str | None = Query(None, description="5m, 15m, 1h or eod; omit for all")) -> dict:
    eng = _analysis()
    if eng.prediction is None:
        await eng.update_prediction()
    pred = eng.prediction or {"available": False, "horizons": {}}
    if horizon is None:
        return pred
    if horizon not in HORIZONS:
        raise HTTPException(400, f"horizon must be one of {list(HORIZONS)}")
    return {**{k: v for k, v in pred.items() if k != "horizons"}, **(pred.get("horizons") or {}).get(horizon, {})}


@app.get("/api/models")
def models() -> dict:
    p = _analysis().predictor
    return {
        "source": get_settings().resolved_source,
        "retrain": app.state.retrainer.status(),
        "horizons": p.summary() if p else {},
    }


@app.get("/api/track-record")
def track_record_api(days: int = Query(30, ge=1, le=365)) -> dict:
    hub = _hub()
    rec = track_record(hub.engine, hub.s.resolved_source, days)
    rec["retrain"] = app.state.retrainer.status()
    return rec


@app.get("/api/chart")
async def chart(
    symbol: str = Query("IREN"),
    tf: int = Query(1),
    limit: int = Query(500, ge=10, le=5000),
) -> dict:
    symbol = symbol.upper()
    if tf not in TIMEFRAMES:
        raise HTTPException(400, f"tf must be one of {TIMEFRAMES}")
    if symbol not in _hub().state:
        raise HTTPException(404, f"unknown symbol {symbol}")
    return await _analysis().chart_async(symbol, tf, limit)


@app.websocket("/ws")
async def ws(websocket: WebSocket) -> None:
    await websocket.accept()
    hub = _hub()
    q = hub.subscribe()
    try:
        await websocket.send_json(hub.snapshot())
        latest = app.state.analysis.latest.get(1)
        if latest:
            await websocket.send_json({"type": "analysis", "analysis": latest})
        if app.state.analysis.prediction:
            await websocket.send_json({"type": "prediction", "prediction": app.state.analysis.prediction})
        while True:
            event = await q.get()
            await websocket.send_json(event)
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        hub.unsubscribe(q)
