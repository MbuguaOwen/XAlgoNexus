import asyncio
import websockets
import json
import logging
import time

from data_pipeline.data_normalizer import DataNormalizer
from feature_engineering.feature_engineer import FeatureEngineer
from messaging.market_event import MarketEvent

logger = logging.getLogger("binance_ingestor")
logging.basicConfig(level=logging.INFO)

PAIRS = ["btcusdt", "ethusdt", "ethbtc"]
WS_URL = "wss://stream.binance.com:9443/ws"

def build_subscription():
    streams = [f"{pair}@depth5@100ms" for pair in PAIRS] + [f"{pair}@trade" for pair in PAIRS]
    return {
        "method": "SUBSCRIBE",
        "params": streams,
        "id": int(time.time())
    }

class BinanceIngestor:
    def __init__(self, process_event_func):
        self.process_event_func = process_event_func
        self.feature_engineer = FeatureEngineer()  # Uses internal buffers only

    async def process_event(self, event):
        try:
            # Run external pipeline logic (e.g., from live_controller)
            await self.process_event_func(event)

            # Log internal features (optional diagnostics)
            fv = self.feature_engineer.update(event)
            if fv:
                logger.debug(f"[FEATURES] {fv}")
        except Exception as e:
            logger.exception(f"[BINANCE] Error in event processing: {e}")

    async def handle_message(self, message: dict):
        try:
            if message.get("e") == "trade":
                event = DataNormalizer.normalize_binance_trade(message)
                event.event_type = "trade"
                await self.process_event(event)
                logger.info(f"[TRADE] {event.pair} | Price: {event.price} | Qty: {event.quantity}")

            elif message.get("e") == "depthUpdate":
                event = DataNormalizer.normalize_binance_orderbook(message)
                event.event_type = "orderbook"
                await self.process_event(event)
                logger.info(f"[ORDERBOOK] {event.pair} | Bids: {event.bids[0]} | Asks: {event.asks[0]}")

            else:
                logger.debug(f"[BINANCE] Unknown event: {message}")

        except Exception as e:
            logger.exception(f"[BINANCE] Message handling failed: {e}")

    async def connect_and_listen(self):
        while True:
            try:
                async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=10) as websocket:
                    logger.info("[BINANCE] Connected to stream")
                    await websocket.send(json.dumps(build_subscription()))
                    logger.info("[BINANCE] Subscribed to pairs")

                    while True:
                        raw = await websocket.recv()
                        msg = json.loads(raw)

                        if "e" in msg:
                            await self.handle_message(msg)
                        elif "data" in msg:
                            await self.handle_message(msg["data"])

            except Exception as e:
                logger.warning(f"[BINANCE] Reconnecting in 5s due to: {e}")
                await asyncio.sleep(5)
