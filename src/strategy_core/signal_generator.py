import logging
from datetime import datetime

from filters.kalman_spread_estimator import KalmanSpreadEstimator
from filters.ml_filter import MLFilter

# Logger setup
logger = logging.getLogger("signal_generator_v2")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)

class SignalGenerator:
    def __init__(self, zscore_threshold=2.0):
        self.kalman = KalmanSpreadEstimator()
        self.ml_filter = MLFilter(model_path="crypto_feature_framework/models/triangular_rf_model.pkl")
        self.zscore_threshold = zscore_threshold
        self.confidence_threshold = 0.90  # stricter confidence for trading signal

    def generate_signal(self, features):
        if not features:
            logger.warning("[SIGNAL] Feature vector missing.")
            return None

        btc_price = features.get("btc_price")
        eth_price = features.get("eth_price")
        ethbtc_price = features.get("eth_btc")

        if btc_price is None or eth_price is None or ethbtc_price is None:
            logger.warning("[SIGNAL] Missing price data in feature vector.")
            return None

        # 1️⃣ Compute triangular arbitrage metrics
        implied_ethbtc = eth_price / btc_price
        spread = ethbtc_price - implied_ethbtc
        features["implied_ethbtc"] = implied_ethbtc
        features["spread"] = spread

        # 2️⃣ Update Kalman and compute z-score
        self.kalman.update(btc_price, eth_price)
        zscore = self.kalman.get_zscore()
        kalman_params = self.kalman.get_params()
        features["z_score"] = zscore  # for ML

        # 3️⃣ ML prediction with confidence
        ml_result = self.ml_filter.predict_with_confidence({
            "btc_usd": btc_price,
            "eth_usd": eth_price,
            "eth_btc": ethbtc_price,
            "implied_ethbtc": implied_ethbtc,
            "spread": spread,
            "z_score": zscore
        })
        signal = ml_result["signal"]
        confidence = ml_result["confidence"]

        if signal == 0 or confidence < self.confidence_threshold:
            logger.info(
                f"[SIGNAL] ML vetoed or low confidence | signal={signal} | confidence={confidence:.2f} | zscore={zscore:.4f}"
            )
            return {
                "timestamp": features.get("timestamp", datetime.utcnow()),
                "decision": "HOLD",
                "side": None,
                "reason": "ML veto or low confidence",
                "zscore": zscore,
                "confidence": confidence
            }

        # 4️⃣ Rule-based confirmation
        if zscore > self.zscore_threshold:
            decision = "SELL ETHBTC"
            side = "sell"
        elif zscore < -self.zscore_threshold:
            decision = "BUY ETHBTC"
            side = "buy"
        else:
            decision = "HOLD"
            side = None

        logger.info(
            f"[SIGNAL] Decision={decision} | signal={signal} | confidence={confidence:.2f} | "
            f"zscore={zscore:.4f} | spread={spread:.6f} | "
            f"alpha={kalman_params['alpha']:.4f}, beta={kalman_params['beta']:.4f}"
        )

        return {
            "timestamp": features.get("timestamp", datetime.utcnow()),
            "decision": decision,
            "side": side,
            "zscore": zscore,
            "confidence": confidence,
            "spread": spread,
            "implied_ethbtc": implied_ethbtc,
            "kalman_alpha": kalman_params["alpha"],
            "kalman_beta": kalman_params["beta"],
            "btc_price": btc_price,
            "eth_price": eth_price,
            "ethbtc_price": ethbtc_price,
            "volatility": features.get("volatility"),
            "imbalance": features.get("imbalance")
        }
