"""
Database Configuration Module

This module handles database connection and configuration settings.
Supports both PostgreSQL and other SQLAlchemy-compatible databases.

Configuration is read from environment variables for security.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Database Configuration from Environment Variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "kenyan_market")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_TYPE = os.getenv("DB_TYPE", "postgresql")

# Connection Pool Settings
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

def build_connection_string():
    """
    Build database connection string
    
    Returns:
        str: SQLAlchemy connection string
    """
    if DB_TYPE == "postgresql":
        conn_string = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    elif DB_TYPE == "mysql":
        conn_string = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@"
            f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    elif DB_TYPE == "sqlite":
        conn_string = f"sqlite:///{DB_NAME}.db"
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")
    
    return conn_string

def get_db_connection():
    """
    Create and return database connection engine
    
    Returns:
        sqlalchemy.engine.Engine: Database engine
        
    Raises:
        Exception: If connection cannot be established
    """
    try:
        conn_string = build_connection_string()
        
        engine = create_engine(
            conn_string,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_recycle=POOL_RECYCLE,
            echo=os.getenv("DB_ECHO", "False").lower() == "true"
        )
        
        # Test the connection
        with engine.connect() as connection:
            logger.info(f"✓ Successfully connected to {DB_TYPE}://{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        return engine
    
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def close_connection(engine):
    """
    Close database connection
    
    Args:
        engine: SQLAlchemy engine
    """
    try:
        engine.dispose()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing connection: {str(e)}")

# Configuration info for logging/debugging
CONFIG_INFO = {
    'db_type': DB_TYPE,
    'host': DB_HOST,
    'port': DB_PORT,
    'database': DB_NAME,
    'user': DB_USER,
    'pool_size': POOL_SIZE,
    'max_overflow': MAX_OVERFLOW
}
