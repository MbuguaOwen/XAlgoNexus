#!/usr/bin/env python3
"""
Train and export a combined ML filter model for crypto triangular arbitrage signals.
"""

import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

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
        raise FileNotFoundError(f"Training data not found: {path}")
    df = pd.read_csv(path)
    if "label" not in df.columns:
        raise ValueError("Expected 'label' column for supervised training.")
    return df

# -------------------------------
# Train Model
# -------------------------------
def train_model(df):
    X = df.drop(columns=["label", "timestamp"], errors='ignore')
    y = df["label"]

    tscv = TimeSeriesSplit(n_splits=5)
    final_model = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42)

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        final_model.fit(X_train, y_train)
        y_pred = final_model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"[Fold {fold+1}] Accuracy: {acc:.4f}")
        print(classification_report(y_test, y_pred))

    return final_model

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
    model = train_model(df)
    save_model(model)
