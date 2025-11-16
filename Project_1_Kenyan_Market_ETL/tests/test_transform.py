"""
Unit tests for transform module
"""

import unittest
import pandas as pd
from etl.transform import clean_data, standardize_columns, transform_data

class TestTransform(unittest.TestCase):
    """Test cases for data transformation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data = pd.DataFrame({
            'Market Name': ['Nairobi', 'Mombasa', 'Nairobi'],
            'Product Name': ['Maize', 'Rice', 'Maize'],
            'Price': [50.0, 60.0, 50.0],
            'Quantity': [100, 200, 150]
        })
    
    def test_clean_data_removes_duplicates(self):
        """Test that clean_data removes duplicates"""
        df_with_duplicates = pd.concat([self.sample_data, self.sample_data.iloc[0:1]])
        result = clean_data(df_with_duplicates)
        self.assertEqual(len(result), len(self.sample_data))
    
    def test_standardize_columns_lowercases_names(self):
        """Test that standardize_columns converts to lowercase"""
        result = standardize_columns(self.sample_data)
        assert 'market_name' in result.columns
        assert 'product_name' in result.columns
    
    def test_transform_data_returns_dataframe(self):
        """Test that transform_data returns a dataframe"""
        result = transform_data(self.sample_data)
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_transform_data_handles_empty_dataframe(self):
        """Test that transform_data handles empty dataframe"""
        empty_df = pd.DataFrame()
        result = transform_data(empty_df)
        self.assertTrue(result.empty)

if __name__ == '__main__':
    unittest.main()
