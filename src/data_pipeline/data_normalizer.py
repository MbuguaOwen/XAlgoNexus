# /src/data_pipeline/data_normalizer.py

import logging
from datetime import datetime

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("data_normalizer")


class NormalizedEvent:
    """
    Represents a normalized market event, such as a trade or order book snapshot,
    ready for feature engineering or database insertion.
    """

    def __init__(self, timestamp, exchange, event_type, pair, price, quantity,
                 side=None, bids=None, asks=None):
        self.timestamp = timestamp
        self.exchange = exchange
        self.event_type = event_type  # 'trade' or 'orderbook'
        self.pair = pair
        self.price = price
        self.quantity = quantity
        self.side = side
        self.bids = bids
        self.asks = asks

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "exchange": self.exchange,
            "event_type": self.event_type,
            "pair": self.pair,
            "price": self.price,
            "quantity": self.quantity,
            "side": self.side,
            "bids": self.bids,
            "asks": self.asks
        }


class DataNormalizer:
    """
    Static utility class to normalize raw Binance WebSocket messages into
    XAlgo's internal event schema.
    """

    @staticmethod
    def normalize_binance_trade(msg: dict) -> NormalizedEvent:
        """
        Normalize Binance trade event payload.

        Example input:
        {
          'e': 'trade', 'E': 123456789, 's': 'BTCUSDT',
          't': 12345, 'p': '0.001', 'q': '100', 'b': 88, 'a': 50,
          'T': 123456785, 'm': True, 'M': True
        }
        """
        return NormalizedEvent(
            timestamp=datetime.utcfromtimestamp(msg['T'] / 1000),
            exchange="binance",
            event_type="trade",
            pair=msg['s'].lower(),
            price=float(msg['p']),
            quantity=float(msg['q']),
            side='sell' if msg['m'] else 'buy'
        )

    @staticmethod
    def normalize_binance_orderbook(msg: dict) -> NormalizedEvent:
        """
        Normalize Binance depthUpdate (L2 orderbook) event payload.

        Example input:
        {
          'e': 'depthUpdate', 'E': 123456789, 's': 'BTCUSDT',
          'U': 157, 'u': 160, 'b': [['0.0024', '10']], 'a': [['0.0026', '100']]
        }
        """
        return NormalizedEvent(
            timestamp=datetime.utcfromtimestamp(msg['E'] / 1000),
            exchange="binance",
            event_type="orderbook",
            pair=msg['s'].lower(),
            price=None,
            quantity=None,
            bids=msg.get('b', []),
            asks=msg.get('a', [])
        )


if __name__ == "__main__":
    logger.info("[XALGO] Binance Data Normalizer Ready.")
