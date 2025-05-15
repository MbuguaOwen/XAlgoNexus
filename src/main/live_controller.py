# /src/main/live_controller.py

import os
import sys
import time
import asyncio
import logging
import subprocess
import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, start_http_server
from dotenv import load_dotenv

# ----------------------
# Environment & Path Setup
# ----------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
load_dotenv()

# ----------------------
# Logging Setup
# ----------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("live_controller")

# ----------------------
# FastAPI App
# ----------------------
app = FastAPI()

# ----------------------
# Inject Controller Router
# ----------------------
from controllers import execution_controller
app.include_router(execution_controller.router)

# ----------------------
# Internal Imports
# ----------------------
from metrics.metrics import (
    spread_gauge, volatility_gauge, imbalance_gauge, pnl_gauge,
    heartbeat_gauge
)
from data_pipeline.data_normalizer import DataNormalizer
from feature_engineering.feature_engineer import FeatureEngineer
from strategy_core.signal_generator import SignalGenerator
from filters.ml_filter import MLFilter, prediction_total, prediction_correct
from risk_manager.risk_manager import RiskManager
from execution_layer.execution_router import ExecutionRouter
from execution_layer.pnl_tracker import PnLTracker
from data_pipeline.timescaledb_adapter import TimescaleDBAdapter
from metrics.prometheus_scores import push_scores_to_prometheus
from data_pipeline.binance_ingestor import BinanceIngestor

# ----------------------
# Core Component Initialization
# ----------------------
normalizer = DataNormalizer()
feature_engineer = FeatureEngineer()
risk_manager = RiskManager()
execution_router = ExecutionRouter()
pnl_tracker = PnLTracker()

try:
    signal_generator = SignalGenerator()
    ml_filter = MLFilter()
except Exception as e:
    logger.warning(f"[MLFilter] Model initialization failed: {e}")

    class DummySignalGenerator:
        def generate_signal(self, feature):
            logger.warning("[DummySignal] Returning HOLD due to missing model.")
            return {"decision": "HOLD"}

    signal_generator = DummySignalGenerator()
    ml_filter = None

# ----------------------
# Database Adapter
# ----------------------
db_config = {
    'user': os.getenv("POSTGRES_USER", "postgres"),
    'password': os.getenv("POSTGRES_PASSWORD", "11230428018"),
    'database': os.getenv("POSTGRES_DB", "xalgo_trading_db"),
    'host': os.getenv("POSTGRES_HOST", "localhost"),
    'port': int(os.getenv("POSTGRES_PORT", 5432))
}
storage_adapter = TimescaleDBAdapter(db_config)

# ----------------------
# Heartbeat Loop
# ----------------------
def emit_heartbeat():
    heartbeat_gauge.set(time.time())

async def heartbeat_loop():
    while True:
        emit_heartbeat()
        await asyncio.sleep(1)

# ----------------------
# Core Event Processing Logic
# ----------------------
async def process_event(event):
    try:
        if event.event_type == 'trade':
            await storage_adapter.insert_trade_event(event)
        elif event.event_type == 'orderbook':
            await storage_adapter.insert_orderbook_event(event)

        feature = feature_engineer.update(event)
        if feature:
            await storage_adapter.insert_feature_vector(feature)

            spread_gauge.set(feature["spread"])
            volatility_gauge.set(feature["volatility"])
            imbalance_gauge.set(feature["imbalance"])

            signal = signal_generator.generate_signal(feature)

            if signal and signal["decision"] != "HOLD":
                if ml_filter:
                    result = ml_filter.predict_with_confidence(feature)
                    confidence = result["confidence"]
                    prediction = result["signal"]
                    cointegration = 0.0  # Placeholder
                    anomaly = 0.0        # Placeholder
                    composite = push_scores_to_prometheus(confidence, cointegration, anomaly)

                    if prediction != 1 or composite < 0.8:
                        logger.info(f"[MLFilter] Blocked execution | Score={composite:.2f}")
                        return

                base_price = feature["spread"]
                quantity_usd = 1000.0
                slippage = 0.0005

                if risk_manager.check_trade_permission(signal, quantity_usd, slippage):
                    order = execution_router.simulate_order_execution(signal, base_price, quantity_usd)
                    if order:
                        await storage_adapter.insert_execution_order(order)
                        pnl_tracker.update_position(
                            symbol=order['pair'],
                            fill_price=order['filled_price'],
                            qty=order['quantity'],
                            side=order['side']
                        )
                        pnl_tracker.mark_to_market({order['pair']: order['filled_price']})
                        risk_manager.update_pnl(pnl_tracker.get_total_pnl())
                        pnl_gauge.set(risk_manager.daily_pnl)

                        # 🔁 Runtime Drift Detection + Retraining Trigger
                        model_precision = prediction_correct / max(prediction_total, 1)
                        model_pnl_error = abs(pnl_tracker.get_total_pnl() / max(prediction_total, 1))

                        if model_precision < 0.55 or model_pnl_error > 0.002:
                            logger.warning(f"[RETRAINING] Model drift detected — precision={model_precision:.2f}, pnl_error={model_pnl_error:.6f}")
                            subprocess.run(["python", "src/tools/train_ml_filter_combined.py"])

    except Exception as e:
        logger.error(f"[LIVE_CONTROLLER] Event processing failed: {e}")

# ----------------------
# Startup Routine
# ----------------------
async def start_pipeline():
    logger.info("[XALGO] Bootstrapping components...")
    await storage_adapter.init_pool()

    # Run ingestor and heartbeat concurrently
    ingestor = BinanceIngestor(process_event_func=process_event)
    await asyncio.gather(
        ingestor.connect_and_listen(),
        heartbeat_loop()
    )

# ----------------------
# FastAPI Endpoints
# ----------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/pnl")
def get_pnl():
    return pnl_tracker.summary()

@app.get("/drift")
def model_drift_status():
    return JSONResponse({
        "precision": prediction_correct / max(prediction_total, 1),
        "pnl_error": abs(pnl_tracker.get_total_pnl() / max(prediction_total, 1))
    })

@app.on_event("startup")
async def list_routes():
    from fastapi.routing import APIRoute
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"✅ Route: {route.path} [{', '.join(route.methods)}]")

# ----------------------
# Entrypoint
# ----------------------
if __name__ == "__main__":
    start_http_server(9100)
    asyncio.run(start_pipeline())
    uvicorn.run(app, host="0.0.0.0", port=9100)
