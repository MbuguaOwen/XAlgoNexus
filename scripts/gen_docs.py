#!/usr/bin/env python3

"""
gen_docs.py

Generates auto-documentation for the XAlgoNexus project.
Outputs a summary README_AUTO.md file containing CLI commands, Prometheus metrics, and file structure.
"""

import os

README_OUTPUT = "docs/README_AUTO.md"

CLI_COMMANDS = [
    "xalgo run  # Launch real-time pipeline",
    "xalgo train  # Retrain the ML model on recent labeled data",
    "xalgo logs  # Print latest trades and signal logs",
    "xalgo test  # Run all unit tests",
    "xalgo clean  # Clean audit (remove pycache, temp files)"
]

PROMETHEUS_METRICS = [
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

def generate_readme():
    with open(README_OUTPUT, "w") as f:
        f.write("# 📊 XAlgoNexus Auto-Generated README

")

        f.write("## 🚀 CLI Commands
")
        for cmd in CLI_COMMANDS:
            f.write(f"- `{cmd}`
")

        f.write("
## 📈 Prometheus Metrics
")
        for metric in PROMETHEUS_METRICS:
            f.write(f"- `{metric}`
")

        f.write("
## 📁 Project File Structure (Top-Level Only)
")
        for item in sorted(os.listdir(".")):
            if os.path.isdir(item):
                f.write(f"- `/`{item}/
")
            elif os.path.isfile(item):
                f.write(f"- `{item}`
")

    print(f"[INFO] README generated at: {README_OUTPUT}")

if __name__ == "__main__":
    generate_readme()
