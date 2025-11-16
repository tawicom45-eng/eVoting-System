-- Kenyan Market Tables

-- Primary table to store market product prices per date. The schema matches
-- the CSV fields: Market Name, Product Name, Price, Quantity, Date Recorded
-- Designed for PostgreSQL with a uniqueness constraint to support idempotent loads

CREATE TABLE IF NOT EXISTS market_data (
    id BIGSERIAL PRIMARY KEY,
    market_name TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    date_recorded DATE NOT NULL,
    source_file TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Unique constraint to avoid duplicate rows for same market/product/date
ALTER TABLE market_data
    ADD CONSTRAINT market_data_unique_market_product_date
    UNIQUE (market_name, product_name, date_recorded);

-- Indexes to speed up common queries
CREATE INDEX IF NOT EXISTS idx_market_data_market ON market_data (market_name);
CREATE INDEX IF NOT EXISTS idx_market_data_product ON market_data (product_name);
CREATE INDEX IF NOT EXISTS idx_market_data_date ON market_data (date_recorded);

-- Summary table for quick aggregates (optional, populated by ETL)
CREATE TABLE IF NOT EXISTS market_summary (
    id BIGSERIAL PRIMARY KEY,
    market_name TEXT,
    product_name TEXT,
    date_recorded DATE,
    total_quantity INTEGER,
    average_price NUMERIC(10,2),
    total_revenue NUMERIC(15,2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_market_summary_market_date ON market_summary (market_name, date_recorded);
