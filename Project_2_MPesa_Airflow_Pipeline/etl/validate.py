"""
Data Validation Module

Implements business rule validation for transaction data including:
- Amount range validation
- Status validation
- Fraud detection rules
- Data quality checks
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class TransactionValidator:
    """Validate transactions against business rules"""
    
    MIN_AMOUNT = 1
    MAX_AMOUNT = 1000000
    VALID_STATUSES = ['success', 'failed', 'pending', 'reversed']
    VALID_TYPES = ['transfer', 'withdrawal', 'deposit', 'payment', 'airtime_purchase']
    
    def __init__(self, df):
        """Initialize validator with dataframe"""
        self.df = df
        self.validation_results = {
            'total_records': len(df),
            'valid_records': 0,
            'invalid_records': 0,
            'warnings': [],
            'errors': [],
            'anomalies': []
        }
    
    def validate_amount_range(self):
        """Validate transaction amounts are within acceptable range"""
        logger.info("Validating amount ranges...")
        
        invalid_amounts = self.df[
            (self.df['amount'] < self.MIN_AMOUNT) | 
            (self.df['amount'] > self.MAX_AMOUNT)
        ]
        
        if len(invalid_amounts) > 0:
            msg = f"Found {len(invalid_amounts)} transactions with invalid amounts"
            self.validation_results['warnings'].append(msg)
            logger.warning(msg)
        
        return len(invalid_amounts) == 0
    
    def validate_status_values(self):
        """Validate status values are from allowed set"""
        logger.info("Validating status values...")
        
        invalid_status = self.df[~self.df['status'].isin(self.VALID_STATUSES)]
        
        if len(invalid_status) > 0:
            msg = f"Found {len(invalid_status)} transactions with invalid status"
            self.validation_results['errors'].append(msg)
            logger.error(msg)
            return False
        
        return True
    
    def validate_transaction_types(self):
        """Validate transaction types are from allowed set"""
        logger.info("Validating transaction types...")
        
        if 'transaction_type' not in self.df.columns:
            return True
        
        invalid_types = self.df[~self.df['transaction_type'].isin(self.VALID_TYPES)]
        
        if len(invalid_types) > 0:
            msg = f"Found {len(invalid_types)} transactions with invalid type"
            self.validation_results['warnings'].append(msg)
            logger.warning(msg)
        
        return True
    
    def validate_phone_numbers(self):
        """Validate phone numbers have minimum length"""
        logger.info("Validating phone numbers...")
        
        invalid_sender = self.df[self.df['sender'].str.len() < 10]
        invalid_receiver = self.df[self.df['receiver'].str.len() < 10]
        
        invalid_count = len(invalid_sender) + len(invalid_receiver)
        
        if invalid_count > 0:
            msg = f"Found {invalid_count} transactions with invalid phone numbers"
            self.validation_results['errors'].append(msg)
            logger.error(msg)
            return False
        
        return True
    
    def detect_anomalies(self):
        """Detect statistical anomalies in transactions"""
        logger.info("Detecting anomalies...")
        
        anomaly_count = 0
        
        mean_amount = self.df['amount'].mean()
        std_amount = self.df['amount'].std()
        threshold = mean_amount + (3 * std_amount)
        
        high_value_txns = self.df[self.df['amount'] > threshold]
        if len(high_value_txns) > 0:
            anomaly_count += len(high_value_txns)
            msg = f"Found {len(high_value_txns)} high-value anomalies (>${threshold:.2f})"
            self.validation_results['anomalies'].append(msg)
            logger.info(msg)
        
        failed_txns = self.df[self.df['status'] == 'failed']
        if len(failed_txns) > 0:
            failure_rate = (len(failed_txns) / len(self.df)) * 100
            if failure_rate > 10:
                msg = f"High failure rate detected: {failure_rate:.2f}%"
                self.validation_results['anomalies'].append(msg)
                logger.warning(msg)
                anomaly_count += 1
        
        return anomaly_count
    
    def validate_completeness(self):
        """Validate data completeness"""
        logger.info("Validating data completeness...")
        
        required_fields = ['transaction_id', 'sender', 'receiver', 'amount', 'status']
        missing_values = self.df[required_fields].isnull().sum().sum()
        
        if missing_values > 0:
            msg = f"Found {missing_values} missing values in required fields"
            self.validation_results['errors'].append(msg)
            logger.error(msg)
            return False
        
        return True
    
    def validate(self):
        """Execute complete validation pipeline"""
        logger.info("Starting validation pipeline...")
        
        all_valid = True
        
        all_valid &= self.validate_completeness()
        all_valid &= self.validate_phone_numbers()
        all_valid &= self.validate_status_values()
        all_valid &= self.validate_amount_range()
        all_valid &= self.validate_transaction_types()
        
        self.detect_anomalies()
        
        self.validation_results['valid_records'] = len(self.df) - len(self.validation_results['errors'])
        self.validation_results['invalid_records'] = len(self.validation_results['errors'])
        self.validation_results['validation_passed'] = all_valid
        
        logger.info(f"Validation completed. Valid: {self.validation_results['valid_records']}")
        
        return all_valid
    
    def get_results(self):
        """Return validation results"""
        return self.validation_results

def validate_transactions(data):
    """Main validation function"""
    logger.info("Validating transaction data...")
    
    if isinstance(data, pd.DataFrame):
        df = data
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        logger.error("Invalid data format")
        return False
    
    validator = TransactionValidator(df)
    is_valid = validator.validate()
    
    return is_valid
