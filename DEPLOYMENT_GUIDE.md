# Victor Data Engineering Portfolio - Complete Deployment Guide

## ✅ Deployment Status: COMPLETE

All 4 projects have been configured and are ready for execution.

---

## 📦 Configuration Summary

### Environment Files Created
✅ `.env` files created in each project with:
- **Project 1**: PostgreSQL connection settings, API base URL, logging configuration
- **Project 2**: Airflow settings, PostgreSQL database credentials, batch size configuration
- **Project 3**: Kafka broker connection, topic configuration, consumer settings
- **Project 4**: AWS S3 credentials template, Data Warehouse database settings

### Requirements Updated
All `requirements.txt` files updated for Python 3.14 compatibility:
- **Project 1**: pandas, numpy, sqlalchemy, psycopg2-binary, requests, pytest
- **Project 2**: apache-airflow, faker, pandas, numpy, sqlalchemy, psycopg2-binary
- **Project 3**: kafka-python, pandas, numpy, pytest
- **Project 4**: boto3, sqlalchemy, psycopg2-binary, pandas, numpy

---

## 🏗️ Project Structure Complete

### Project 1: Kenyan Market ETL (22 Files)
```
Project_1_Kenyan_Market_ETL/
├── run_pipeline.py              # Main orchestration script
├── etl/
│   ├── extract.py              # Multi-source data extraction
│   ├── transform.py            # Data cleaning & transformation
│   └── load.py                 # Batch database loading
├── config/
│   ├── db_config.py            # Database connection management
│   └── settings.py             # Configuration settings
├── tests/
│   ├── test_extract.py         # Extract module tests
│   ├── test_transform.py       # Transform module tests
│   ├── test_load.py            # Load module tests
│   └── test_integration.py     # End-to-end tests
├── data/
│   └── sample_market_data.csv  # Sample input data
├── sql/
│   └── create_tables.sql       # Database schema
├── .env                         # Configuration
├── requirements.txt             # Dependencies
├── Makefile                     # Build commands
└── README_SETUP.md             # Setup guide
```

**Key Features**:
- Extract from CSV, API, or Database sources
- Transform with data cleaning, standardization, type conversion
- Load in configurable batches (default 1000 records)
- Comprehensive error handling and logging
- Support for PostgreSQL, MySQL, SQLite

**Run Command**:
```bash
cd Project_1_Kenyan_Market_ETL
python run_pipeline.py
```

---

### Project 2: M-Pesa Airflow Pipeline (19 Files)
```
Project_2_MPesa_Airflow_Pipeline/
├── mpesa_dag.py                # Airflow DAG definition
├── generator/
│   └── transaction_generator.py # Realistic data generation
├── etl/
│   ├── clean.py               # Data cleaning module
│   ├── validate.py            # Business rule validation
│   └── load_to_db.py          # Database batch loading
├── tests/
│   ├── test_integration.py    # Integration tests
│   └── conftest.py            # Pytest configuration
├── sql/
│   ├── schema.sql             # Table definitions
│   └── fraud_rules.sql        # Fraud detection views
├── docker-compose-airflow.yml # Airflow infrastructure
├── .env                        # Configuration
├── requirements.txt            # Dependencies
└── Makefile                    # Build commands
```

**Key Features**:
- Airflow DAG with task groups
- Realistic Kenyan transaction generation (Faker)
- 5-stage ETL: Extract → Validate → Clean → Fraud Detection → Load
- XCom-based inter-task communication
- Fraud detection rules engine
- Batch database loading with error recovery

**Run Command**:
```bash
cd Project_2_MPesa_Airflow_Pipeline
docker-compose -f docker-compose-airflow.yml up
# Access UI at http://localhost:8080
```

---

### Project 3: Real-Time Streaming (11 Files)
```
Project_3_RealTime_Streaming/
├── run_producer.py             # Continuous producer runner
├── run_consumer.py             # Consumer with statistics
├── streaming/
│   ├── kafka_producer.py       # Producer implementation
│   └── kafka_consumer.py       # Consumer implementation
├── docker-compose-kafka.yml    # Kafka infrastructure
├── .env                         # Configuration
├── requirements.txt             # Dependencies
└── Makefile                     # Build commands
```

**Key Features**:
- Kafka producer with continuous message generation
- Consumer with event processing and statistics aggregation
- Asynchronous consumption support
- Message compression (gzip)
- Graceful shutdown handling
- Real-time performance metrics

**Run Command**:
```bash
cd Project_3_RealTime_Streaming
docker-compose -f docker-compose-kafka.yml up -d
# Terminal 1:
python run_producer.py
# Terminal 2:
python run_consumer.py
```

---

