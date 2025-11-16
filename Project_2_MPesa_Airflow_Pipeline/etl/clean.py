"""
Data Cleaning Module

Handles data cleaning operations on transaction data including:
- Null value handling
- Duplicate removal
- Format standardization
- Data type conversions
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransactionCleaner:
    """Clean and standardize transaction data"""
    
    REQUIRED_FIELDS = ['transaction_id', 'sender', 'receiver', 'amount', 'timestamp']
    
    def __init__(self, df=None):
        """Initialize cleaner with optional dataframe"""
        self.df = df
        self.cleaning_report = {}
    
    def load_from_dict_list(self, data_list):
        """Load data from list of dictionaries"""
        self.df = pd.DataFrame(data_list)
        logger.info(f"Loaded {len(self.df)} records")
        return self
    
    def remove_duplicates(self):
        """Remove duplicate transactions"""
        initial_count = len(self.df)
        self.df = self.df.drop_duplicates(subset=['transaction_id'], keep='first')
        removed = initial_count - len(self.df)
        self.cleaning_report['duplicates_removed'] = removed
        logger.info(f"Removed {removed} duplicates")
        return self
    
    def handle_missing_values(self):
        """Handle missing values"""
        missing_before = self.df.isnull().sum().sum()
        
        if 'amount' in self.df.columns:
            self.df['amount'].fillna(0, inplace=True)
        
        if 'status' in self.df.columns:
            self.df['status'].fillna('pending', inplace=True)
        
        self.df = self.df.dropna(subset=['transaction_id', 'sender', 'receiver'])
        
        missing_after = self.df.isnull().sum().sum()
        self.cleaning_report['missing_values_handled'] = missing_before - missing_after
        logger.info(f"Handled {missing_before - missing_after} missing values")
        return self
    
    def standardize_columns(self):
        """Standardize column names and formats"""
        self.df.columns = self.df.columns.str.lower().str.strip()
        
        if 'sender' in self.df.columns:
            self.df['sender'] = self.df['sender'].astype(str).str.strip()
        if 'receiver' in self.df.columns:
            self.df['receiver'] = self.df['receiver'].astype(str).str.strip()
        
        if 'transaction_type' in self.df.columns:
            self.df['transaction_type'] = self.df['transaction_type'].str.lower().str.strip()
        
        if 'status' in self.df.columns:
            self.df['status'] = self.df['status'].str.lower().str.strip()
        
        logger.info("Standardized column names and values")
        return self
    
    def convert_data_types(self):
        """Convert data types appropriately"""
        if 'amount' in self.df.columns:
            self.df['amount'] = pd.to_numeric(self.df['amount'], errors='coerce')
        
        if 'fee' in self.df.columns:
            self.df['fee'] = pd.to_numeric(self.df['fee'], errors='coerce').fillna(0)
        
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
        
        logger.info("Converted data types")
        return self
    
    def validate_required_fields(self):
        """Validate that required fields are present"""
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in self.df.columns]
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
        
        self.cleaning_report['required_fields_present'] = len(missing_fields) == 0
        return self
    
    def remove_invalid_records(self):
        """Remove records with invalid data"""
        initial_count = len(self.df)
        
        if 'amount' in self.df.columns:
            self.df = self.df[self.df['amount'] > 0]
        
        if 'sender' in self.df.columns:
            self.df = self.df[self.df['sender'].str.len() >= 10]
        if 'receiver' in self.df.columns:
            self.df = self.df[self.df['receiver'].str.len() >= 10]
        
        removed = initial_count - len(self.df)
        self.cleaning_report['invalid_records_removed'] = removed
        logger.info(f"Removed {removed} invalid records")
        return self
    
    def get_cleaned_data(self):
        """Return cleaned dataframe"""
        return self.df.reset_index(drop=True)
    
    def get_cleaning_report(self):
        """Return cleaning report"""
        self.cleaning_report['final_record_count'] = len(self.df)
        return self.cleaning_report
    
    def clean(self):
        """Execute complete cleaning pipeline"""
        logger.info("Starting data cleaning pipeline...")
        
        self.remove_duplicates() \
            .handle_missing_values() \
            .standardize_columns() \
            .convert_data_types() \
            .validate_required_fields() \
            .remove_invalid_records()
        
        logger.info(f"Cleaning completed. Records: {len(self.df)}")
        return self

def clean_transactions(data):
    """Main cleaning function"""
    logger.info("Cleaning transaction data...")
    
    if isinstance(data, pd.DataFrame):
        df = data
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        logger.error("Invalid data format")
        return pd.DataFrame()
    
    cleaner = TransactionCleaner(df)
    cleaner.clean()
    
    return cleaner.get_cleaned_data()
