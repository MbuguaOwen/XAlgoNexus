
from prometheus_client import Gauge

# Spread between ETH/BTC (Kalman or statistical spread)
spread_gauge = Gauge('xalgo_latest_spread', 'Latest spread value between ETH and BTC')

# Market volatility estimate
volatility_gauge = Gauge('xalgo_latest_volatility', 'Estimated market volatility')

# Orderbook imbalance indicator
imbalance_gauge = Gauge('xalgo_latest_imbalance', 'Current orderbook imbalance')

# Real-time daily cumulative profit/loss
pnl_gauge = Gauge('xalgo_daily_pnl', 'Daily cumulative PnL (USD)')
