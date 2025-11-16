# Data Engineering Portfolio - Execution Checklist

## ✅ DEPLOYMENT CHECKLIST

### Phase 1: Environment Setup
- [x] Created `.env` files for all 4 projects
- [x] Updated `requirements.txt` for Python 3.10+ compatibility
- [x] Verified project structure (67 files across 4 projects)
- [x] Generated comprehensive documentation

### Phase 2: Pre-Execution Requirements
- [ ] **PostgreSQL Installation**
  ```bash
  # Install PostgreSQL
  # Create databases: kenyan_market, mpesa_db, safaricom_dw
  createdb kenyan_market
  createdb mpesa_db
  createdb safaricom_dw
  ```

- [ ] **Docker Installation** (for Projects 2 & 3)
  ```bash
  # Install Docker Desktop (includes Docker Compose)
  ```

- [ ] **Python Packages Installation**
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

### Phase 3: Configuration
- [ ] **Update `.env` Files**
  - [ ] Project 1: Database credentials (PostgreSQL/MySQL/SQLite)
  - [ ] Project 2: Airflow settings and database credentials
  - [ ] Project 3: Kafka broker configuration (if not using Docker)
  - [ ] Project 4: AWS S3 credentials (optional for demo)

- [ ] **Database Schema Creation**
  ```bash
  # Run SQL scripts for each project
  
  # Project 1
  psql -U postgres -d kenyan_market -f Project_1_Kenyan_Market_ETL/sql/create_tables.sql
  
  # Project 2
  psql -U postgres -d mpesa_db -f Project_2_MPesa_Airflow_Pipeline/sql/schema.sql
  
  # Project 4
  psql -U postgres -d safaricom_dw -f Project_4_Safaricom_DataWarehouse/sql/create_star_schema.sql
  ```

### Phase 4: Project Execution

#### Project 1: Kenyan Market ETL
- [ ] Navigate to project directory
  ```bash
  cd Project_1_Kenyan_Market_ETL
  ```
- [ ] Run pipeline
  ```bash
  python run_pipeline.py
  ```
- [ ] Expected output:
  - CSV file loaded
  - Data transformed
  - Batch loading to database (1000 records at a time)
  - Load report generated

#### Project 2: M-Pesa Airflow Pipeline
- [ ] Navigate to project directory
  ```bash
  cd Project_2_MPesa_Airflow_Pipeline
  ```
- [ ] Start Airflow
  ```bash
  docker-compose -f docker-compose-airflow.yml up
  ```
- [ ] Access Airflow UI
  ```
  http://localhost:8080
  (Default: airflow/airflow)
  ```
- [ ] Expected output:
  - Airflow services running (webserver, scheduler, postgres)
  - DAG visible in UI
  - Tasks execute in sequence

#### Project 3: Real-Time Streaming
- [ ] Navigate to project directory
  ```bash
  cd Project_3_RealTime_Streaming
  ```
- [ ] Start Kafka
  ```bash
  docker-compose -f docker-compose-kafka.yml up -d
  ```
- [ ] Start Producer (Terminal 1)
  ```bash
  python run_producer.py
  ```
- [ ] Start Consumer (Terminal 2)
  ```bash
  python run_consumer.py
  ```
- [ ] Expected output:
  - Producer: Continuous message generation
  - Consumer: Real-time message processing with statistics

#### Project 4: Safaricom Data Warehouse
- [ ] Navigate to project directory
  ```bash
  cd Project_4_Safaricom_DataWarehouse
  ```
- [ ] Run ETL
  ```bash
  python warehouse_etl.py
  ```
- [ ] Expected output:
  - Dimension tables loaded (customers, dates)
  - Fact tables loaded (transactions)
  - Summary tables generated
  - ETL completion report

### Phase 5: Verification

#### Data Validation
- [ ] **Project 1**: Query table to verify loaded records
  ```sql
  SELECT COUNT(*) FROM market_data;
  ```

- [ ] **Project 2**: Check transaction records
  ```sql
  SELECT COUNT(*) FROM transactions;
  ```

- [ ] **Project 3**: Monitor real-time message flow
  ```
  Total messages processed: [XXX]
  Successful: [XXX]
  Failed: [XXX]
  ```

