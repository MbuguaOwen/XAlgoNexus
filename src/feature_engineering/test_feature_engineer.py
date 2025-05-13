import random
from datetime import datetime
from feature_engineering.feature_engineer import FeatureEngineer

class MockEvent:
    def __init__(self, pair, price):
        self.event_type = 'trade'
        self.pair = pair
        self.price = price
        self.timestamp = datetime.utcnow()

# Initialize
fe = FeatureEngineer()

# Simulate 20 ticks for each pair
btc_prices = [random.uniform(95000, 97000) for _ in range(20)]
eth_prices = [random.uniform(2800, 3200) for _ in range(20)]
ethbtc_prices = [eth / btc for eth, btc in zip(eth_prices, btc_prices)]

for i in range(20):
    fe.update(MockEvent("btcusdt", btc_prices[i]))
    fe.update(MockEvent("ethusdt", eth_prices[i]))
    fe.update(MockEvent("ethbtc", ethbtc_prices[i]))

    feature = fe.update(MockEvent("btcusdt", btc_prices[i]))  # trigger update on final tick
    if feature:
        print("[TEST_FEATURE_VECTOR]", feature)