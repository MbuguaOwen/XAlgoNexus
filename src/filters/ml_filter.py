import numpy as np
import pandas as pd
import joblib
import logging
from prometheus_client import Counter, Gauge
from collections import deque

logger = logging.getLogger("ml_filter")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)

# --- Prometheus metrics ---
prediction_total = Counter("mlfilter_total_predictions", "Total ML predictions")
prediction_correct = Counter("mlfilter_correct_predictions", "Heuristic-correct predictions")

confidence_score_gauge = Gauge("mlfilter_confidence_score", "Confidence score")
anomaly_score_gauge = Gauge("mlfilter_anomaly_score", "Anomaly score")
cointegration_score_gauge = Gauge("mlfilter_cointegration_score", "Cointegration score")
composite_score_gauge = Gauge("mlfilter_composite_score", "Composite fusion score")

# --- KalmanMonitor ---
class KalmanMonitor:
    def __init__(self, window=100):
        self.residuals = deque(maxlen=window)
    def update(self, eth_usd, btc_usd, eth_btc):
        implied = btc_usd * eth_btc
        residual = eth_usd - implied
        self.residuals.append(residual)
    def get_score(self):
        return max(0.0, 1.0 - np.std(self.residuals)) if len(self.residuals) >= 10 else 1.0

# --- MLFilter with fusion ---
class MLFilter:
    def __init__(self,
                 model_path="ml_model/triangular_rf_model.pkl",
                 anomaly_path="ml_model/anomaly_filter.pkl"):
        self.model = None
        self.anomaly_model = None
        self.anomaly_scaler = None
        self.feature_order = [
            "btc_usd", "eth_usd", "eth_btc",
            "implied_ethbtc", "spread", "z_score"
        ]
        self.kalman = KalmanMonitor()
        self._load_model(model_path, anomaly_path)

    def _load_model(self, model_path, anomaly_path):
        try:
            self.model = joblib.load(model_path)
            logger.info(f"[MLFilter] Loaded model from {model_path}")
        except Exception as e:
            logger.warning(f"[MLFilter] Failed to load model: {e}")

        try:
            obj = joblib.load(anomaly_path)
            self.anomaly_model = obj["model"]
            self.anomaly_scaler = obj["scaler"]
            logger.info(f"[MLFilter] Loaded anomaly model from {anomaly_path}")
        except Exception as e:
            logger.warning(f"[MLFilter] Failed to load anomaly model: {e}")

    def predict(self, fv: dict) -> int:
        return self.predict_with_confidence(fv)["signal"]

    def predict_with_confidence(self, fv: dict) -> dict:
        if not self.model:
            logger.warning("[MLFilter] No ML model. Default ALLOW.")
            return {"signal": 1, "confidence": 0.0, "composite": 0.0}

        try:
            # Extract feature input
            X = pd.DataFrame([[fv.get(k, 0.0) for k in self.feature_order]], columns=self.feature_order)
            proba = self.model.predict_proba(X)[0]
            pred = int(np.argmax(proba))
            signal = [-1, 0, 1][pred]
            confidence = float(np.max(proba))
            prediction_total.inc()

            if (signal == 1 and fv.get("spread", 0.0) < 0) or (signal == -1 and fv.get("spread", 0.0) > 0):
                prediction_correct.inc()

            # Anomaly score
            anomaly_score = 1.0
            if self.anomaly_model and self.anomaly_scaler:
                X_scaled = self.anomaly_scaler.transform(X)
                raw = self.anomaly_model.decision_function(X_scaled)[0]
                anomaly_score = 1.0 - (raw - self.anomaly_model.offset_)  # normalize flip

            # Cointegration score
            self.kalman.update(fv.get("eth_usd", 0.0), fv.get("btc_usd", 0.0), fv.get("eth_btc", 0.0))
            cointegration = self.kalman.get_score()

            # Composite score
            composite = 0.4 * confidence + 0.4 * cointegration + 0.2 * (1 - anomaly_score)

            # Push metrics
            confidence_score_gauge.set(confidence)
            anomaly_score_gauge.set(anomaly_score)
            cointegration_score_gauge.set(cointegration)
            composite_score_gauge.set(composite)

            logger.info(f"[MLFilter] Signal={signal} | Conf={confidence:.3f} | Anom={anomaly_score:.3f} | Coin={cointegration:.3f} | Comp={composite:.3f}")
            return {"signal": signal, "confidence": confidence, "composite": composite}

        except Exception as e:
            logger.error(f"[MLFilter] Scoring error: {e}")
            return {"signal": 1, "confidence": 0.0, "composite": 0.0}
