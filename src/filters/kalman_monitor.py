import numpy as np
from collections import deque

class KalmanMonitor:
    def __init__(self, window=100):
        self.residuals = deque(maxlen=window)

    def update(self, residual):
        self.residuals.append(residual)

    def get_score(self):
        if len(self.residuals) < 5:
            return 1.0  # assume stable
        std = np.std(self.residuals)
        return max(0.0, 1.0 - std)