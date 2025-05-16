# /ml_model/generate_signal_predictions.py

import pandas as pd
import joblib
import numpy as np
from collections import deque
from xgboost import XGBClassifier

# -------------------------------
# Load ML Models
# -------------------------------
rf_model = joblib.load("ml_model/triangular_rf_model.pkl")
anomaly_data = joblib.load("ml_model/anomaly_filter.pkl")
anomaly_model, scaler = anomaly_data["model"], anomaly_data["scaler"]

# -------------------------------
# Kalman-style Cointegration Monitor
# -------------------------------
class KalmanMonitor:
    def __init__(self, window=100):
        self.residuals = deque(maxlen=window)

    def update(self, eth, btc, ethbtc):
        implied = btc * ethbtc
        residual = eth - implied
        self.residuals.append(residual)

    def get_score(self):
        return max(0.0, 1.0 - np.std(self.residuals)) if len(self.residuals) >= 10 else 1.0

# -------------------------------
# Load Features
# -------------------------------
df = pd.read_csv("ml_model/data/features_triangular_labeled.csv")
X = df.drop(columns=["label"], errors="ignore")

# -------------------------------
# Confidence Scoring
# -------------------------------
proba = rf_model.predict_proba(X)
prediction_raw = proba.argmax(axis=1)
confidence = proba.max(axis=1)

# -------------------------------
# Anomaly Scoring
# -------------------------------
X_scaled = scaler.transform(X)
anomaly_raw = anomaly_model.decision_function(X_scaled)
anomaly_score = 1.0 - (anomaly_raw - anomaly_raw.min()) / (anomaly_raw.max() - anomaly_raw.min())

# -------------------------------
# Cointegration Scoring
# -------------------------------
kalman = KalmanMonitor()
cointegration_score = [
    kalman.update(row["eth_price"], row["btc_price"], row["ethbtc_price"]) or kalman.get_score()
    for _, row in X.iterrows()
]

# -------------------------------
# Composite Scoring
# -------------------------------
def fusion_score(conf, coin, anomaly):
    """Weighted scoring: 40% confidence, 40% cointegration, 20% inverse anomaly."""
    return round(0.4 * conf + 0.4 * coin + 0.2 * (1.0 - anomaly), 4)

composite_score = [
    fusion_score(c, k, a)
    for c, k, a in zip(confidence, cointegration_score, anomaly_score)
]

# -------------------------------
# Final Signal Decision
# -------------------------------
label_map = {0: -1, 1: 0, 2: 1}
mapped_preds = pd.Series(prediction_raw).map(label_map)
filtered = [p if s >= 0.85 else 0 for p, s in zip(mapped_preds, composite_score)]

# -------------------------------
# Output to CSV
# -------------------------------
out_df = pd.DataFrame({
    "timestamp": pd.date_range(start="2022-01-01", periods=len(X), freq="3min"),
    "prediction": filtered,
    "confidence": confidence,
    "anomaly_score": anomaly_score,
    "cointegration_score": cointegration_score,
    "composite_score": composite_score
})

out_path = "ml_model/signal_predictions_full.csv"
out_df.to_csv(out_path, index=False)
print(f"✅ Predictions saved to: {out_path}")
