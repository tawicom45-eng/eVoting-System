# Project 1: Kenyan Market ETL Pipeline

## Overview

This project demonstrates a **production-ready ETL (Extract, Transform, Load) pipeline** for processing **Kenyan agricultural market data** used by traders, distributors, and agribusiness platforms. The pipeline extracts market prices from multiple sources, deduplicates and aggregates by market/product/date, and loads into PostgreSQL for reporting and analytics.

**Business Context:** Kenyan markets (Nairobi, Mombasa, Kisumu) report daily prices for crops (maize, tomatoes, beans). Duplicate entries occur due to multiple reporting sources. The system ensures accurate market intelligence for price discovery and supply chain optimization.

**Status:** ✅ 38 tests passing | 0 warnings | Python 3.8-3.11 support | GitHub Actions CI/CD

**Performance:** Processes 500 raw records → 482 aggregated records in ~2.5 seconds (~200 records/sec)

## Key Features

- ✅ **Intelligent Deduplication**: Automatically detects and aggregates duplicate market/product/date entries (500 → 482 records)
- ✅ **Idempotent Upserts**: PostgreSQL ON CONFLICT strategy for safe re-runs without data duplication
- ✅ **Data Transformation**: Standardization, cleaning, validation with type coercion
- ✅ **Batch Processing**: Efficient loading of large datasets with configurable batch sizes
- ✅ **Power BI Integration**: Export snapshot-ready CSV for visualization
- ✅ **Clean Load Option**: `--truncate` flag for testing and resets
- ✅ **Error Handling**: CSV fallback, null handling, infinite value detection, comprehensive logging
- ✅ **Comprehensive Testing**: 38 unit tests covering edge cases (empty data, nulls, infinite values)
- ✅ **CI/CD Pipeline**: GitHub Actions with code quality checks (Black, isort, mypy)

## 🎯 Interview Talking Points

### 1. Idempotent Loading (Most Important!)

**The Problem:** Running the pipeline twice loads data twice = corrupted analytics

**The Solution:** PostgreSQL `ON CONFLICT (market_name, product_name, date_recorded) DO UPDATE` clause ensures:

- First run: Inserts 482 records
- Second run: Updates same 482 records (no duplication!)
- Safe to deploy in production and schedule daily without data validation

**Why This Matters:** Shows understanding of production data pipelines and idempotency patterns

### 2. Smart Deduplication

**Logic:** When duplicate (market, product, date) is found:

- Combine quantities: `SUM(quantity)`
- Keep first occurrence of other columns
- Result: 500 raw records → 482 aggregated (18 duplicates found)

**Why This Matters:** Shows ETL transformation thinking and handling real-world dirty data

### 3. Comprehensive Test Coverage

**Tests Included:**

- 14 deduplication tests (nulls, case-sensitivity, edge cases)
- 3 extract tests (CSV parsing, error handling)
- 18 load tests (type coercion, constraint management, batch processing)
- 3 transform tests (column standardization, empty data)

**Why This Matters:** Demonstrates quality mindset and TDD practices

### 4. Error Handling at Scale

```python
# Handles edge cases that break pipelines:
- NaN in price column → Coerced to float
- Infinite values → Removed from dataset
- Missing required columns → Exception with clear message
- Type mismatches → Automatic coercion with logging
```

**Why This Matters:** Shows production-readiness and debugging skills

### 5. CI/CD & Code Quality

- GitHub Actions runs on Python 3.8, 3.9, 3.10, 3.11
- Linting: flake8 (style), mypy (types)
- Formatting: Black (code style), isort (imports)
- Coverage: pytest-cov tracks code coverage

**Why This Matters:** Modern DevOps practices and team collaboration mindset

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Tests (All 38 Passing)

```bash
pytest -v
```

### Run Pipeline (Idempotent - Safe to Re-run)

```bash
python run_pipeline.py
```

### Run Pipeline (Clean Load - Truncates First)

```bash
python run_pipeline.py --truncate
```

### Export for Power BI

```bash
python scripts/export_powerbi_snapshot.py
# Output: dashboards/powerbi_sample_export.csv
```

## Project Structure

- `etl/`: ETL pipeline modules (extract, transform, load)
- `config/`: Database configuration and connection pooling
- `sql/`: SQL schemas and DDL
- `dashboards/`: Power BI files and CSV exports
- `scripts/`: Utilities (export, cleanup, diagnostics, test data)
- `tests/`: Unit tests (38 tests, 100% passing)
  - `test_dedup.py`: Deduplication logic (14 tests)
  - `test_extract.py`: CSV extraction (3 tests)
  - `test_load.py`: Database loading (18 tests)
  - `test_transform.py`: Data transformation (3 tests)
