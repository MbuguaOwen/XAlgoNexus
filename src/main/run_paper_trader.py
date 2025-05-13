import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

import asyncio
import logging
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from feature_engineering.feature_engineer import FeatureEngineer
from strategy_core.signal_generator import SignalGenerator
from execution_layer.binance_executor import BinanceExecutor
from filters.ml_filter import MLFilter
from metrics.prometheus_scores import push_scores_to_prometheus
from scoring.scoring_engine import compute_cointegration_score, compute_anomaly_score

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)

# Core pipeline components
engineer = FeatureEngineer()
signal_gen = SignalGenerator()
executor = BinanceExecutor()
ml_filter = MLFilter()

# Virtual account for paper trading
virtual_balance_usd = 50.0
position = 0.0  # net ETHBTC exposure
entry_price = None


def get_utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def log_trade(order, features, signal, confidence):
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/trade_log.csv"
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
         f.write("timestamp,side,price,volume,spread,decision,confidence\n")

    with open(log_file, "a") as f:
        f.write(f"{get_utc_timestamp()},{order['side']},{order['price']},{order['volume']},{features.get('spread')},{signal['decision']},{confidence:.3f}\n")


def log_signal(pair, features, signal, confidence, cointegration_score, anomaly_score, status):
    os.makedirs("logs", exist_ok=True)
    log_file = "logs/signal_log.csv"
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("timestamp,pair,decision,confidence,spread,volatility,imbalance,btc_usd,eth_usd,eth_btc,implied_ethbtc,z_score,cointegration_score,anomaly_score,status\n")
    with open(log_file, "a") as f:
        f.write(f"{get_utc_timestamp()},{pair},{signal},{confidence:.4f},{features.get('spread')},{features.get('volatility')},{features.get('imbalance')},{features.get('btc_usd')},{features.get('eth_usd')},{features.get('eth_btc')},{features.get('implied_ethbtc')},{features.get('z_score')},{cointegration_score:.4f},{anomaly_score:.4f},{status}\n")


def summarize_trades():
    log_file = "logs/trade_log.csv"
    if not os.path.exists(log_file):
        logging.warning("[SUMMARY] No trade log found.")
        return

    df = pd.read_csv(log_file, parse_dates=["timestamp"])
    if df.empty:
        logging.warning("[SUMMARY] Trade log is empty.")
        return

    df = df.sort_values("timestamp")
    df["side_factor"] = df["side"].map({"BUY": 1, "SELL": -1})
    df["return"] = df["spread"] * df["side_factor"]
    df["cum_return"] = df["return"].cumsum()

    sharpe = np.mean(df["return"]) / (np.std(df["return"]) + 1e-9) * np.sqrt(252)

    logging.info("===== SESSION SUMMARY =====")
    logging.info(f"Total Trades:       {len(df)}")
    logging.info(f"Cumulative Return:  {df['cum_return'].iloc[-1]:.6f}")
    logging.info(f"Sharpe Ratio:       {sharpe:.2f}")
    logging.info("============================")

    plt.figure(figsize=(10, 5))
    plt.plot(df["timestamp"], df["cum_return"], label="Equity Curve")
    plt.title("Simulated Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Cumulative Return")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("logs/equity_curve.png")
    plt.close()


def summarize_signals():
    log_file = "logs/signal_log.csv"
    if not os.path.exists(log_file):
        logging.warning("[SIGNAL SUMMARY] No signal log found.")
        return

    df = pd.read_csv(log_file, parse_dates=["timestamp"])
    if df.empty:
        logging.warning("[SIGNAL SUMMARY] Signal log is empty.")
        return

    total = len(df)
    executed = df[df["status"] == "executed"]
    skipped = df[df["status"] == "skipped"]

    logging.info("===== SIGNAL ANALYSIS =====")
    logging.info(f"Total Signals:     {total}")
    logging.info(f"Executed:          {len(executed)}")
    logging.info(f"Skipped:           {len(skipped)}")
    logging.info(f"Execution Rate:    {len(executed)/total*100:.2f}%")
    logging.info(f"Avg Conf (Exec):   {executed['confidence'].mean():.4f}")
    logging.info(f"Avg Conf (Skip):   {skipped['confidence'].mean():.4f}")
    logging.info("============================")

    plt.figure(figsize=(8, 5))
    df.boxplot(column="confidence", by="status", grid=False)
    plt.title("Confidence Distribution by Status")
    plt.suptitle("")
    plt.ylabel("Confidence Score")
    plt.tight_layout()
    plt.savefig("logs/signal_analysis.png")
    plt.close()


async def handle_event(event):
    global virtual_balance_usd, position, entry_price

    if event.event_type != "trade":
        return

    features = engineer.update(event)
    if not features:
        return

    decision = signal_gen.generate_signal(features)
    if not decision or "decision" not in decision:
        logging.warning("[SIGNAL] No decision returned or malformed — skipping.")
        log_signal("ETHBTC", features, "None", 0.0, 0.0, 0.0, "invalid")
        return

    result = ml_filter.predict_with_confidence(features)
    confidence = result["confidence"]
    signal = result["signal"]
    cointegration_score = compute_cointegration_score(features)
    anomaly_score = compute_anomaly_score(features)

    composite_score = push_scores_to_prometheus(confidence, cointegration_score, anomaly_score)
    signal_label = decision["decision"]

    logging.info(f"[ML] Signal={signal_label} | Confidence={confidence:.2f} | Cointegration={cointegration_score:.2f} | Anomaly={anomaly_score:.2f} | Composite={composite_score:.2f}")

    # Simulate trade decision and portfolio update
    if signal_label in ["BUY ETHBTC", "SELL ETHBTC"] and composite_score > 0.8 and confidence > 0.6:
        price = features.get("eth_btc")
        qty = virtual_balance_usd / price if signal_label == "BUY ETHBTC" else position

        order = {
            "side": decision["side"],
            "price": price,
            "volume": qty,
            "pair": "ETHBTC"
        }

        if decision["side"] == "BUY":
            position += qty
            virtual_balance_usd -= qty * price
            entry_price = price
        elif decision["side"] == "SELL" and position > 0:
            virtual_balance_usd += qty * price
            position = 0
            entry_price = None

        log_trade(order, features, decision, confidence)
        log_signal("ETHBTC", features, signal_label, confidence, cointegration_score, anomaly_score, "executed")
        logging.info(f"[PORTFOLIO] Balance: ${virtual_balance_usd:.2f}, Position: {position:.4f} ETHBTC")

    else:
        log_signal("ETHBTC", features, signal_label, confidence, cointegration_score, anomaly_score, "skipped")


async def main_loop():
    from data_pipeline.binance_ingestor import BinanceIngestor
    ingestor = BinanceIngestor(on_trade=handle_event)
    await ingestor.connect_and_listen()


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logging.info("[SYSTEM] Shutdown requested by user.")
    except Exception as e:
        logging.warning(f"[SYSTEM] Runtime terminated with error: {e}")
    finally:
        summarize_trades()
        summarize_signals()
