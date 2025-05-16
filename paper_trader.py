#!/usr/bin/env python3
"""
Simulated paper trader that reads feature input and runs composite-scored trading logic.
Supports both live streaming (via BinanceIngestor) and CSV playback mode.
"""

import argparse
import logging
import asyncio
import pandas as pd
from strategy_core.signal_generator import SignalGenerator
from execution_layer.execution_router import ExecutionRouter
from execution_layer.pnl_tracker import PnLTracker
from data_pipeline.binance_ingestor import BinanceIngestor

# Optional TimescaleDB (if running full stack)
from data_pipeline.timescaledb_adapter import TimescaleDBAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("paper_trader")

# Setup system components
signal_generator = SignalGenerator()
execution_router = ExecutionRouter()
pnl_tracker = PnLTracker()

db_config = {
    'user': "postgres",
    'password': "11230428018",
    'database': "xalgo_trading_db",
    'host': "localhost",
    'port': 5432
}
storage_adapter = TimescaleDBAdapter(db_config)


async def stream_handler(event):
    feature = event.get("features", {})
    if not feature:
        return

    signal = signal_generator.generate_signal(feature)
    if signal["decision"] in ["BUY ETHBTC", "SELL ETHBTC"]:
        order = execution_router.send_order(signal, base_price=feature["spread"], quantity_usd=1000.0)
        if order:
            pnl_tracker.update_position(signal["decision"], order["filled_price"], order["trade_value_usd"])
            await storage_adapter.insert_execution_order(order)

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
        feature = row.to_dict()
        await stream_handler({"features": feature})
        await asyncio.sleep(0.1)  # simulate pacing


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["stream", "playback"], default="stream")
    parser.add_argument("--csv", type=str, help="CSV path for playback mode")
    args = parser.parse_args()

    if args.mode == "stream":
        asyncio.run(run_stream())
    elif args.mode == "playback":
        if not args.csv:
            logger.error("Playback mode requires --csv path")
        else:
            asyncio.run(run_playback(args.csv))