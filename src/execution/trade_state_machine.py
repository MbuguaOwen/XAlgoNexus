import logging
from prometheus_client import Counter
from execution.execution_safety import ExecutionSafety
from execution.hedge_handler import HedgeHandler

successful_cycles = Counter("xalgo_successful_cycles", "Full triangle trades completed successfully")

class TradeStateMachine:
    def __init__(self, broker):
        self.logger = logging.getLogger("trade_state_machine")
        self.safety = ExecutionSafety()
        self.hedge = HedgeHandler(broker)

    def execute_cycle(self, leg1, leg2, leg3, base_currency):
        self.safety.reset()

        # Step 1: Execute Leg 1
        try:
            result1 = leg1()
            if result1.get("filled"):
                self.safety.update_leg_status(1, True)
        except Exception as e:
            self.logger.error(f"[Leg1] Execution failed: {e}")
            return False

        # Step 2: Execute Leg 2
        try:
            result2 = leg2()
            if result2.get("filled"):
                self.safety.update_leg_status(2, True)
        except Exception as e:
            self.logger.error(f"[Leg2] Execution failed: {e}")
            return self._handle_incomplete_cycle(residual=result1.get("asset"), qty=result1.get("qty"), base=base_currency)

        # Step 3: Execute Leg 3
        try:
            result3 = leg3()
            if result3.get("filled"):
                self.safety.update_leg_status(3, True)
        except Exception as e:
            self.logger.error(f"[Leg3] Execution failed: {e}")
            return self._handle_incomplete_cycle(residual=result2.get("asset"), qty=result2.get("qty"), base=base_currency)

        # Final validation
        if self.safety.is_cycle_complete():
            successful_cycles.inc()
            self.logger.info("[CYCLE] Arbitrage cycle completed successfully.")
            return True
        else:
            self.logger.warning("[CYCLE] Incomplete cycle - fallback hedge triggered.")
            return self._handle_incomplete_cycle(residual=result3.get("asset"), qty=result3.get("qty"), base=base_currency)

    def _handle_incomplete_cycle(self, residual, qty, base):
        self.logger.warning(f"[RECOVERY] Hedging {qty} {residual} → {base}")
        self.hedge.hedge(residual_asset=residual, quantity=qty, base_asset=base)
        return False