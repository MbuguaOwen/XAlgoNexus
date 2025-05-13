# /src/messaging/market_event.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class MarketEvent:
    event_type: str                   # e.g. 'trade' or 'orderbook'
    timestamp: datetime
    exchange: str
    pair: str

    # Optional for trade events
    price: Optional[float] = None
    quantity: Optional[float] = None
    side: Optional[str] = None       # 'buy' or 'sell'

    # Optional for orderbook events
    bids: Optional[str] = None       # JSON or stringified depth data
    asks: Optional[str] = None
