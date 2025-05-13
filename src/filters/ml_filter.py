import numpy as np
import joblib
import logging
from prometheus_client import Counter

# ----------------------
# Logger setup
# ----------------------
logger = logging.getLogger("ml_filter")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)

# ----------------------
# Prometheus metrics
# ----------------------
prediction_total = Counter(
    "mlfilter_total_predictions", "Total number of ML filter predictions"
)
prediction_correct = Counter(
    "mlfilter_correct_predictions", "Heuristic-correct predictions by ML filter"
)

# ----------------------
# ML Filter Class
# ----------------------
class MLFilter:
    def __init__(self, model_path="crypto_feature_framework/models/triangular_rf_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_order = [
            "btc_usd", "eth_usd", "eth_btc",
            "implied_ethbtc", "spread", "z_score"
        ]
        self._load_model()

    def _load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            logger.info(f"[MLFilter] Loaded model from {self.model_path}")
        except Exception as e:
            logger.warning(f"[MLFilter] Failed to load model: {e}")
            self.model = None

    def predict(self, fv: dict) -> int:
        result = self.predict_with_confidence(fv)
        return result["signal"]

    def predict_with_confidence(self, fv: dict) -> dict:
        """
        Returns:
            {
                'signal': int,        # -1, 0, or 1
                'confidence': float   # 0.0 to 1.0
            }
        """
        if not self.model:
            logger.warning("[MLFilter] Model unavailable. Defaulting to ALLOW.")
            return {"signal": 1, "confidence": 0.0}

        try:
            features = self.extract_features(fv)
            logger.debug(f"[MLFilter] Feature Vector: {features}")

            proba = self.model.predict_proba([features])[0]
            logger.debug(f"[MLFilter] Prediction Probabilities: {proba}")

            prediction = int(np.argmax(proba))
            signal = [-1, 0, 1][prediction]

            prediction_total.inc()

            if (signal == 1 and fv.get("spread", 0.0) < 0) or \
               (signal == -1 and fv.get("spread", 0.0) > 0):
                prediction_correct.inc()

            confidence = float(np.max(proba))
            logger.info(f"[MLFilter] Signal: {signal} | Confidence: {confidence:.4f}")
            return {"signal": signal, "confidence": confidence}

        except Exception as e:
            logger.error(f"[MLFilter] Prediction error: {e}")
            return {"signal": 1, "confidence": 0.0}

    def extract_features(self, fv: dict) -> np.ndarray:
        try:
            features = np.array([fv.get(key, 0.0) for key in self.feature_order])
            return features
        except Exception as e:
            logger.error(f"[MLFilter] Feature extraction error: {e}")
            return np.zeros(len(self.feature_order))
