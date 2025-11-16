# Project 4: Safaricom Data Warehouse

## Overview
This project implements a data warehouse for Safaricom with star schema design for transaction analytics.

## Features
- Star schema dimensional modeling
- AWS S3 data staging
- ETL pipeline for fact and dimension tables
- PowerBI reporting
- Data dictionary and documentation

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python warehouse_etl.py
```

## Structure
- `s3/`: Staging data from S3
- `sql/`: Dimension and fact table schemas
- `models/`: Star schema documentation
- `reports/`: PowerBI dashboards
