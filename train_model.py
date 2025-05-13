
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

# Load triangular features file (assume large-scale version)
df = pd.read_csv("ml_model/features_triangular_full.csv")

# Apply labeling (simple z-score thresholding for now)
threshold = 1.0
def label_z(z):
    if z > threshold:
        return -1
    elif z < -threshold:
        return 1
    else:
        return 0

df["label"] = df["z_score"].apply(label_z)

# Feature selection
features = [
    "btc_usd", "eth_usd", "eth_btc",
    "implied_ethbtc", "spread", "z_score"
]
X = df[features]
y = df["label"]

# Time-aware train/test split (80/20)
split_idx = int(0.8 * len(df))
X_train, X_test = X[:split_idx], X[split_idx:]
y_train, y_test = y[:split_idx], y[split_idx:]

# Train the model
clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
clf.fit(X_train, y_train)

# Evaluation
y_pred = clf.predict(X_test)
print("[REPORT]")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(clf, "crypto_feature_framework/models/triangular_rf_model.pkl")
print("✅ Model saved to crypto_feature_framework/models/triangular_rf_model.pkl")
