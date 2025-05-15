# /metrics/metrics.py

from prometheus_client import Gauge, Counter

# 🔄 Live Market Metrics
spread_gauge = Gauge('xalgo_latest_spread', 'Latest spread value between ETH and BTC')
volatility_gauge = Gauge('xalgo_latest_volatility', 'Estimated market volatility')
imbalance_gauge = Gauge('xalgo_latest_imbalance', 'Current orderbook imbalance')
pnl_gauge = Gauge('xalgo_daily_pnl', 'Daily cumulative PnL (USD)')

# 📈 Model Metrics
confidence_score = Gauge('xalgo_latest_confidence_score', 'Confidence score from trained ML model')
anomaly_score = Gauge('xalgo_anomaly_score', 'Market anomaly detection score')
cointegration_stability_score = Gauge('xalgo_cointegration_stability_score', 'Kalman filter spread stability score')

# 📊 Drift Monitoring
model_precision_score = Gauge("xalgo_model_precision", "Model precision on live trades")
model_pnl_error = Gauge("xalgo_model_pnl_error", "Absolute PnL error on ML predictions")

# 📉 Execution Metrics
hedge_activations = Counter("xalgo_hedge_trades", "Number of emergency hedge trades executed")
successful_cycles = Counter("xalgo_successful_cycles", "Full triangle trades completed successfully")
