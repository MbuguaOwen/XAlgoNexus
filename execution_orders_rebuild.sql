-- 📦 Backup current table (optional)
DROP TABLE IF EXISTS execution_orders_backup;
CREATE TABLE execution_orders_backup AS TABLE execution_orders;

-- 💣 Drop the existing table (only if you're sure)
DROP TABLE IF EXISTS execution_orders;

-- 🏗 Recreate with full required schema
CREATE TABLE execution_orders (
    id BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    decision TEXT NOT NULL,
    requested_price DOUBLE PRECISION,
    filled_price DOUBLE PRECISION,
    slippage DOUBLE PRECISION,
    trade_value_usd DOUBLE PRECISION,
    status TEXT NOT NULL,
    pair TEXT,
    side TEXT,
    composite_score DOUBLE PRECISION,
    confidence DOUBLE PRECISION
);

-- 📈 Reapply TimescaleDB hypertable
SELECT create_hypertable('execution_orders', 'timestamp');