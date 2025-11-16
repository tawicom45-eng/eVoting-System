-- Customer Dimension Table

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id SERIAL PRIMARY KEY,
    customer_key VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    registration_date DATE,
    account_type VARCHAR(50),
    status VARCHAR(20),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_key ON dim_customer(customer_key);
