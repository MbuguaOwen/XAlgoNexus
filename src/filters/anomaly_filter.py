import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyFilter:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        self.trained = False

    def fit(self, X):
        self.model.fit(X)
        self.trained = True

    def get_score(self, feature_dict):
        if not self.trained:
            return 0.0  # default score before training
        try:
            X = np.array([[feature_dict.get(k, 0.0) for k in sorted(feature_dict.keys())]])
            score = -self.model.decision_function(X)[0]  # negative outlier score
            return min(max(score, 0.0), 1.0)
        except Exception:
            return 0.0