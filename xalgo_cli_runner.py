#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os

# Determine base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# CLI command: Run the live trading pipeline
def run_pipeline():
    subprocess.run(["python", "src/main/live_controller.py"], check=True)

# CLI command: Train the machine learning model
def train_model():
    subprocess.run(["python", "src/tools/train_ml_filter_combined.py"], check=True)

# CLI command: Tail logs for recent activity
def tail_logs():
    print("\n--- SIGNAL LOG ---\n")
    subprocess.run(["tail", "-n", "20", os.path.join(LOG_DIR, "signal_log.csv")], check=False)

    print("\n--- TRADE LOG ---\n")
    subprocess.run(["tail", "-n", "20", os.path.join(LOG_DIR, "trade_log.csv")], check=False)

# CLI command: Run all unit tests
def run_tests():
    if os.path.isdir("tests"):
        subprocess.run(["pytest", "tests/"], check=True)
    else:
        print("⚠️  No tests/ directory found. Skipping tests.")

    

# Entry point
def main():
    parser = argparse.ArgumentParser(description="XAlgoNexus CLI")
    parser.add_argument("command", help="Command to run", choices=["run", "train", "logs", "test"])
    args = parser.parse_args()

    if args.command == "run":
        run_pipeline()
    elif args.command == "train":
        train_model()
    elif args.command == "logs":
        tail_logs()
    elif args.command == "test":
        run_tests()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
