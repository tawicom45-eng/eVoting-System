"""
Integration tests for Project 2 M-Pesa Pipeline
"""

import unittest
import pandas as pd
import json
from datetime import datetime
from generator.transaction_generator import TransactionGenerator
from etl.clean import TransactionCleaner
from etl.validate import TransactionValidator

class TestMPesaPipeline(unittest.TestCase):
    """Integration tests for M-Pesa pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = TransactionGenerator()
        self.transactions = self.generator.generate_transactions(count=100)
    
    def test_transaction_generation(self):
        """Test transaction generation"""
        self.assertEqual(len(self.transactions), 100)
        self.assertIn('transaction_id', self.transactions[0])
        self.assertIn('sender', self.transactions[0])
        self.assertIn('amount', self.transactions[0])
    
    def test_data_cleaning(self):
        """Test data cleaning pipeline"""
        df = pd.DataFrame(self.transactions)
        cleaner = TransactionCleaner(df)
        cleaner.clean()
        
        cleaned_data = cleaner.get_cleaned_data()
        self.assertGreater(len(cleaned_data), 0)
        self.assertNotIn(None, cleaned_data['transaction_id'])
    
    def test_data_validation(self):
        """Test data validation"""
        df = pd.DataFrame(self.transactions)
        validator = TransactionValidator(df)
        is_valid = validator.validate()
        
        results = validator.get_results()
        self.assertIn('validation_passed', results)

if __name__ == '__main__':
    unittest.main()