- [ ] **Project 4**: Verify star schema
  ```sql
  SELECT COUNT(*) FROM dim_customer;
  SELECT COUNT(*) FROM dim_date;
  SELECT COUNT(*) FROM fact_transactions;
  SELECT COUNT(*) FROM summary_daily_transactions;
  ```

#### Test Execution
- [ ] Run Project 1 tests
  ```bash
  cd Project_1_Kenyan_Market_ETL
  pytest tests/
  ```

- [ ] Run Project 2 tests
  ```bash
  cd Project_2_MPesa_Airflow_Pipeline
  pytest tests/
  ```

#### Log Review
- [ ] [ ] Check log files for errors
  ```bash
  # Logs are typically in logs/ directory
  tail -f logs/*.log
  ```

### Phase 6: Performance & Optimization
- [ ] [ ] Monitor resource usage during execution
- [ ] [ ] Verify batch processing efficiency
- [ ] [ ] Check database connection pooling
- [ ] [ ] Monitor real-time streaming throughput

### Phase 7: Deployment Readiness
- [ ] [ ] Code review completed
- [ ] [ ] All tests passing
- [ ] [ ] Documentation complete
- [ ] [ ] No hardcoded credentials
- [ ] [ ] Error handling validated
- [ ] [ ] Logging configured
- [ ] [ ] Performance acceptable
- [ ] [ ] Security validated

---

## 📋 Project-Specific Checklists

### Project 1: Kenyan Market ETL
**Features to Verify**:
- [ ] CSV extraction working
- [ ] API extraction working (if configured)
- [ ] Database extraction working (if configured)
- [ ] Data cleaning applied
- [ ] Type conversion successful
- [ ] Batch loading to database
- [ ] Error handling functional
- [ ] Logging detailed

### Project 2: M-Pesa Airflow
**Features to Verify**:
- [ ] Airflow DAG visible in UI
- [ ] Transaction generation realistic (Kenyan data)
- [ ] Data validation passing (95%+ threshold)
- [ ] Fraud detection triggered
- [ ] Database loading successful
- [ ] Report generation working
- [ ] Task dependencies correct

### Project 3: Real-Time Streaming
**Features to Verify**:
- [ ] Kafka brokers running
- [ ] Messages produced continuously
- [ ] Messages consumed successfully
- [ ] Statistics aggregated
- [ ] Compression working (gzip)
- [ ] Async operations functional
- [ ] Graceful shutdown working

### Project 4: Data Warehouse
**Features to Verify**:
- [ ] S3 connection working (or fallback to local CSV)
- [ ] Dimension tables populated
- [ ] Fact tables populated with correct foreign keys
- [ ] Summary tables generated
- [ ] Date dimension includes holidays
- [ ] Customer dimension accurate
- [ ] ETL performance acceptable

---

## 🎯 Success Criteria

### All Projects Must:
- ✅ Execute without errors
- ✅ Load/process data successfully
- ✅ Generate expected output
- ✅ Complete in reasonable time
- ✅ Log all operations
- ✅ Handle errors gracefully
- ✅ Support re-runs without duplicates (idempotent)
- ✅ Demonstrate Kenyan business context

### Portfolio Must:
- ✅ Showcase 4 distinct data engineering concepts
- ✅ Include ETL, Orchestration, Streaming, Data Warehousing
- ✅ Demonstrate production-ready code quality
- ✅ Include comprehensive documentation
- ✅ Be immediately deployable
- ✅ Require minimal configuration
- ✅ Support team collaboration
- ✅ Scale to larger datasets

---

## 📞 Support Resources

### Documentation
- `DEPLOYMENT_GUIDE.md` - Step-by-step setup
- `IMPLEMENTATION_SUMMARY.md` - Technical overview
- `COMPLETE_DOCUMENTATION.md` - Comprehensive guide
- `README_SETUP.md` - Per-project instructions

### Troubleshooting
- Check `.env` file configuration
- Verify database connectivity
- Review log files for errors
- Ensure all dependencies installed
- Check Docker service status (for Projects 2 & 3)
- Review Python version compatibility (3.10+)

### Quick Commands
```bash
# Check Python version
python --version

# Verify PostgreSQL connection
psql -U postgres -c "SELECT version();"

# List running Docker containers
docker ps

# Check Kafka logs
docker-compose logs kafka

# View Airflow logs
docker-compose logs scheduler
```

---

**Portfolio Status**: ✅ READY FOR EXECUTION
**Last Verified**: November 16, 2025
**Version**: 1.0
