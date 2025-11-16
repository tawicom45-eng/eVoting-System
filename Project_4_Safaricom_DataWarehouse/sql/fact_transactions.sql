-- Transactions Fact Table

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_key VARCHAR(50) UNIQUE NOT NULL,
    sender_id INT REFERENCES dim_customer(customer_id),
    receiver_id INT REFERENCES dim_customer(customer_id),
    date_id INT REFERENCES dim_date(date_id),
    amount DECIMAL(15, 2),
    transaction_type VARCHAR(50),
    status VARCHAR(20),
    fee DECIMAL(10, 2),
    net_amount DECIMAL(15, 2),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sender ON fact_transactions(sender_id);
CREATE INDEX idx_receiver ON fact_transactions(receiver_id);
CREATE INDEX idx_date ON fact_transactions(date_id);
