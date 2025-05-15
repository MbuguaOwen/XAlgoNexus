import logging
from prometheus_client import Counter

hedge_activations = Counter("xalgo_hedge_trades", "Number of emergency hedge trades executed")

class HedgeHandler:
    def __init__(self, broker):
        self.broker = broker  # expects broker.place_order(...)

    def hedge(self, residual_asset: str, quantity: float, base_asset: str):
        logger = logging.getLogger("hedge_handler")
        logger.warning(f"[HEDGE] Initiating hedge: {quantity} {residual_asset} → {base_asset}")

        try:
            result = self.broker.place_order(
                pair=f"{residual_asset}{base_asset}",
                side="SELL",
                amount=quantity,
                order_type="MARKET"
            )
            hedge_activations.inc()
            logger.info(f"[HEDGE] Hedge executed: {result}")
            return result
        except Exception as e:
            logger.error(f"[HEDGE] Failed to hedge: {e}")
            return None