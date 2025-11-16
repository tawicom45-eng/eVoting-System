# Victor Data Engineering Portfolio

Welcome to my comprehensive data engineering portfolio. This collection showcases my expertise in building enterprise-grade data solutions, ETL pipelines, real-time streaming, and data warehousing. **All projects are production-ready with CI/CD automation, comprehensive test coverage, and professional documentation.**

[![Project 1 Tests](https://img.shields.io/badge/Project_1_Tests-38%2F38%20passing-brightgreen)](./Project_1_Kenyan_Market_ETL)
[![Project 2 Tests](https://img.shields.io/badge/Project_2_Tests-3%2F3%20passing-brightgreen)](./Project_2_MPesa_Airflow_Pipeline)
[![CI/CD Workflow](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue)](#cicd-status)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-Black%20%7C%20isort%20%7C%20mypy-blue)](#technical-skills)

## 📋 Projects Overview

### [Project 1: Kenyan Market ETL](./Project_1_Kenyan_Market_ETL) ⭐ **Fully Tested**
Complete ETL pipeline for processing Kenyan market data with idempotent upserts, deduplication, and PowerBI integration.

**Key Features:**
- Extract from CSV with error handling
- Data transformation with automatic deduplication logic (removes duplicates while aggregating quantities)
- Idempotent upsert to PostgreSQL (no data duplication on re-runs)
- Comprehensive unit tests (38 tests, all passing)
- CI/CD with GitHub Actions (Python 3.8-3.11)

**Technologies:** Python, Pandas, PostgreSQL, SQLAlchemy, PowerBI
**Interview Talking Points:** Explain dedup strategy, idempotent loading design, test coverage for edge cases

### [Project 2: M-Pesa Airflow Pipeline](./Project_2_MPesa_Airflow_Pipeline) ⭐ **Fully Tested**
Apache Airflow-orchestrated ETL pipeline for M-Pesa transaction processing with synthetic data generation and validation.

**Key Features:**
- Transaction generator with realistic Kenyan phone numbers and distribution patterns
- Data cleaning pipeline (duplicates, nulls, type coercion)
- Transaction validation with comprehensive rule engine
- Docker Compose setup for Airflow + Postgres
- Integration tests with 100% passing rate

**Technologies:** Apache Airflow, Python, Faker, PostgreSQL, Docker
**Interview Talking Points:** Airflow DAG design, data generation for testing, cleaning pipeline architecture

### [Project 3: Real-Time Streaming](./Project_3_RealTime_Streaming)
Kafka-based real-time data streaming solution for live transaction processing and analytics.

**Key Features:**
- Kafka producer for transaction streaming
- Kafka consumer with transformation logic
- Real-time aggregation and dashboarding
- Docker Compose setup for Kafka + Zookeeper
- Scalable architecture for high-volume ingestion

**Technologies:** Apache Kafka, Python, Jupyter, Plotly, Docker
**Interview Talking Points:** Kafka architecture, consumer group design, exactly-once semantics

### [Project 4: Safaricom Data Warehouse](./Project_4_Safaricom_DataWarehouse)
Enterprise data warehouse with star schema design for Safaricom transactions analytics and reporting.

**Key Features:**
- Dimensional modeling (facts & dimensions)
- AWS S3 integration for data ingestion
- Optimized SQL queries for analytics
- Aggregation tables for reporting performance
- Security checks and input validation

**Technologies:** Python, AWS S3, PostgreSQL, SQLAlchemy, PowerBI
**Interview Talking Points:** Star schema design, fact vs. dimension tables, performance optimization

## 🛠️ Technical Skills

- **Languages:** Python, SQL
- **Big Data & Streaming:** Apache Airflow, Apache Kafka
- **Databases:** PostgreSQL, MySQL
- **Cloud:** AWS (S3, EC2)
- **Data Warehousing:** Star Schema, Dimensional Modeling
- **Visualization:** PowerBI, Jupyter Notebooks
- **Tools:** Docker, Git, GitHub Actions (CI/CD)
- **Data Processing:** Pandas, NumPy
- **Testing:** Pytest, Unit & Integration Tests
- **Code Quality:** Black, isort, Flake8, MyPy

## 📁 Getting Started Quickly

### Quick Test Run (Project 1 - Fully Tested)

```bash
cd Project_1_Kenyan_Market_ETL
pip install -r requirements.txt
pytest -v  # Run all 38 tests - all passing ✓
```

### For Interviews: Talk About These Aspects

1. **Idempotency:** Project 1 demonstrates idempotent upserts - running the pipeline twice doesn't duplicate data
2. **Deduplication:** Smart logic aggregates quantities for duplicate market entries
3. **Testing:** 38 comprehensive unit tests covering edge cases (nulls, infinite values, empty data)
4. **CI/CD:** GitHub Actions runs tests on Python 3.8-3.12, checks code quality (Black, isort, mypy)
5. **Real-World Skills:** Handles missing values, type coercion, constraint management, batch loading

## 📋 CI/CD Status

- ✅ **Project 1 (Kenyan Market ETL):** 38 tests passing, GitHub Actions enabled, Python 3.8-3.11
- ✅ **Project 2 (M-Pesa Airflow):** 3 tests passing, GitHub Actions enabled, Python 3.9-3.12
- ✅ **Project 3 (Real-Time Streaming):** Kafka setup validated, GitHub Actions enabled
- ✅ **Project 4 (Data Warehouse):** Security checks enabled, GitHub Actions enabled

## 📁 Portfolio Documents

- [Victor_Data_Engineering_Portfolio.pdf](./Portfolio_Documents/Victor_Data_Engineering_Portfolio.pdf)
- [CV_Data_Engineer.pdf](./Portfolio_Documents/CV_Data_Engineer.pdf)
- [Cover_Letter_Safaricom.pdf](./Portfolio_Documents/Cover_Letter_Safaricom.pdf)

## 🎯 Key Achievements

- Designed and implemented scalable ETL pipelines processing millions of transactions
- Built real-time streaming solutions with Kafka handling high-volume data ingestion
- Developed enterprise data warehouses with optimized star schema design
- Implemented automated fraud detection rules for financial transactions
- Created comprehensive dashboards and reports for business intelligence

## 📚 Project Structure

Each project follows best practices with:

- Clear separation of concerns (extract, transform, load)
- Configuration management
- SQL schema definitions
- Docker containerization for reproducibility
- Requirements files for dependency management
- Comprehensive README documentation

## 🚀 Getting Started

1. Clone the repository
2. Navigate to individual project directories
3. Install dependencies: `pip install -r requirements.txt`
4. Follow project-specific README for setup and execution

## 📧 Contact

For inquiries about these projects or data engineering opportunities, please reach out through the contact information provided in the CV.

---

**Last Updated:** November 2025
