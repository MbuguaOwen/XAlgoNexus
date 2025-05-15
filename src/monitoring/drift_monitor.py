from prometheus_client import Gauge

# Prometheus Gauges
model_precision_score = Gauge("xalgo_model_precision", "Precision of ML predictions over time")
model_pnl_error = Gauge("xalgo_model_pnl_error", "Prediction PnL delta vs actual")

class DriftMonitor:
    def __init__(self):
        self.total = 0
        self.correct = 0

    def update(self, predicted_signal, actual_outcome, predicted_pnl, actual_pnl):
        self.total += 1
        if predicted_signal == actual_outcome:
            self.correct += 1

        precision = self.correct / self.total if self.total else 0.0
        pnl_error = abs(actual_pnl - predicted_pnl)

        model_precision_score.set(precision)
        model_pnl_error.set(pnl_error)

        return precision, pnl_error