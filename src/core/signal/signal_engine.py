from collections import deque
import time
from filters.ml_filter import MLFilter
from prometheus_client import Counter

# Prometheus metrics
signal_counter = Counter('xalgo_signals_emitted_total', 'Total trade signals emitted', ['type'])

class TradeSignal:
    def __init__(self, signal_type, reason, timestamp, metadata=None):
        self.signal_type = signal_type
        self.reason = reason
        self.timestamp = timestamp
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<TradeSignal {self.signal_type} @ {self.timestamp} | {self.reason}>"

class SignalEngine:
    def __init__(self, upper_thresh=2.0, lower_thresh=-2.0, vol_cap=2.5e-6, imbalance_cap=0.8, ml_filter=None):
        self.upper_thresh = upper_thresh
        self.lower_thresh = lower_thresh
        self.vol_cap = vol_cap
        self.imbalance_cap = imbalance_cap
        self.ml_filter = ml_filter or MLFilter()
        self.signal_queue = deque()

    def process(self, fv: dict):
        ts = time.time()
        signals = []

        spread_z = fv.get('spread_zscore', 0)
        volatility = fv.get('volatility', 0)
        imbalance = abs(fv.get('imbalance', 0))

        # Signal generation logic
        if spread_z > self.upper_thresh:
            signals.append(TradeSignal("SHORT_REAL_LONG_SYNTH", "Spread upper bound", ts, fv))
        elif spread_z < self.lower_thresh:
            signals.append(TradeSignal("LONG_REAL_SHORT_SYNTH", "Spread lower bound", ts, fv))

        if imbalance > self.imbalance_cap and volatility < self.vol_cap:
            signals.append(TradeSignal("IMBALANCE_TRADE", "Order book imbalance signal", ts, fv))

        # ML filter override
        if self.ml_filter:
            ml_decision = self.ml_filter.predict(fv)
            if ml_decision != 1:
                print("[SignalEngine] ML filter vetoed signal")
                return
            else:
                signals = [s for s in signals if s.signal_type != "IMBALANCE_TRADE"]

        # Emit signals
        for signal in signals:
            signal_counter.labels(type=signal.signal_type).inc()
            self.signal_queue.append(signal)
            print(f"[SignalEngine] Emitted: {signal}")

    def get_signals(self):
        while self.signal_queue:
            yield self.signal_queue.popleft()