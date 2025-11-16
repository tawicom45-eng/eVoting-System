"""
Unit tests for extract module
"""

import unittest
import pandas as pd
from etl.extract import extract_from_csv, extract_data

class TestExtract(unittest.TestCase):
    """Test cases for data extraction"""
    
    def test_extract_data_returns_dataframe(self):
        """Test that extract_data returns a dataframe"""
        result = extract_data()
        self.assertIsInstance(result, pd.DataFrame)
    
    def test_extract_from_csv_with_invalid_path(self):
        """Test extract_from_csv with invalid file path"""
        result = extract_from_csv('nonexistent_file.csv')
        self.assertTrue(result.empty)
    
    def test_extract_from_csv_returns_dataframe(self):
        """Test that extract_from_csv returns a dataframe"""
        result = extract_from_csv('dummy.csv')
        self.assertIsInstance(result, pd.DataFrame)

if __name__ == '__main__':
    unittest.main()
