from datetime import datetime
from prometheus_client import Counter
from core.execution_layer.pnl_tracker import PnLTracker

# Prometheus metrics
execution_counter = Counter('xalgo_trades_executed_total', 'Total trades executed', ['mode', 'type'])

class ExecutionEngine:
    def __init__(self, mode="paper", logger=None):
        self.mode = mode  # "live" or "paper"
        self.logger = logger or print
        self.trade_log = []
        self.pnl_tracker = PnLTracker()

    def execute(self, signal):
        trade_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": signal.signal_type,
            "reason": signal.reason,
            "metadata": signal.metadata
        }

        execution_counter.labels(mode=self.mode, type=signal.signal_type).inc()

        # Extract trade metadata (required for PnL tracking)
        symbol = signal.metadata.get('pair', 'btcusdt')
        price = signal.metadata.get('price', 0)
        qty = signal.metadata.get('quantity', 0)
        side = signal.metadata.get('side', 'buy')

        self.pnl_tracker.update_position(symbol, price, qty, side)

        if self.mode == "live":
            self.logger(f"[LIVE] Executing: {trade_details}")
        else:
            self.logger(f"[PAPER] Executed: {trade_details}")

        self.trade_log.append(trade_details)

    def get_trade_log(self):
        return self.trade_log

    def get_pnl_summary(self):
        return self.pnl_tracker.summary()