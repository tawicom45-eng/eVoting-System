-- M-Pesa Transactions Table

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    transaction_id UUID UNIQUE NOT NULL,
    sender VARCHAR(20) NOT NULL,
    receiver VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    transaction_type VARCHAR(50),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transaction_id ON transactions(transaction_id);
CREATE INDEX idx_timestamp ON transactions(timestamp);
CREATE INDEX idx_status ON transactions(status);
