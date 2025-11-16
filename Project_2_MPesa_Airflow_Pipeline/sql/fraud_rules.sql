-- Fraud Detection Rules for M-Pesa

-- Rule 1: Flag multiple transactions within short time
CREATE VIEW suspicious_rapid_transactions AS
SELECT 
    sender,
    COUNT(*) as transaction_count,
    MAX(amount) as max_amount,
    SUM(amount) as total_amount
FROM transactions
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY sender
HAVING COUNT(*) > 10 OR SUM(amount) > 100000;

-- Rule 2: Flag unusually large transactions
CREATE VIEW suspicious_large_amounts AS
SELECT 
    transaction_id,
    sender,
    receiver,
    amount
FROM transactions
WHERE amount > (SELECT AVG(amount) * 5 FROM transactions)
    AND status = 'success';
