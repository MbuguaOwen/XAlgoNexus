#!/usr/bin/env python3
"""
Train and export a combined ML filter model for crypto triangular arbitrage signals.
"""

import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, accuracy_score
from src.utils.download_if_missing import download_file_from_google_drive

# -------------------------------
# Download config
# -------------------------------
btc_file_id = "1SM_Lpngr8FulTj9zF0A655B-IuiGgf3j"
eth_file_id = "1egnWMTphdxtRaa9-BvlXUIO4dQutMPUG"
btc_target = "ml_model/BTCUSD.csv"
eth_target = "ml_model/ETHUSD.csv"

# --- Auto-download large source files if missing ---
download_file_from_google_drive(btc_file_id, btc_target)
download_file_from_google_drive(eth_file_id, eth_target)

# -------------------------------
# Config
# -------------------------------
DATA_PATH = "ml_model/data/features_triangular_full.csv"
MODEL_OUTPUT_PATH = "ml_model/triangular_rf_model.pkl"

# -------------------------------
# Load Data
# -------------------------------
def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        print(f"⚠️ Training data not found: {path}. Skipping model training.")
        return None

    df = pd.read_csv(path)
    if df.empty:
        print("⚠️ Training data is empty.")
        return None

    if "label" not in df.columns:
        print("⚠️ 'label' column missing in training data.")
        return None

    return df

# -------------------------------
# Train Model
# -------------------------------
def train_model(df):
    X = df.drop(columns=["label", "timestamp"], errors='ignore')
    y = df["label"]

    tscv = TimeSeriesSplit(n_splits=5)
    model = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42)

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"[Fold {fold+1}] Accuracy: {acc:.4f}")
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
# Entry Point
# -------------------------------
if __name__ == "__main__":
    df = load_data()
    if df is not None:
        model = train_model(df)
        save_model(model)
    else:
        print("⚠️ No training performed.")
