# Project 2: M-Pesa Airflow Pipeline

## Overview
This project implements an Apache Airflow-based ETL pipeline for M-Pesa transaction processing.

## Features
- Transaction data generation
- Data validation and cleaning
- Apache Airflow orchestration
- Fraud detection rules
- Database loading

## Setup
```bash
docker-compose -f docker-compose-airflow.yml up
```

## Usage
```bash
python mpesa_dag.py
```

## Structure
- `generator/`: Transaction data generation
- `etl/`: Data cleaning and validation
- `sql/`: Database schemas and fraud rules
- `logs/`: Airflow logs (auto-generated)
