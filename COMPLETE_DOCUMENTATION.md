"""
Project Documentation and Architecture Guide
"""

# Victor Data Engineering Portfolio - Complete Documentation

## Project Overview

This portfolio contains 4 comprehensive data engineering projects demonstrating:

### Project 1: Kenyan Market ETL
**Purpose**: Extract-Transform-Load pipeline for market data
**Tech Stack**: Python, Pandas, SQLAlchemy, PostgreSQL
**Key Features**:
- Multi-source data extraction (CSV, API, Database)
- Comprehensive data cleaning and validation
- Batch database loading with error handling
- Production-ready logging and error recovery

**Running**:
```bash
cd Project_1_Kenyan_Market_ETL
pip install -r requirements.txt
cp .env.example .env
# Configure .env with database credentials
python run_pipeline.py
```

### Project 2: M-Pesa Airflow Pipeline
**Purpose**: Apache Airflow orchestrated ETL for M-Pesa transactions
**Tech Stack**: Apache Airflow, Python, PostgreSQL, Faker
**Key Features**:
- Realistic transaction data generation
- Multi-stage validation and cleaning
- Fraud detection rules
- DAG-based workflow orchestration
- XCom for inter-task communication

**Running**:
```bash
cd Project_2_MPesa_Airflow_Pipeline
pip install -r requirements.txt
docker-compose -f docker-compose-airflow.yml up
# Access Airflow UI at http://localhost:8080
```

### Project 3: Real-Time Streaming
**Purpose**: Apache Kafka-based real-time transaction processing
**Tech Stack**: Apache Kafka, Python, Docker
**Key Features**:
- Continuous transaction stream producer
- Event-driven consumer with statistics
- Asynchronous message processing
- Real-time metrics aggregation

**Running Producer**:
```bash
cd Project_3_RealTime_Streaming
pip install -r requirements.txt
docker-compose -f docker-compose-kafka.yml up -d
python run_producer.py
```

**Running Consumer** (in another terminal):
```bash
python run_consumer.py
```

### Project 4: Safaricom Data Warehouse
**Purpose**: Star schema data warehouse with S3 integration
**Tech Stack**: AWS S3, Python, PostgreSQL, SQLAlchemy
**Key Features**:
- Star schema dimensional modeling
- S3 data staging with fallback to local
- Automated fact and dimension table loading
- Summary table generation for analytics

**Running**:
```bash
cd Project_4_Safaricom_DataWarehouse
pip install -r requirements.txt
cp .env.example .env
# Configure .env with S3 and database credentials
python warehouse_etl.py
```

## Architecture Patterns

### ETL Pattern (Projects 1, 2, 4)
1. **Extract**: Data ingestion from multiple sources
2. **Transform**: Cleaning, validation, enrichment
3. **Load**: Batch/incremental database loading

### Streaming Pattern (Project 3)
1. **Produce**: Continuous event generation
2. **Consume**: Real-time event processing
3. **Aggregate**: Statistics and metrics calculation

### Orchestration Pattern (Project 2)
1. **DAG Definition**: Task dependencies
2. **Task Groups**: Logical grouping
3. **XCom**: Inter-task communication
4. **Error Handling**: Retry logic

## Common Development Tasks

### Running All Tests
```bash
# Project 1
cd Project_1_Kenyan_Market_ETL && python -m pytest tests/ -v

# Project 2
cd Project_2_MPesa_Airflow_Pipeline && python -m pytest tests/ -v
```

### Code Quality
```bash
# Lint code
flake8 . --max-line-length=120

# Format code
black . --line-length=120

# Type checking
mypy .
```

### Database Setup
```bash
# PostgreSQL setup
createdb kenyan_market
createdb mpesa_db
createdb safaricom_dw

# Load schemas
psql kenyan_market < Project_1_Kenyan_Market_ETL/sql/create_tables.sql
```

## Performance Considerations

1. **Batch Processing**: Large datasets processed in configurable batches
2. **Connection Pooling**: Optimized database connections
3. **Async Processing**: Non-blocking operations where applicable
4. **Caching**: Results cached where appropriate
5. **Incremental Loads**: Only new/modified data processed

## Security Best Practices

1. **Environment Variables**: Sensitive config via .env files
2. **Credential Management**: No hardcoded secrets
3. **Database Pooling**: Connection timeouts and recycling
4. **Error Handling**: Secure error messages (no sensitive data leakage)
5. **Logging**: Comprehensive audit trails

## Monitoring & Logging

All projects include comprehensive logging:
- **Log Levels**: INFO, WARNING, ERROR, DEBUG
- **Log Files**: Timestamped logs in project logs/ directories
- **Metrics**: Performance metrics and statistics
- **Alerts**: Error notifications and recovery options

## Troubleshooting

### Database Connection Issues
- Verify database is running
- Check .env credentials
- Ensure database exists

### Airflow Issues
- Check Airflow logs: `airflow logs -t task_id -d dag_id`
- Verify dag syntax: `airflow dags list`
- Check scheduler status: `airflow scheduler`

### Kafka Issues
- Verify Kafka broker: `kafka-broker-api-versions.sh --bootstrap-server localhost:9092`
- Check topics: `kafka-topics.sh --list --bootstrap-server localhost:9092`
- Monitor messages: `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions`

## Future Enhancements

1. **Real-time Dashboard**: Live analytics using Plotly/Grafana
2. **Machine Learning**: Anomaly detection in transactions
3. **Data Quality Framework**: Great Expectations integration
4. **Cloud Migration**: AWS Glue, EMR, or Azure equivalents
5. **Advanced Analytics**: Predictive modeling pipelines

---

**Last Updated**: November 16, 2025
**Portfolio Status**: Complete and Production-Ready
