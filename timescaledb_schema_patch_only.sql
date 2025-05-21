
-- 🛠 Apply Hypertables and Indexes Only (Assumes Tables Already Exist)

-- Convert existing tables into hypertables
SELECT create_hypertable('trade_events', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
SELECT create_hypertable('orderbook_events', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
SELECT create_hypertable('feature_vectors', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
SELECT create_hypertable('execution_orders', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);
SELECT create_hypertable('strategy_log', 'timestamp', if_not_exists => TRUE, migrate_data => TRUE);

-- Add valid TimescaleDB-compatible indexes

-- trade_events
CREATE INDEX IF NOT EXISTS idx_trade_events_pair     ON trade_events(timestamp, pair);
CREATE INDEX IF NOT EXISTS idx_trade_events_exchange ON trade_events(timestamp, exchange);

-- orderbook_events
CREATE INDEX IF NOT EXISTS idx_orderbook_events_pair     ON orderbook_events(timestamp, pair);
CREATE INDEX IF NOT EXISTS idx_orderbook_events_exchange ON orderbook_events(timestamp, exchange);

-- feature_vectors
CREATE INDEX IF NOT EXISTS idx_feature_vectors_spread ON feature_vectors(timestamp, spread);

-- execution_orders
CREATE INDEX IF NOT EXISTS idx_execution_orders_order_id ON execution_orders(timestamp, order_id);
