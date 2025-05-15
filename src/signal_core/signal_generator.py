import logging
from datetime import datetime
from filters.kalman_spread_estimator import KalmanSpreadEstimator
from filters.ml_filter import MLFilter
from filters.anomaly_filter import AnomalyFilter
from filters.kalman_monitor import KalmanMonitor
from metrics.metrics import confidence_score, anomaly_score, cointegration_stability_score
from logging.shadow_audit_logger import ShadowAuditLogger  # ✅ Audit logger added

logger = logging.getLogger("signal_generator_v2")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
)

class SignalGenerator:
    def __init__(self, zscore_threshold=2.0, confidence_threshold=0.90):
        self.kalman = KalmanSpreadEstimator()
        self.kalman_monitor = KalmanMonitor()
        self.anomaly_filter = AnomalyFilter()
        self.ml_filter = MLFilter(model_path="crypto_feature_framework/models/triangular_rf_model.pkl")
        self.zscore_threshold = zscore_threshold
        self.confidence_threshold = confidence_threshold
        self.drift_monitor = KalmanMonitor()  # Can be replaced with specialized monitor
        self.audit_logger = ShadowAuditLogger()  # ✅ Initialize shadow audit logger

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

        implied_ethbtc = eth_price / btc_price
        spread = ethbtc_price - implied_ethbtc
        features["implied_ethbtc"] = implied_ethbtc
        features["spread"] = spread

        self.kalman.update(btc_price, eth_price)
        zscore = self.kalman.get_zscore()
        kalman_params = self.kalman.get_params()
        features["z_score"] = zscore

        # ML Filter
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
        confidence_score.set(confidence)

        # Anomaly Score
        anomaly = self.anomaly_filter.get_score(features)
        anomaly_score.set(anomaly)

        # Cointegration Stability Score
        cointegration_stability = self.kalman_monitor.get_score()
        cointegration_stability_score.set(cointegration_stability)

        if signal == 0 or confidence < self.confidence_threshold:
            logger.info(f"[SIGNAL] ML veto or low confidence | signal={signal} | confidence={confidence:.2f} | zscore={zscore:.4f}")
            return {
                "timestamp": features.get("timestamp", datetime.utcnow()),
                "decision": "HOLD",
                "side": None,
                "reason": "ML veto or low confidence",
                "zscore": zscore,
                "confidence": confidence,
                "anomaly": anomaly,
                "cointegration_stability": cointegration_stability
            }

        if anomaly > 0.8 or cointegration_stability < 0.3:
            logger.info(f"[SIGNAL] Blocked due to anomaly={anomaly:.2f} or cointegration_stability={cointegration_stability:.2f}")
            return {
                "timestamp": features.get("timestamp", datetime.utcnow()),
                "decision": "HOLD",
                "side": None,
                "reason": "Market anomaly or unstable cointegration",
                "zscore": zscore,
                "confidence": confidence,
                "anomaly": anomaly,
                "cointegration_stability": cointegration_stability
            }

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
            f"zscore={zscore:.4f} | spread={spread:.6f} | anomaly={anomaly:.2f} | "
            f"cointegration_stability={cointegration_stability:.2f} | "
            f"alpha={kalman_params['alpha']:.4f}, beta={kalman_params['beta']:.4f}"
        )

        signal_output = {
            "timestamp": features.get("timestamp", datetime.utcnow()),
            "decision": decision,
            "side": side,
            "zscore": zscore,
            "confidence": confidence,
            "anomaly": anomaly,
            "cointegration_stability": cointegration_stability,
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

        # ✅ Sample audit usage (dummy outcome + pnl for now)
        self.audit_logger.log(signal_output, actual_outcome=1, actual_pnl=0.0012)

        return signal_output

    def audit_trade(self, signal_output, actual_outcome, actual_pnl):
        expected = signal_output["decision"]
        predicted_signal = 1 if expected == "BUY ETHBTC" else -1 if expected == "SELL ETHBTC" else 0
        predicted_pnl = signal_output.get("confidence", 0.5) * 0.001  # Estimation heuristic

        precision, pnl_error = self.drift_monitor.update(
            predicted_signal=predicted_signal,
            actual_outcome=actual_outcome,
            predicted_pnl=predicted_pnl,
            actual_pnl=actual_pnl
        )
        logger.info(f"[AUDIT] Precision={precision:.2f} | PnL Error={pnl_error:.6f}")
