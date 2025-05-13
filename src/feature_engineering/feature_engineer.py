import numpy as np
import pandas as pd
from collections import deque
import logging
from filters.kalman_spread_estimator import KalmanSpreadEstimator

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("feature_engineer")

class FeatureEngineer:
    """
    Computes real-time engineered features from normalized trade events.
    Supports adaptive spread analysis and basic volatility/imbalance tracking.
    """

    def __init__(self, db_conn=None, maxlen=500):
        self.prices = {
            'btcusdt': deque(maxlen=maxlen),
            'ethusdt': deque(maxlen=maxlen),
            'ethbtc': deque(maxlen=maxlen)
        }
        self.timestamps = deque(maxlen=maxlen)
        self.db_conn = db_conn
        self.kalman = KalmanSpreadEstimator()

    def update(self, event):
        """
        Receives a normalized event and updates internal buffers.
        If sufficient data is present, calculates feature vector.
        """
        if event.event_type != 'trade':
            return None

        pair = event.pair
        if pair not in self.prices:
            return None

        self.prices[pair].append(float(event.price))
        self.timestamps.append(event.timestamp)

        if self.ready():
            fv = self.calculate_features()
            return fv

        return None

    def ready(self):
        """
        Determines if enough data is buffered for feature calculation.
        """
        return all(len(q) > 10 for q in self.prices.values())

    def calculate_features(self):
        """
        Computes Kalman-filtered spread, volatility (as spread std), and synthetic imbalance.
        """
        try:
            btc_usdt = self.prices['btcusdt'][-1]
            eth_usdt = self.prices['ethusdt'][-1]
            eth_btc = self.prices['ethbtc'][-1]

            implied_ethbtc = eth_usdt / btc_usdt
            spread = eth_btc - implied_ethbtc

            # Update Kalman filter
            self.kalman.update(implied_ethbtc, eth_btc)
            zscore = self.kalman.get_zscore()

            imbalance = np.random.uniform(-1, 1)  # 🔄 Replace with real imbalance when available

            feature_vector = {
                "timestamp": self.timestamps[-1],
                "spread": spread,
                "spread_zscore": zscore,
                "volatility": self.kalman.spread_std,
                "imbalance": imbalance
            }

            logger.info(f"[FEATURE_VECTOR] {feature_vector}")
            return feature_vector

        except Exception as e:
            logger.error(f"[FEATURE_CALCULATION_ERROR] {e}")
            return None