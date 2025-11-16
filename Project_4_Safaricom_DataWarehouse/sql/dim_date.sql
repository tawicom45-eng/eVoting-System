-- Date Dimension Table

CREATE TABLE IF NOT EXISTS dim_date (
    date_id SERIAL PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INT,
    month INT,
    day INT,
    quarter INT,
    week_of_year INT,
    day_of_week VARCHAR(10),
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

CREATE INDEX idx_full_date ON dim_date(full_date);
