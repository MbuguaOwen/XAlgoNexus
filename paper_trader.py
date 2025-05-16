#!/usr/bin/env python3
"""
Simulated paper trader that reads trade data and generates composite ML signals.
Executes trades via the simulated router, logs results to TimescaleDB and CSV.
"""

import argparse
import logging
import asyncio
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from strategy_core.signal_generator import SignalGenerator
from execution_layer.execution_router import ExecutionRouter
from execution_layer.pnl_tracker import PnLTracker
from feature_engineering.feature_engineer import FeatureEngineer
from data_pipeline.binance_ingestor import BinanceIngestor
from data_pipeline.timescaledb_adapter import TimescaleDBAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paper_trader")

# Components
signal_generator = SignalGenerator()
execution_router = ExecutionRouter()
pnl_tracker = PnLTracker()
feature_engineer = FeatureEngineer()

db_config = {
    'user': "postgres",
    'password': "11230428018",
    'database': "xalgo_trading_db",
    'host': "localhost",
    'port': 5432
}
storage_adapter = TimescaleDBAdapter(db_config)

# Trade CSV log
TRADE_LOG_PATH = "ml_model/logs/paper_trade_log.csv"
os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)
trade_log = []

async def stream_handler(event):
    feature = feature_engineer.update(event)
    if not feature:
        return

    signal = signal_generator.generate_signal(feature)
    if signal["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        order = execution_router.send_order(signal, base_price=feature["spread"], quantity_usd=1000.0)
        if order:
            pnl_tracker.update_position(signal["decision"], order["filled_price"], order["trade_value_usd"])
            await storage_adapter.insert_execution_order(order)

            # Log to memory
            record = {
                "timestamp": datetime.utcnow(),
                "decision": signal["decision"],
                "confidence": signal.get("confidence"),
                "composite_score": signal.get("composite_score"),
                "price": order["filled_price"],
                "value": order["trade_value_usd"],
                "slippage": order["slippage"]
            }
            trade_log.append(record)

    pnl = pnl_tracker.get_total_pnl()
    logger.info(f"[PNL] Running PnL = ${pnl:.4f}")

async def run_stream():
    logger.info("[MODE] Starting Binance live stream mode")
    await storage_adapter.init_pool()
    ingestor = BinanceIngestor(process_event_func=stream_handler)
    await ingestor.connect_and_listen()

async def run_playback(csv_path):
    logger.info(f"[MODE] Starting CSV playback mode from {csv_path}")
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        await stream_handler(type("Event", (), row.to_dict()))
        await asyncio.sleep(0.1)

def flush_trade_log():
    if trade_log:
        df = pd.DataFrame(trade_log)
        df.to_csv(TRADE_LOG_PATH, index=False)
        print(f"✅ Trade log saved to: {TRADE_LOG_PATH}")
    else:
        print("⚠️ No trades executed. No file saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["stream", "playback"], default="stream")
    parser.add_argument("--csv", type=str, help="CSV path for playback mode")
    args = parser.parse_args()

    try:
        if args.mode == "stream":
            asyncio.run(run_stream())
        elif args.mode == "playback":
            if not args.csv:
                logger.error("Playback mode requires --csv path")
            else:
                asyncio.run(run_playback(args.csv))
    finally:
        flush_trade_log()