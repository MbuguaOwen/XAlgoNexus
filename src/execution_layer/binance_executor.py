import os
from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime
from binance.client import Client
from binance.enums import *

# Logger
logger = logging.getLogger("binance_executor")
logging.basicConfig(level=logging.INFO)

class BinanceExecutor:
    def __init__(self, api_key=None, api_secret=None, mode="paper"):
        """
        Args:
            mode: "paper" = testnet, "live" = real Binance
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.mode = mode
        self.client = self._connect()

    def _connect(self):
        if self.mode == "paper":
            logger.info("[BINANCE] Connecting to TESTNET")
            client = Client(self.api_key, self.api_secret, testnet=True)
            client.API_URL = 'https://testnet.binance.vision/api'
        else:
            logger.info("[BINANCE] Connecting to LIVE Binance")
            client = Client(self.api_key, self.api_secret)
        return client

    def send_order(self, pair, side, volume):
        """
        Send a market order to Binance (testnet or live)
        Args:
            pair (str): Symbol like 'ETHBTC'
            side (str): 'buy' or 'sell'
            volume (float): Notional base asset quantity (e.g., ETH units)
        """
        try:
            order = self.client.create_order(
                symbol=pair.upper(),
                side=SIDE_BUY if side.lower() == "buy" else SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=volume
            )
            logger.info(f"[BINANCE] Order Sent: {order}")
            return order
        except Exception as e:
            logger.error(f"[BINANCE] Order Failed: {e}")
            return {"status": "error", "error": str(e), "timestamp": str(datetime.utcnow())}
