from prometheus_client import Gauge

# Gauges
spread_zscore_gauge = Gauge('xalgo_spread_zscore', 'Live spread Z-score')
volatility_gauge = Gauge('xalgo_volatility_level', 'Live volatility estimate')
pnl_gauge = Gauge('xalgo_pnl_simulated', 'Simulated running PnL')

def update_spread_zscore(value: float):
    spread_zscore_gauge.set(value)

def update_volatility(value: float):
    volatility_gauge.set(value)

def update_pnl(value: float):
    pnl_gauge.set(value)