-- 📦 Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ─────────────────────────────────────────────
-- 🟦 Table: trade_events (Raw Trades)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trade_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    exchange TEXT NOT NULL,
    pair TEXT NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    side TEXT NOT NULL
);
SELECT create_hypertable('trade_events', 'timestamp', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_trade_events_pair     ON trade_events(timestamp, pair);
CREATE INDEX IF NOT EXISTS idx_trade_events_exchange ON trade_events(timestamp, exchange);

-- ─────────────────────────────────────────────
-- 🟩 Table: orderbook_events (Level 2 Snapshots)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orderbook_events (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    exchange TEXT NOT NULL,
    pair TEXT NOT NULL,
    bids TEXT,  -- Stored as JSON string or comma-delimited
    asks TEXT
);
SELECT create_hypertable('orderbook_events', 'timestamp', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_orderbook_events_pair     ON orderbook_events(timestamp, pair);
CREATE INDEX IF NOT EXISTS idx_orderbook_events_exchange ON orderbook_events(timestamp, exchange);

-- ─────────────────────────────────────────────
-- 🟨 Table: feature_vectors (ML Engineered Features)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feature_vectors (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    spread DOUBLE PRECISION,
    volatility DOUBLE PRECISION,
    imbalance DOUBLE PRECISION
);
SELECT create_hypertable('feature_vectors', 'timestamp', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_feature_vectors_spread ON feature_vectors(timestamp, spread);

-- ─────────────────────────────────────────────
-- 🟥 Table: execution_orders (Order Execution Logs)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS execution_orders (
    id BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    decision TEXT NOT NULL,
    requested_price DOUBLE PRECISION,
    filled_price DOUBLE PRECISION,
    slippage DOUBLE PRECISION,
    trade_value_usd DOUBLE PRECISION,
    status TEXT NOT NULL,
    pair TEXT,                     -- 📌 Added
    side TEXT,                     -- 📌 Added
    composite_score DOUBLE PRECISION, -- 📌 Added
    confidence DOUBLE PRECISION       -- 📌 Added
);
SELECT create_hypertable('execution_orders', 'timestamp', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_execution_orders_order_id ON execution_orders(timestamp, order_id);

-- ✅ Schema Notes:
-- - All timestamp fields are indexed & hypertable-optimized.
-- - `execution_orders` includes composite score + confidence for ML analysis.
-- - `bids` and `asks` assumed to be stored as serialized JSON/text for flexibility.
-- - Schema is forward-compatible with Prometheus-based pipeline auditing.
