from fastapi import APIRouter, HTTPException, Request
from strategy_core.signal_generator import SignalGenerator
from execution_layer.execution_router import ExecutionRouter

router = APIRouter()
signal_gen = SignalGenerator()
executor = ExecutionRouter()  # defaults to paper mode


@router.post("/trade")
async def trade(request: Request):
    payload = await request.json()
    features = payload.get("features", {})

    if not features:
        raise HTTPException(status_code=422, detail="Missing 'features' in request payload")

    signal = signal_gen.generate_signal(features)

    if signal["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        base_price = features.get("spread", 1.0)
        quantity_usd = features.get("volume", 1000.0)

        tx = executor.send_order(
            signal=signal,
            base_price=base_price,
            quantity_usd=quantity_usd
        )

        return {
            "status": "executed" if tx else "blocked",
            "order_details": tx,
            "signal": signal
        }

    return {
        "status": "no_trade",
        "signal": signal
    }


@router.post("/execute")
def generate_and_execute_signal(features: dict):
    signal = signal_gen.generate_signal(features)

    if signal["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        base_price = features.get("spread", 1.0)
        quantity_usd = features.get("volume", 1000.0)

        tx = executor.send_order(
            signal=signal,
            base_price=base_price,
            quantity_usd=quantity_usd
        )

        return {
            "status": "executed" if tx else "blocked",
            "order_details": tx,
            "signal": signal
        }

    return {
        "status": "no_trade",
        "signal": signal
    }
