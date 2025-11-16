"""
AWS S3 Configuration and Data Loading

Handles S3 connectivity, data retrieval, and database connections for the data warehouse.
"""

import boto3
import os
import pandas as pd
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

logger = logging.getLogger(__name__)

# AWS Configuration
S3_BUCKET = os.getenv("S3_BUCKET", "safaricom-data")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_PREFIX = os.getenv("S3_PREFIX", "transactions/")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Database Configuration
DB_HOST = os.getenv("DW_DB_HOST", "localhost")
DB_PORT = os.getenv("DW_DB_PORT", "5432")
DB_NAME = os.getenv("DW_DB_NAME", "safaricom_dw")
DB_USER = os.getenv("DW_DB_USER", "postgres")
DB_PASSWORD = os.getenv("DW_DB_PASSWORD", "password")
DB_TYPE = os.getenv("DW_DB_TYPE", "postgresql")

class S3DataLoader:
    """Load data from S3 bucket"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            region_name=S3_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        logger.info(f"S3 client initialized for bucket: {S3_BUCKET}")
    
    def list_files(self):
        """List files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=S3_BUCKET,
                Prefix=S3_PREFIX
            )
            
            files = [obj['Key'] for obj in response.get('Contents', [])]
            logger.info(f"Found {len(files)} files in S3")
            return files
        except Exception as e:
            logger.error(f"Error listing S3 files: {str(e)}")
            return []
    
    def download_csv(self, s3_key):
        """Download CSV file from S3"""
        try:
            obj = self.s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
            df = pd.read_csv(obj['Body'])
            logger.info(f"Downloaded {len(df)} records from {s3_key}")
            return df
        except Exception as e:
            logger.error(f"Error downloading {s3_key}: {str(e)}")
            return pd.DataFrame()
    
    def download_all_data(self):
        """Download all data from S3 and combine into single dataframe"""
        logger.info(f"Downloading all data from S3://{S3_BUCKET}/{S3_PREFIX}")
        
        files = self.list_files()
        
        all_data = []
        for file_key in files:
            if file_key.endswith('.csv'):
                df = self.download_csv(file_key)
                if not df.empty:
                    all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Combined {len(combined_df)} total records")
            return combined_df
        else:
            logger.warning("No data downloaded from S3")
            return pd.DataFrame()

def build_connection_string():
    """Build database connection string"""
    if DB_TYPE == "postgresql":
        return f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    elif DB_TYPE == "mysql":
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")

def get_db_connection():
    """Get database connection engine"""
    try:
        conn_string = build_connection_string()
        engine = create_engine(
            conn_string,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600
        )
        
        with engine.connect() as conn:
            logger.info(f"✓ Connected to {DB_TYPE} at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        return engine
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def get_s3_data():
    """Load data from S3"""
    logger.info("Loading data from S3...")
    
    try:
        # Try to load from S3
        if AWS_ACCESS_KEY and AWS_SECRET_KEY:
            loader = S3DataLoader()
            data = loader.download_all_data()
            
            if not data.empty:
                return data
        
        # Fallback: Load from local sample file
        logger.warning("Falling back to local sample data...")
        sample_file = os.path.join(os.path.dirname(__file__), 's3', 'sample_mpesa_transactions.csv')
        
        if os.path.exists(sample_file):
            df = pd.read_csv(sample_file)
            logger.info(f"Loaded {len(df)} records from local sample")
            return df
        else:
            logger.error("No sample data file found")
            return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()
