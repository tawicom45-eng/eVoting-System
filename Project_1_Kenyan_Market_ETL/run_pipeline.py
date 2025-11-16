#!/usr/bin/env python
"""
Main ETL Pipeline Execution Script

This script orchestrates the complete ETL pipeline for Kenyan market data:
1. Extract data from multiple sources
2. Transform and clean the data
3. Load into database and CSV

Usage:
    python run_pipeline.py
    
Environment Variables:
    DB_HOST: Database host (default: localhost)
    DB_PORT: Database port (default: 5432)
    DB_NAME: Database name (default: kenyan_market)
    DB_USER: Database user (default: postgres)
    DB_PASSWORD: Database password
"""

import sys
import logging
import argparse
from datetime import datetime
from etl.extract import extract_data
from etl.transform import transform_data
from etl.load import load_data
from config.db_config import get_db_connection
from sqlalchemy import text

def create_logs_directory():
    """Create logs directory if it doesn't exist"""
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Ensure output directory exists for CSV backups
    if not os.path.exists('output'):
        os.makedirs('output')

# Ensure logs directory exists before configuring logging
create_logs_directory()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    pass

def truncate_table(engine, table_name='market_data'):
    """Truncate or delete all rows from the target table in a DB-compatible way.

    Uses TRUNCATE for Postgres and DELETE for SQLite (which doesn't support TRUNCATE).
    """
    dialect = engine.dialect.name.lower()
    logger.info(f"Truncating table {table_name} (dialect={dialect})")
    try:
        with engine.begin() as conn:
            if dialect == 'postgresql':
                conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
            else:
                # SQLite and others: use DELETE
                conn.execute(text(f"DELETE FROM {table_name}"))
        logger.info(f"Truncated table {table_name}")
    except Exception as e:
        logger.warning(f"Failed to truncate table {table_name}: {e}")


def main(args):
    """Run the complete ETL pipeline"""
    pipeline_start_time = datetime.now()
    
    try:
        print("\n" + "="*60)
        print("KENYAN MARKET ETL PIPELINE")
        print("="*60)
        print(f"Start Time: {pipeline_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Create logs directory
        create_logs_directory()
        
        # Step 1: Extract
        logger.info("="*60)
        logger.info("EXTRACTION PHASE")
        logger.info("="*60)
        raw_data = extract_data()
        
        if raw_data.empty:
            logger.error("Extraction failed - no data extracted")
            sys.exit(1)
        
        logger.info(f"Extraction completed: {len(raw_data)} records")
        
        # Step 2: Transform
        logger.info("\n" + "="*60)
        logger.info("TRANSFORMATION PHASE")
        logger.info("="*60)
        transformed_data = transform_data(raw_data)
        
        if transformed_data.empty:
            logger.error("Transformation failed - no data transformed")
            sys.exit(1)
        
        logger.info(f"Transformation completed: {len(transformed_data)} records")
        
        # Step 3: Load
        logger.info("\n" + "="*60)
        logger.info("LOADING PHASE")
        logger.info("="*60)
        try:
            conn = get_db_connection()

            # If user requested a clean/force load, truncate the target table first
            if getattr(args, 'truncate', False):
                try:
                    truncate_table(conn, table_name='market_data')
                except Exception:
                    logger.warning("Could not truncate table before load; continuing with load")

            load_data(
                transformed_data,
                conn,
                table_name='market_data',
                output_csv='output/market_data_loaded.csv'
            )
            logger.info("Data loading completed successfully")
        except Exception as e:
            logger.warning(f"Database loading failed: {str(e)}")
            logger.info("Attempting CSV-only load...")
            load_data(
                transformed_data,
                None,
                table_name='market_data',
                output_csv='output/market_data_loaded.csv'
            )
        
        # Pipeline completion
        pipeline_end_time = datetime.now()
        duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        print("\n" + "="*60)
        print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"End Time: {pipeline_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Records Processed: {len(transformed_data)}")
        print("="*60 + "\n")
        
        logger.info(f"Pipeline completed successfully in {duration:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        print(f"\n❌ Pipeline failed: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Kenyan Market ETL pipeline')
    parser.add_argument('--truncate', '--force', action='store_true', dest='truncate',
                        help='Truncate the target table before loading (clean load)')
    parsed = parser.parse_args()
    main(parsed)
