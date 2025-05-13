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
    os.makedirs(os.path.dirname(README_OUTPUT), exist_ok=True)

    with open(README_OUTPUT, "w") as f:
        f.write("# 📊 XAlgoNexus Auto-Generated README\n\n")

        f.write("## 🚀 CLI Commands\n")
        for cmd in CLI_COMMANDS:
            f.write(f"- `{cmd}`\n")

        f.write("\n## 📈 Prometheus Metrics\n")
        for metric in PROMETHEUS_METRICS:
            f.write(f"- `{metric}`\n")

        f.write("\n## 📁 Project File Structure (Top-Level Only)\n")
        for item in sorted(os.listdir(".")):
            if os.path.isdir(item):
                f.write(f"- `/`{item}/\n")
            elif os.path.isfile(item):
                f.write(f"- `{item}`\n")

    print(f"[INFO] README generated at: {README_OUTPUT}")

if __name__ == "__main__":
    generate_readme()
