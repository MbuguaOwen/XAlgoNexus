import logging
import random
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("execution_router")


class ExecutionRouter:
    """
    Simulates or routes trade executions based on generated signals.
    """
    def __init__(self, slippage_basis_points: float = 5.0, mode: str = "paper"):
        self.slippage_basis_points = slippage_basis_points
        self.mode = mode
        self.orders_executed = []

    def send_order(self, signal: dict, base_price: float, quantity_usd: float):
        if self.mode == "paper":
            return self._simulate_order_execution(signal, base_price, quantity_usd)
        else:
            raise NotImplementedError("Live execution not implemented yet.")

    def _simulate_order_execution(self, signal: dict, base_price: float, quantity_usd: float) -> dict | None:
        if not signal or signal.get("decision", "HOLD") == "HOLD":
            logger.info("[EXECUTION] HOLD signal — execution skipped.")
            return None

        if signal.get("composite_score", 0.0) < 0.85:
            logger.info(f"[EXECUTION] Composite score too low ({signal['composite_score']:.4f}) — execution blocked.")
            return None

        slippage_pct = random.uniform(0, self.slippage_basis_points) / 10000
        direction = signal["decision"].upper()
        fill_price = base_price * (1 + slippage_pct) if "BUY" in direction else base_price * (1 - slippage_pct)

        order = {
            "order_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow(),
            "decision": direction,
            "requested_price": round(base_price, 8),
            "filled_price": round(fill_price, 8),
            "slippage": round(slippage_pct, 8),
            "trade_value_usd": round(quantity_usd, 2),
            "composite_score": round(signal.get("composite_score", 0.0), 4),
            "status": "FILLED"
        }

        self.orders_executed.append(order)
        logger.info(f"[EXECUTION] Order executed: {order}")
        return order

    def get_last_order(self) -> dict | None:
        return self.orders_executed[-1] if self.orders_executed else None
