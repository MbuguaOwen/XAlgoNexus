import numpy as np

class KalmanSpreadEstimator:
    def __init__(self, initial_alpha=0.0, initial_beta=1.0, Q=1e-5, R=1e-3):
        self.alpha = initial_alpha
        self.beta = initial_beta
        self.Q = Q
        self.R = R
        self.P = np.eye(2)
        self.state = np.array([self.alpha, self.beta])
        self.last_spread = 0.0
        self.spread_std = 1.0
        self.spread_history = []

    def update(self, x, y):
        phi = np.array([1.0, x])
        y_pred = np.dot(phi, self.state)

        # Kalman gain
        P_phi = self.P @ phi
        S = max(phi @ P_phi + self.R, 1e-8)  # Stability safeguard
        K = P_phi / S

        residual = y - y_pred
        self.state += K * residual

        # Covariance update with symmetry enforcement
        P_new = self.P - np.outer(K, phi) @ self.P + self.Q * np.eye(2)
        self.P = 0.5 * (P_new + P_new.T)

        self.last_spread = residual
        self.spread_history.append(residual)

        if len(self.spread_history) > 200:
            self.spread_history = self.spread_history[-200:]
        self.spread_std = np.std(self.spread_history) or 1.0

        return residual

    def get_zscore(self):
        return self.last_spread / self.spread_std

    def get_params(self):
        return {'alpha': self.state[0], 'beta': self.state[1]}
