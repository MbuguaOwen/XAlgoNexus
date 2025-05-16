#!/usr/bin/env python3
"""
Train and export a composite ML model for crypto triangular arbitrage filtering.
Uses features from confidence, anomaly, and cointegration metrics.
"""

import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, accuracy_score

# -------------------------------
# Config
# -------------------------------
DATA_PATH = "ml_model/data/features_triangular_labeled.csv"
MODEL_OUTPUT_PATH = "ml_model/triangular_rf_model.pkl"

# -------------------------------
# Basic Fallback Labeling
# -------------------------------
def apply_basic_labels(df, threshold=0.0005):
    df["label"] = 0
    df.loc[df["spread"] > threshold, "label"] = -1
    df.loc[df["spread"] < -threshold, "label"] = 1
    print("⚠️ Fallback labels applied using spread threshold.")
    return df

# -------------------------------
# Load Labeled Dataset
# -------------------------------
def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        print(f"❌ File missing: {path}")
        return None

    df = pd.read_csv(path)
    if df.empty:
        print("❌ Dataset is empty.")
        return None

    if "label" not in df.columns:
        print("⚠️ No label found. Trying fallback...")
        if "spread" not in df.columns:
            print("❌ Missing 'spread' column. Cannot label.")
            return None
        df = apply_basic_labels(df)

    return df

# -------------------------------
# Train Model with Composite Features
# -------------------------------
def train_model(df):
    # Select inference-safe feature columns
    feature_cols = [
        "btc_usd", "eth_usd", "eth_btc",
        "implied_ethbtc", "spread", "z_score",
        "confidence_score", "cointegration_stability_score", "anomaly_score"
    ]

    if not all(col in df.columns for col in feature_cols):
        missing = [col for col in feature_cols if col not in df.columns]
        print(f"❌ Missing required features: {missing}")
        return None

    X = df[feature_cols]
    y = df["label"]

    model = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42)
    tscv = TimeSeriesSplit(n_splits=5)

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        print(f"[Fold {fold + 1}] Accuracy: {acc:.4f}")
        print(classification_report(y_test, y_pred))

    return model

# -------------------------------
# Save Model
# -------------------------------
def save_model(model, path=MODEL_OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"✅ Model saved to: {path}")

# -------------------------------
# Main Entrypoint
# -------------------------------
if __name__ == "__main__":
    df = load_data()
    if df is not None:
        model = train_model(df)
        if model:
            save_model(model)
    else:
        print("⚠️ Training aborted — data invalid or missing.")
