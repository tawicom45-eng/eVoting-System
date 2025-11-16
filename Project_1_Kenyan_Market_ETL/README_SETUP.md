# Project 1: Kenyan Market ETL - Setup Guide

## 📋 Project Overview

This project implements a complete ETL (Extract, Transform, Load) pipeline for processing Kenyan market data including prices and quantities of various products across different markets.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, for database storage)
- pip (Python package manager)

### 1. Installation

```bash
# Navigate to project directory
cd Project_1_Kenyan_Market_ETL

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kenyan_market
DB_USER=postgres
DB_PASSWORD=your_password
```

### 3. Running the Pipeline

#### Standard Run (Idempotent Upsert)

```bash
python run_pipeline.py
```

Safely runs multiple times; uses ON CONFLICT to update existing records.

#### Clean Load (Truncate First)

```bash
python run_pipeline.py --truncate
# or
python run_pipeline.py --force
```

Truncates the target table before loading (useful for testing or resetting data).

## 📂 Project Structure

```
Project_1_Kenyan_Market_ETL/
├── etl/                 # ETL modules
│   ├── extract.py      # Data extraction logic
│   ├── transform.py    # Data cleaning & transformation
│   └── load.py         # Data loading to database
├── config/             # Configuration files
│   └── db_config.py    # Database configuration
├── data/               # Sample data
│   └── sample_market_data.csv
├── tests/              # Unit tests
├── sql/                # SQL scripts
│   └── create_tables.sql
├── run_pipeline.py     # Main pipeline script
├── requirements.txt    # Python dependencies
└── .env.example        # Environment configuration template
```

## 🔄 Pipeline Phases

### Phase 1: Extract

- Reads data from CSV files in `data/raw/` and `data/` directories
- Supports multiple file sources
- Returns consolidated dataframe (e.g., 500 rows)

### Phase 2: Transform

- **Standardizes column names** (Market Name → market_name)
- **Deduplicates by key** (market_name, product_name, date_recorded)
  - Aggregates duplicates: avg(price), sum(quantity)
  - Reduces data volume intelligently (500 → 482 records)
- Removes exact duplicates and handles missing values
- Converts dates and currency formats
- Calculates derived fields
- Validates data quality

### Phase 3: Load

- **Idempotent upsert to PostgreSQL** using ON CONFLICT
- Temporary table strategy for batch efficiency
- Graceful fallback to CSV if DB unavailable
- Generates detailed load reports
- Creates CSV backup in `output/` directory

## 📊 Data Model

### market_data Table (PostgreSQL)

```sql
CREATE TABLE market_data (
    id BIGSERIAL PRIMARY KEY,
    market_name TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    date_recorded DATE NOT NULL,
    source_file TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Unique constraint for idempotent loads
ALTER TABLE market_data
    ADD CONSTRAINT market_data_unique_market_product_date
    UNIQUE (market_name, product_name, date_recorded);

-- Performance indexes
CREATE INDEX idx_market_data_market ON market_data (market_name);
CREATE INDEX idx_market_data_product ON market_data (product_name);
CREATE INDEX idx_market_data_date ON market_data (date_recorded);
```

## 🧪 Running Tests

```bash
# Set PYTHONPATH to project root
set PYTHONPATH=%CD%

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_extract.py -v

# Run with coverage
python -m pytest tests/ --cov=etl --cov=config
```

## 📊 Power BI Integration

### Export Snapshot for Power BI

```bash
# Clean temp tables from previous runs
python scripts/cleanup_temp.py

# Run pipeline with truncate for fresh data
python run_pipeline.py --truncate

# Export to CSV snapshot
python scripts/export_powerbi_snapshot.py
# Output: dashboards/powerbi_sample_export.csv
```

### Opening in Power BI Desktop

1. Open Power BI Desktop
2. Get Data → CSV → select `dashboards/powerbi_sample_export.csv`
3. Verify data types: market_name (Text), product_name (Text), price (Decimal), quantity (Whole Number), date_recorded (Date)
4. Create visuals: bar charts, time series, slicers, KPIs
5. Save report to `dashboards/powerbi_dashboard.pbix`

See `dashboards/README_POWERBI.md` for detailed instructions.

## 🛠️ Development

### Code Quality

```bash
# Format code
black etl/ config/ tests/

# Lint code
flake8 etl/ config/

# Run all quality checks
make lint
```

## 📝 Logging

Pipeline logs are automatically saved to `logs/` directory with timestamps:
```
logs/pipeline_20240115_143022.log
```

## 🔍 Troubleshooting

### Database Connection Issues

- Ensure PostgreSQL is running: `psql -U postgres`
- Verify credentials in `.env` file
- Check database exists or create it:

```bash
psql -U postgres -c "CREATE DATABASE kenyan_market;"
```

### Temp Table Errors on Re-Run

If you see "ON CONFLICT" errors, clean temp tables:

```bash
python scripts/cleanup_temp.py
```

### Missing Data Errors

- Ensure sample data exists in `data/` directory
- Check file is named `sample_market_data.csv`
- Verify column names: Market Name, Product Name, Price, Quantity, Date Recorded

### Import Errors

- Set PYTHONPATH: `set PYTHONPATH=%CD%`
- Run `pip install -r requirements.txt` again
- Ensure Python 3.8+

### Power BI Export Returns 0 Rows

- Verify pipeline ran successfully and loaded data
- Check Postgres connection is working: `python scripts/check_count.py`
- Ensure market_data table has rows: `SELECT COUNT(*) FROM market_data;`

## 📚 Utility Scripts

Helper scripts in `scripts/` directory:

- `export_powerbi_snapshot.py` — Export market_data to CSV for Power BI
- `cleanup_temp.py` — Remove temporary tables from failed runs
- `check_count.py` — Verify row counts in database
- `query_db.py` — Query and inspect the SQLite database
- `apply_ddl.py` — Apply schema from sql/create_tables.sql

## 📝 Configuration Reference

### .env Variables

```
DB_TYPE=postgresql          # or sqlite
DB_HOST=localhost
DB_PORT=5432
DB_NAME=kenyan_market
DB_USER=postgres
DB_PASSWORD=your_password
DB_POOL_SIZE=5
LOG_LEVEL=INFO
BATCH_SIZE=1000
```

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Power BI Getting Started](https://docs.microsoft.com/power-bi/)

## 📧 Support

For issues or questions:

1. Check logs in `logs/` directory for detailed error messages
2. Run utility scripts to diagnose:
   - `python scripts/check_count.py` — Verify DB connection
   - `python scripts/cleanup_temp.py` — Clean up temp artifacts
3. Review this guide's Troubleshooting section
