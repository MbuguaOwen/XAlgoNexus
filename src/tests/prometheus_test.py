#!/usr/bin/env python3

"""
prometheus_test.py

Validates the Prometheus metrics endpoint used in the XAlgo Nexus trading system.
Ensures all expected metrics are present and properly formatted.
"""

import requests

EXPECTED_METRICS = [
    "xalgo_latest_spread",
    "xalgo_latest_volatility",
    "xalgo_latest_imbalance",
    "xalgo_daily_pnl",
    "xalgo_confidence_score",
    "xalgo_cointegration_score",
    "xalgo_anomaly_score",
    "xalgo_composite_score",
    "mlfilter_total_predictions",
    "mlfilter_correct_predictions"
]

PROMETHEUS_ENDPOINT = "http://localhost:9100/metrics"

def fetch_metrics():
    try:
        response = requests.get(PROMETHEUS_ENDPOINT, timeout=3)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ERROR] Failed to reach Prometheus metrics endpoint: {e}")
        return None

def validate_metrics(metrics_text):
    missing = []
    for metric in EXPECTED_METRICS:
        if metric not in metrics_text:
            missing.append(metric)
    return missing

def main():
    print("[INFO] Validating Prometheus metrics...")
    metrics_text = fetch_metrics()
    if metrics_text is None:
        print("[FAIL] Could not fetch Prometheus metrics.")
        exit(1)

    missing = validate_metrics(metrics_text)
    if missing:
        print(f"[FAIL] Missing metrics: {missing}")
        exit(1)

    print("[PASS] All expected Prometheus metrics are present.")

if __name__ == "__main__":
    main()
