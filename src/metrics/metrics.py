from prometheus_client import Gauge

# Spread between ETH/BTC (Kalman or statistical spread)
spread_gauge = Gauge('xalgo_latest_spread', 'Latest spread value between ETH and BTC')

# Market volatility estimate
volatility_gauge = Gauge('xalgo_latest_volatility', 'Estimated market volatility')

# Orderbook imbalance indicator
imbalance_gauge = Gauge('xalgo_latest_imbalance', 'Current orderbook imbalance')

# Real-time daily cumulative profit/loss
pnl_gauge = Gauge('xalgo_daily_pnl', 'Daily cumulative PnL (USD)')

# ML model confidence score (from SignalGenerator)
confidence_score = Gauge('xalgo_latest_confidence_score', 'Confidence score from trained ML model')

# Anomaly detection score (IsolationForest or similar)
anomaly_score = Gauge('xalgo_anomaly_score', 'Market anomaly detection score')

# Kalman spread stability score
cointegration_stability_score = Gauge('xalgo_cointegration_stability_score', 'Kalman filter spread stability score')
