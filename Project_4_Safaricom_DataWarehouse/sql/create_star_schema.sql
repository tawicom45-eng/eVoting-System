-- Execute this file to create the complete star schema

\i dim_customer.sql
\i dim_date.sql
\i fact_transactions.sql

-- Create summary tables for performance
CREATE TABLE IF NOT EXISTS summary_daily_transactions (
    date_id INT REFERENCES dim_date(date_id),
    total_transactions INT,
    total_amount DECIMAL(15, 2),
    total_fee DECIMAL(15, 2),
    successful_transactions INT,
    failed_transactions INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create materialized view for reporting
CREATE MATERIALIZED VIEW mv_transaction_summary AS
SELECT 
    dd.full_date,
    COUNT(ft.transaction_id) as transaction_count,
    SUM(ft.amount) as total_amount,
    AVG(ft.amount) as avg_amount,
    COUNT(CASE WHEN ft.status = 'success' THEN 1 END) as successful_count
FROM fact_transactions ft
JOIN dim_date dd ON ft.date_id = dd.date_id
GROUP BY dd.full_date;
