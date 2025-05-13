
import csv
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from data_pipeline.data_normalizer import DataNormalizer
from feature_engineering.feature_engineer import FeatureEngineer
from strategy_core.signal_generator import SignalGenerator
from risk_manager.risk_manager import RiskManager
from execution_layer.execution_router import ExecutionRouter
from execution_layer.pnl_tracker import PnLTracker
from data_pipeline.timescaledb_adapter import TimescaleDBAdapter

logger = logging.getLogger("historical_ingestor")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

db_config = {
    'user': 'postgres',
    'password': '11230428018',
    'database': 'xalgo_trading_db',
    'host': 'timescaledb',
    'port': 5432
}

normalizer = DataNormalizer()
feature_engineer = FeatureEngineer()
signal_generator = SignalGenerator()
risk_manager = RiskManager()
execution_router = ExecutionRouter()
pnl_tracker = PnLTracker()
storage_adapter = TimescaleDBAdapter(db_config)

async def process_row(row):
    try:
        # Simulate event structure
        event = {
            "event_type": "trade",
            "timestamp": datetime.utcfromtimestamp(int(row['time']) / 1000.0),
            "exchange": "binance",
            "pair": "btcusdt",
            "price": float(row['price']),
            "quantity": float(row['qty']),
            "side": "buy" if row['isBuyerMaker'] == 'false' else "sell"
        }

        await storage_adapter.insert_trade_event(event)
        feature = feature_engineer.update(event)
        if feature:
            await storage_adapter.insert_feature_vector(feature)
    except Exception as e:
        logger.error(f"Error processing row: {e}")

async def replay_file():
    await storage_adapter.init_pool()
    file_path = Path("ml_model/data/BTCUSDT-trades-2024-12.csv")
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            await process_row(row)
            await asyncio.sleep(0.001)  # Simulate low-latency streaming

if __name__ == "__main__":
    asyncio.run(replay_file())
