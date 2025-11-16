"""
Database Loading Module

Handles loading transactions to database with:
- Batch processing
- Error handling
- Transaction management
- Status tracking
"""

import pandas as pd
import logging
from datetime import datetime
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class DatabaseLoader:
    """Load transaction data to database"""
    
    def __init__(self, engine, table_name='transactions'):
        """Initialize loader"""
        self.engine = engine
        self.table_name = table_name
        self.batch_size = 1000
        self.load_stats = {
            'total_records': 0,
            'inserted': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
    
    def create_table_if_not_exists(self):
        """Create transactions table if it doesn't exist"""
        logger.info(f"Creating table {self.table_name} if not exists...")
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            transaction_id VARCHAR(50) UNIQUE NOT NULL,
            sender VARCHAR(20) NOT NULL,
            receiver VARCHAR(20) NOT NULL,
            amount DECIMAL(15, 2) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            transaction_type VARCHAR(50),
            status VARCHAR(20),
            provider VARCHAR(50),
            fee DECIMAL(10, 2),
            net_amount DECIMAL(15, 2),
            risk_level VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            logger.info(f"Table {self.table_name} ready")
        except Exception as e:
            logger.error(f"Error creating table: {str(e)}")
            raise
    
    def load_batch(self, df_batch):
        """Load a batch of records to database"""
        try:
            records_inserted = df_batch.to_sql(
                self.table_name,
                con=self.engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            self.load_stats['inserted'] += len(df_batch)
            logger.info(f"Inserted {len(df_batch)} records")
            return len(df_batch)
        except Exception as e:
            logger.error(f"Error loading batch: {str(e)}")
            self.load_stats['failed'] += len(df_batch)
            return 0
    
    def load_data(self, df):
        """Load dataframe to database in batches"""
        self.load_stats['start_time'] = datetime.now()
        self.load_stats['total_records'] = len(df)
        
        logger.info(f"Starting load of {len(df)} records...")
        
        self.create_table_if_not_exists()
        
        total_batches = (len(df) + self.batch_size - 1) // self.batch_size
        
        for i in range(0, len(df), self.batch_size):
            batch_num = (i // self.batch_size) + 1
            df_batch = df.iloc[i:i + self.batch_size]
            
            logger.info(f"Loading batch {batch_num}/{total_batches}...")
            self.load_batch(df_batch)
        
        self.load_stats['end_time'] = datetime.now()
        duration = (self.load_stats['end_time'] - self.load_stats['start_time']).total_seconds()
        
        logger.info(f"Load completed in {duration:.2f} seconds")
        logger.info(f"Inserted: {self.load_stats['inserted']}, Failed: {self.load_stats['failed']}")
        
        return self.load_stats
    
    def get_load_stats(self):
        """Return load statistics"""
        return self.load_stats

def load_transactions_to_db(data, engine, table_name='transactions'):
    """Main loading function"""
    logger.info("Loading transactions to database...")
    
    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data
    else:
        logger.error("Invalid data format")
        return {}
    
    if df.empty:
        logger.warning("No data to load")
        return {}
    
    loader = DatabaseLoader(engine, table_name)
    stats = loader.load_data(df)
    
    return stats
