import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque

# Rolling buffer for residuals
residual_buffer = deque(maxlen=200)

# Basic anomaly model (can be extended to batch training)
anomaly_model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
anomaly_window = deque(maxlen=200)

def compute_cointegration_score(features: dict) -> float:
    """
    Measures how well ETHBTC tracks its implied value (ETH/USDT divided by BTC/USDT).
    Lower residual variance = higher stability score.
    """
    try:
        eth_btc = features.get("eth_btc", None)
        implied_ethbtc = features.get("implied_ethbtc", None)

        if eth_btc is None or implied_ethbtc is None:
            return 0.0

        residual = abs(eth_btc - implied_ethbtc)
        residual_buffer.append(residual)

        if len(residual_buffer) < residual_buffer.maxlen:
            return 0.5  # warming up

        std_residual = np.std(residual_buffer)
        return float(np.clip(1 - std_residual * 100, 0.0, 1.0))

    except Exception:
        return 0.0

def compute_anomaly_score(features: dict) -> float:
    """
    Applies IsolationForest to detect rare/abnormal feature vectors.
    Returns a score between 0.0 (normal) to 1.0 (highly anomalous).
    """
    try:
        vector = np.array([
            features.get("spread", 0.0),
            features.get("spread_zscore", 0.0),
            features.get("volatility", 0.0),
            features.get("imbalance", 0.0)
        ])
        anomaly_window.append(vector)

        if len(anomaly_window) < anomaly_window.maxlen:
            return 0.5  # warming up

        X = np.array(anomaly_window)
        anomaly_model.fit(X)
        score = anomaly_model.decision_function([vector])[0]  # higher = more normal
        return float(np.clip(1 - score, 0.0, 1.0))

    except Exception:
        return 0.5
