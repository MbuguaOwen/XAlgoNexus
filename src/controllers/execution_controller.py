# /src/controllers/execution_controller.py

from fastapi import APIRouter, HTTPException
from signal_core.signal_generator import SignalGenerator
from execution_layer.binance_executor import BinanceExecutor

router = APIRouter()
signal_gen = SignalGenerator()
executor = BinanceExecutor()  # ✅ Automatically pulls keys + mode from .env

@router.post("/execute")
def generate_and_execute_signal(features: dict):
    decision = signal_gen.generate_signal(features)

    if decision["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        volume = features.get("volume", 0.01)  # default to 0.01 ETH
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