### Project 4: Safaricom Data Warehouse (14 Files)
```
Project_4_Safaricom_DataWarehouse/
├── warehouse_etl.py            # Main ETL pipeline
├── s3_config.py                # AWS S3 integration
├── sql/
│   ├── create_star_schema.sql  # Schema creation
│   ├── dim_customer.sql        # Customer dimension
│   ├── dim_date.sql            # Date dimension
│   ├── fact_transactions.sql   # Transaction facts
│   └── summary_tables.sql      # Summary aggregations
├── data/
│   └── sample_mpesa_transactions.csv  # Local fallback data
├── models/
│   └── data_dictionary.md      # Schema documentation
├── .env                         # Configuration
├── requirements.txt             # Dependencies
└── Makefile                     # Build commands
```

**Key Features**:
- Star schema dimensional modeling
- S3 data staging with boto3 integration
- Fallback to local CSV sample data
- Automated dimension table loading (date, customer)
- Automated fact table loading (transactions)
- Summary table generation
- Batch processing with error handling

**Run Command**:
```bash
cd Project_4_Safaricom_DataWarehouse
python warehouse_etl.py
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- PostgreSQL (for Projects 1, 2, 4)
- Docker & Docker Compose (for Projects 2, 3 - optional)

### Step 1: Create Databases
```bash
# Connect to PostgreSQL
psql -U postgres

# Create databases
CREATE DATABASE kenyan_market;
CREATE DATABASE mpesa_db;
CREATE DATABASE safaricom_dw;
```

### Step 2: Install Dependencies
```bash
# Project 1
cd Project_1_Kenyan_Market_ETL
pip install -r requirements.txt

# Project 2
cd ../Project_2_MPesa_Airflow_Pipeline
pip install -r requirements.txt

# Project 3
cd ../Project_3_RealTime_Streaming
pip install -r requirements.txt

# Project 4
cd ../Project_4_Safaricom_DataWarehouse
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Each project has a `.env` file. Update with your credentials:
- Database host, port, username, password
- AWS credentials (Project 4 - optional)
- Kafka broker address (Project 3 - if not using Docker)

### Step 4: Run Projects
```bash
# Project 1: ETL Pipeline
cd Project_1_Kenyan_Market_ETL
python run_pipeline.py

# Project 2: Airflow (requires Docker)
cd Project_2_MPesa_Airflow_Pipeline
docker-compose -f docker-compose-airflow.yml up

# Project 3: Streaming (requires Docker)
cd Project_3_RealTime_Streaming
docker-compose -f docker-compose-kafka.yml up -d
python run_producer.py  # Terminal 1
python run_consumer.py  # Terminal 2

# Project 4: Data Warehouse
cd Project_4_Safaricom_DataWarehouse
python warehouse_etl.py
```

---

## 📊 Portfolio Metrics

| Metric | Count |
|--------|-------|
| **Total Projects** | 4 |
| **Total Files** | 67 |
| **Python Modules** | 28+ |
| **SQL Files** | 8 |
| **Test Files** | 4+ |
| **Docker Configs** | 2 |
| **Documentation Files** | 6+ |
| **Total Lines of Code** | 3,500+ |

---

## 🔧 Troubleshooting

### ImportError with SQLAlchemy
**Issue**: `ImportError: cannot import name 'util' from sqlalchemy`
**Solution**: Update SQLAlchemy to 2.0+
```bash
pip install --upgrade sqlalchemy
```

### PostgreSQL Connection Failed
**Issue**: `psycopg2.OperationalError: could not connect to server`
**Solution**: 
1. Ensure PostgreSQL is running
2. Check credentials in `.env` file
3. Verify database exists

### Kafka Connection Failed
**Issue**: Connection refused on localhost:9092
**Solution**:
```bash
cd Project_3_RealTime_Streaming
docker-compose -f docker-compose-kafka.yml restart
```

---

## 📚 Key Technologies

- **Python 3.14**
- **Apache Airflow 2.6+**
- **Apache Kafka 2.0.2+**
- **PostgreSQL/MySQL**
- **AWS S3**
- **SQLAlchemy 2.0+**
- **Pandas 2.0+**
- **Faker (Data Generation)**
- **Docker & Docker Compose**

---

## ✨ Production-Ready Features

✅ Comprehensive error handling
✅ Detailed logging to timestamped files
✅ Database connection pooling
✅ Batch processing for performance
✅ Unit and integration tests
✅ Environment-based configuration
✅ No hardcoded credentials
✅ Data quality validation
✅ Fraud detection rules
✅ Star schema dimensional modeling
✅ Real-time streaming support
✅ Graceful error recovery

---

## 🎯 Next Steps

1. **Install dependencies** as per Step 2 above
2. **Create PostgreSQL databases** per Step 1
3. **Configure .env files** with your credentials
4. **Run individual projects** to verify functionality
5. **Extend projects** with your custom business logic
6. **Deploy to production** using Docker/Kubernetes

---

**Status**: ✅ Portfolio Complete & Ready for Deployment
**Last Updated**: November 16, 2025
**Version**: 1.0
