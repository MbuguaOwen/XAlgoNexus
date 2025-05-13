# /src/controllers/execution_controller.py

from fastapi import APIRouter, HTTPException, Request
from signal_core.signal_generator import SignalGenerator
from execution_layer.binance_executor import BinanceExecutor

router = APIRouter()
signal_gen = SignalGenerator()
executor = BinanceExecutor()  # ✅ Uses API keys from .env


@router.post("/trade")
async def trade(request: Request):
    payload = await request.json()
    features = payload.get("features", {})

    if not features:
        raise HTTPException(status_code=422, detail="Missing 'features' in request payload")

    decision = signal_gen.generate_signal(features)

    if decision["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        volume = features.get("volume", 0.01)
        tx = executor.send_order(
            pair="ETHBTC",
            side=decision["side"],
            volume=volume
        )
        return {
            "status": "executed",
            "order_details": tx,
            "signal": decision
        }

    return {
        "status": "no_trade",
        "signal": decision
    }


@router.post("/execute")
def generate_and_execute_signal(features: dict):
    decision = signal_gen.generate_signal(features)

    if decision["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        volume = features.get("volume", 0.01)
        tx = executor.send_order(
            pair="ETHBTC",
            side=decision["side"],
            volume=volume
        )
        return {
            "status": "executed",
            "order_details": tx,
            "signal": decision
        }

    return {
        "status": "no_trade",
        "signal": decision
    }
