import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

def analyze_signals(log_file="logs/signal_log.csv"):
    if not os.path.exists(log_file):
        logging.warning("No signal log found.")
        return

    df = pd.read_csv(log_file, parse_dates=["timestamp"])
    if df.empty:
        logging.warning("Signal log is empty.")
        return

    total = len(df)
    executed = df[df["status"] == "executed"]
    skipped = df[df["status"] == "skipped"]

    logging.info("===== SIGNAL ANALYSIS REPORT =====")
    logging.info(f"Total Signals:     {total}")
    logging.info(f"Executed:          {len(executed)}")
    logging.info(f"Skipped:           {len(skipped)}")
    logging.info(f"Execution Rate:    {len(executed) / total * 100:.2f}%")
    logging.info(f"Avg Conf (Exec):   {executed['confidence'].mean():.4f}")
    logging.info(f"Avg Conf (Skip):   {skipped['confidence'].mean():.4f}")
    logging.info("==================================")

    # Plot confidence distribution
    plt.figure(figsize=(8, 5))
    df.boxplot(column="confidence", by="status", grid=False)
    plt.title("Confidence Distribution by Status")
    plt.suptitle("")
    plt.ylabel("Confidence Score")
    plt.tight_layout()
    plt.savefig("logs/signal_analysis.png")
    plt.close()

if __name__ == "__main__":
    analyze_signals()
