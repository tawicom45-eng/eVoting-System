# Data Dictionary - Safaricom Data Warehouse

## Fact Table: fact_transactions

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | SERIAL | Unique transaction identifier |
| transaction_key | VARCHAR(50) | Business key for transaction |
| sender_id | INT | Foreign key to dim_customer |
| receiver_id | INT | Foreign key to dim_customer |
| date_id | INT | Foreign key to dim_date |
| amount | DECIMAL(15,2) | Transaction amount |
| transaction_type | VARCHAR(50) | Type of transaction (transfer, withdrawal, deposit) |
| status | VARCHAR(20) | Status (success, failed, pending) |
| fee | DECIMAL(10,2) | Transaction fee |
| net_amount | DECIMAL(15,2) | Amount after fee |

## Dimension Table: dim_customer

| Column | Type | Description |
|--------|------|-------------|
| customer_id | SERIAL | Unique customer identifier |
| customer_key | VARCHAR(50) | Business key for customer |
| customer_name | VARCHAR(255) | Customer full name |
| phone_number | VARCHAR(20) | Customer phone |
| email | VARCHAR(255) | Customer email |
| registration_date | DATE | Account creation date |
| account_type | VARCHAR(50) | Type of account |
| status | VARCHAR(20) | Current status |

## Dimension Table: dim_date

| Column | Type | Description |
|--------|------|-------------|
| date_id | SERIAL | Unique date identifier |
| full_date | DATE | Calendar date |
| year | INT | Year |
| month | INT | Month |
| day | INT | Day of month |
| quarter | INT | Quarter |
| week_of_year | INT | Week number |
| day_of_week | VARCHAR(10) | Day name |
| is_weekend | BOOLEAN | Weekend flag |
| is_holiday | BOOLEAN | Holiday flag |
