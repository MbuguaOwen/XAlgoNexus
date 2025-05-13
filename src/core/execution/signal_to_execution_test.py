
from core.signal.signal_engine import SignalEngine
from filters.ml_filter import MLFilter
from core.execution.execution_engine import ExecutionEngine

# Setup components
signal_engine = SignalEngine(ml_filter=MLFilter())
executor = ExecutionEngine(mode="paper")

# Simulated feature vector input
example_fv = {
    "spread_zscore": 2.7,
    "volatility": 2.0e-6,
    "imbalance": 0.85
}

# Process and act on signals
signal_engine.process(example_fv)

for sig in signal_engine.get_signals():
    executor.execute(sig)
