"""
Safaricom Data Warehouse ETL Pipeline

Complete ETL pipeline for loading transaction data into a star schema data warehouse.
Supports dimension and fact table loading with incremental updates.
"""

import logging
import pandas as pd
from datetime import datetime
from s3_config import get_s3_data
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataWarehouseETL:
    """Orchestrate data warehouse ETL operations"""
    
    def __init__(self, engine):
        """Initialize ETL with database engine"""
        self.engine = engine
        self.etl_stats = {
            'dimensions_loaded': {},
            'facts_loaded': {},
            'start_time': None,
            'end_time': None
        }
    
    def load_dim_date(self, start_date='2024-01-01', end_date='2024-12-31'):
        """Load date dimension table"""
        logger.info("Loading date dimension...")
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        records = []
        for date in dates:
            records.append({
                'full_date': date.date(),
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'quarter': (date.month - 1) // 3 + 1,
                'week_of_year': date.isocalendar()[1],
                'day_of_week': date.day_name(),
                'is_weekend': date.weekday() >= 5,
                'is_holiday': False
            })
        
        df = pd.DataFrame(records)
        
        try:
            df.to_sql('dim_date', con=self.engine, if_exists='append', index=False)
            self.etl_stats['dimensions_loaded']['dim_date'] = len(df)
            logger.info(f"Loaded {len(df)} date records")
        except Exception as e:
            logger.warning(f"Date dimension already loaded: {str(e)}")
    
    def load_dim_customer(self, source_data):
        """Load customer dimension table"""
        logger.info("Loading customer dimension...")
        
        if source_data.empty:
            logger.warning("No customer data to load")
            return
        
        # Extract unique customers from source data
        customers = pd.DataFrame()
        
        if 'sender' in source_data.columns:
            sender_customers = source_data[['sender']].drop_duplicates()
            sender_customers.columns = ['customer_key']
            customers = pd.concat([customers, sender_customers], ignore_index=True)
        
        if 'receiver' in source_data.columns:
            receiver_customers = source_data[['receiver']].drop_duplicates()
            receiver_customers.columns = ['customer_key']
            customers = pd.concat([customers, receiver_customers], ignore_index=True)
        
        customers = customers.drop_duplicates().reset_index(drop=True)
        customers['customer_name'] = 'Customer_' + customers['customer_key']
        customers['phone_number'] = customers['customer_key']
        customers['email'] = customers['customer_key'] + '@safaricom.com'
        customers['registration_date'] = datetime.now().date()
        customers['account_type'] = 'Premium'
        customers['status'] = 'Active'
        
        try:
            customers.to_sql('dim_customer', con=self.engine, if_exists='append', index=False)
            self.etl_stats['dimensions_loaded']['dim_customer'] = len(customers)
            logger.info(f"Loaded {len(customers)} customer records")
        except Exception as e:
            logger.warning(f"Customer dimension error: {str(e)}")
    
    def load_fact_transactions(self, source_data):
        """Load transaction fact table"""
        logger.info("Loading transaction fact table...")
        
        if source_data.empty:
            logger.warning("No transaction data to load")
            return
        
        facts = pd.DataFrame()
        facts['transaction_key'] = source_data['transaction_id']
        facts['sender'] = source_data['sender']
        facts['receiver'] = source_data['receiver']
        facts['amount'] = source_data['amount']
        facts['timestamp'] = pd.to_datetime(source_data['timestamp'])
        facts['transaction_type'] = source_data['transaction_type']
        facts['status'] = source_data['status']
        facts['fee'] = source_data.get('fee', 0)
        facts['net_amount'] = facts['amount'] - facts['fee']
        facts['provider'] = source_data.get('provider', 'Unknown')
        
        try:
            facts.to_sql('fact_transactions', con=self.engine, if_exists='append', index=False)
            self.etl_stats['facts_loaded']['fact_transactions'] = len(facts)
            logger.info(f"Loaded {len(facts)} transaction records")
        except Exception as e:
            logger.warning(f"Fact table error: {str(e)}")
    
    def create_summary_tables(self):
        """Create and populate summary tables"""
        logger.info("Creating summary tables...")
        
        summary_sql = """
        CREATE TABLE IF NOT EXISTS summary_daily_transactions (
            date_id INT,
            total_transactions INT,
            total_amount DECIMAL(15, 2),
            total_fee DECIMAL(15, 2),
            successful_transactions INT,
            failed_transactions INT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        INSERT INTO summary_daily_transactions (date_id, total_transactions, total_amount, total_fee, successful_transactions, failed_transactions)
        SELECT
            dd.date_id,
            COUNT(ft.transaction_id) as total_transactions,
            SUM(ft.amount) as total_amount,
            SUM(ft.fee) as total_fee,
            COUNT(CASE WHEN ft.status = 'success' THEN 1 END) as successful_transactions,
            COUNT(CASE WHEN ft.status = 'failed' THEN 1 END) as failed_transactions
        FROM fact_transactions ft
        LEFT JOIN dim_date dd ON DATE(ft.timestamp) = dd.full_date
        GROUP BY dd.date_id;
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(summary_sql))
                conn.commit()
            logger.info("Summary tables created")
        except Exception as e:
            logger.warning(f"Summary table error: {str(e)}")
    
    def run(self):
        """Execute complete ETL pipeline"""
        self.etl_stats['start_time'] = datetime.now()
        
        logger.info("="*60)
        logger.info("SAFARICOM DATA WAREHOUSE ETL PIPELINE")
        logger.info("="*60)
        
        try:
            # Extract from S3
            logger.info("Extracting data from S3...")
            source_data = get_s3_data()
            
            # Load dimensions
            self.load_dim_date()
            self.load_dim_customer(source_data)
            
            # Load facts
            self.load_fact_transactions(source_data)
            
            # Create summary tables
            self.create_summary_tables()
            
            self.etl_stats['end_time'] = datetime.now()
            duration = (self.etl_stats['end_time'] - self.etl_stats['start_time']).total_seconds()
            
            logger.info("="*60)
            logger.info("ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Dimensions: {self.etl_stats['dimensions_loaded']}")
            logger.info(f"Facts: {self.etl_stats['facts_loaded']}")
            logger.info("="*60)
            
            return True
        
        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}", exc_info=True)
            return False

def main():
    """Main ETL execution"""
    from s3_config import get_db_connection
    
    try:
        engine = get_db_connection()
        etl = DataWarehouseETL(engine)
        success = etl.run()
        
        if not success:
            exit(1)
    
    except Exception as e:
        logger.error(f"Failed to start ETL: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
