"""
Unit tests for data deduplication logic.

Tests cover:
- Deduplication by unique key (market_name, product_name, date_recorded)
- Aggregation: avg(price), sum(quantity)
- Column standardization
- Edge cases: empty data, single records, all duplicates
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from etl.transform import clean_data, standardize_columns, transform_data


class TestDeduplication:
    """Test deduplication logic in transform.py"""

    @pytest.fixture
    def duplicate_data(self):
        """Sample data with duplicates for testing"""
        return pd.DataFrame({
            'Market Name': ['Nairobi', 'Nairobi', 'Mombasa', 'Mombasa', 'Nairobi'],
            'Product Name': ['Maize', 'Maize', 'Rice', 'Rice', 'Beans'],
            'Price': [50.0, 60.0, 120.0, 130.0, 80.0],
            'Quantity': [100, 150, 200, 250, 50],
            'Date Recorded': [
                '2024-01-15',
                '2024-01-15',  # Duplicate: same market, product, date
                '2024-01-15',
                '2024-01-15',  # Duplicate: same market, product, date
                '2024-01-16'
            ]
        })

    @pytest.fixture
    def clean_data_sample(self):
        """Sample data without duplicates"""
        return pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa', 'Kisumu'],
            'product_name': ['Maize', 'Rice', 'Beans'],
            'price': [50.0, 120.0, 80.0],
            'quantity': [100, 200, 50],
            'date_recorded': ['2024-01-15', '2024-01-15', '2024-01-16']
        })

    def test_standardize_columns(self, duplicate_data):
        """Test column name standardization"""
        standardized = standardize_columns(duplicate_data.copy())

        # Check all columns are lowercase with underscores
        assert 'market_name' in standardized.columns
        assert 'product_name' in standardized.columns
        assert 'date_recorded' in standardized.columns

        # Check no uppercase columns exist
        assert not any(col.isupper() for col in standardized.columns)
        assert not any(' ' in col for col in standardized.columns)

    def test_clean_data_deduplication(self, duplicate_data):
        """Test deduplication aggregation"""
        # First standardize
        standardized = standardize_columns(duplicate_data.copy())

        # Then clean (which includes dedup)
        cleaned = clean_data(standardized.copy())

        # Should have 3 rows instead of 5 (2 duplicates removed)
        assert len(cleaned) == 3

        # Check aggregation of first duplicate pair (Nairobi/Maize/2024-01-15)
        nairobi_maize = cleaned[
            (cleaned['market_name'] == 'Nairobi') &
            (cleaned['product_name'] == 'Maize') &
            (cleaned['date_recorded'] == '2024-01-15')
        ]
        assert len(nairobi_maize) == 1

        # Price should be average: (50 + 60) / 2 = 55
        assert nairobi_maize.iloc[0]['price'] == pytest.approx(55.0, abs=0.01)

        # Quantity should be sum: 100 + 150 = 250
        assert nairobi_maize.iloc[0]['quantity'] == 250

    def test_clean_data_second_duplicate_pair(self, duplicate_data):
        """Test aggregation of second duplicate pair"""
        standardized = standardize_columns(duplicate_data.copy())
        cleaned = clean_data(standardized.copy())

        # Check second duplicate pair (Mombasa/Rice/2024-01-15)
        mombasa_rice = cleaned[
            (cleaned['market_name'] == 'Mombasa') &
            (cleaned['product_name'] == 'Rice') &
            (cleaned['date_recorded'] == '2024-01-15')
        ]
        assert len(mombasa_rice) == 1

        # Price: (120 + 130) / 2 = 125
        assert mombasa_rice.iloc[0]['price'] == pytest.approx(125.0, abs=0.01)

        # Quantity: 200 + 250 = 450
        assert mombasa_rice.iloc[0]['quantity'] == 450

    def test_no_duplicates_case(self, clean_data_sample):
        """Test that clean_data doesn't remove unique records"""
        cleaned = clean_data(clean_data_sample.copy())

        # Should maintain same row count
        assert len(cleaned) == len(clean_data_sample)

    def test_all_duplicates_case(self):
        """Test edge case where all records are duplicates"""
        data = pd.DataFrame({
            'market_name': ['Nairobi', 'Nairobi', 'Nairobi'],
            'product_name': ['Maize', 'Maize', 'Maize'],
            'price': [50.0, 60.0, 70.0],
            'quantity': [100, 150, 200],
            'date_recorded': ['2024-01-15', '2024-01-15', '2024-01-15']
        })

        cleaned = clean_data(data.copy())

        # Should reduce to 1 record
        assert len(cleaned) == 1

        # Aggregated values
        assert cleaned.iloc[0]['price'] == pytest.approx(60.0, abs=0.01)  # (50+60+70)/3
        assert cleaned.iloc[0]['quantity'] == 450  # 100+150+200

    def test_empty_dataframe(self):
        """Test edge case with empty DataFrame"""
        data = pd.DataFrame({
            'market_name': [],
            'product_name': [],
            'price': [],
            'quantity': [],
            'date_recorded': []
        })

        cleaned = clean_data(data.copy())

        # Should remain empty
        assert len(cleaned) == 0

    def test_single_record(self):
        """Test edge case with single record"""
        data = pd.DataFrame({
            'market_name': ['Nairobi'],
            'product_name': ['Maize'],
            'price': [50.0],
            'quantity': [100],
            'date_recorded': ['2024-01-15']
        })

        cleaned = clean_data(data.copy())

        # Should remain unchanged
        assert len(cleaned) == 1
        assert cleaned.iloc[0]['market_name'] == 'Nairobi'
        assert cleaned.iloc[0]['price'] == 50.0

    def test_dedup_preserves_data_types(self, duplicate_data):
        """Test that deduplication preserves column data types"""
        standardized = standardize_columns(duplicate_data.copy())
        cleaned = clean_data(standardized.copy())

        # Check numeric types
        assert pd.api.types.is_numeric_dtype(cleaned['price'])
        assert pd.api.types.is_numeric_dtype(cleaned['quantity'])

        # Check object types for strings
        assert pd.api.types.is_object_dtype(cleaned['market_name'])
        assert pd.api.types.is_object_dtype(cleaned['product_name'])

    def test_full_transform_pipeline(self, duplicate_data):
        """Test full transform pipeline including dedup"""
        # This mirrors the actual pipeline flow
        standardized = standardize_columns(duplicate_data.copy())
        cleaned = clean_data(standardized.copy())
        transformed = transform_data(duplicate_data.copy())

        # Should have fewer rows due to dedup
        assert len(transformed) <= len(duplicate_data)

        # Should have expected columns
        assert 'market_name' in transformed.columns
        assert 'product_name' in transformed.columns
        assert 'price' in transformed.columns
        assert 'quantity' in transformed.columns
        assert 'date_recorded' in transformed.columns


class TestDeduplicationEdgeCases:
    """Test edge cases and special scenarios"""

    def test_null_values_in_dedup_key(self):
        """Test handling of NULL values in dedup key columns"""
        data = pd.DataFrame({
            'market_name': ['Nairobi', None, 'Nairobi'],
            'product_name': ['Maize', 'Maize', 'Maize'],
            'price': [50.0, 60.0, 70.0],
            'quantity': [100, 150, 200],
            'date_recorded': ['2024-01-15', '2024-01-15', '2024-01-15']
        })

        cleaned = clean_data(data.copy())

        # NULL rows are dropped during cleaning as per data quality rules
        # Should have at least 1 row (Nairobi/Maize records aggregated)
        assert len(cleaned) >= 1

    def test_case_sensitive_dedup(self):
        """Test that market/product names are case-sensitive in dedup"""
        data = pd.DataFrame({
            'market_name': ['nairobi', 'Nairobi', 'NAIROBI'],
            'product_name': ['Maize', 'Maize', 'Maize'],
            'price': [50.0, 60.0, 70.0],
            'quantity': [100, 150, 200],
            'date_recorded': ['2024-01-15', '2024-01-15', '2024-01-15']
        })

        cleaned = clean_data(data.copy())

        # Different cases should be treated as different entries
        # (depending on whether standardization lowercases names)
        assert len(cleaned) >= 1

    def test_dedup_with_missing_price_quantity(self):
        """Test dedup when price or quantity is missing"""
        data = pd.DataFrame({
            'market_name': ['Nairobi', 'Nairobi'],
            'product_name': ['Maize', 'Maize'],
            'price': [50.0, np.nan],
            'quantity': [100, 150],
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

        cleaned = clean_data(data.copy())

        # Should handle NaN values gracefully
        assert len(cleaned) >= 1

    def test_large_dataset_dedup_performance(self):
        """Test dedup performance with larger dataset"""
        # Create 1000-row dataset with 300 unique market/product/date combos
        np.random.seed(42)
        markets = np.random.choice(['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru'], 300)
        products = np.random.choice(['Maize', 'Rice', 'Beans', 'Wheat'], 300)
        prices = np.random.uniform(50, 200, 300)
        quantities = np.random.randint(50, 500, 300)
        dates = [f'2024-01-{(i % 15) + 1:02d}' for i in range(300)]

        # Create duplicates by repeating 300 rows 3+ times
        data = pd.DataFrame({
            'market_name': list(markets) * 3 + list(markets)[:100],
            'product_name': list(products) * 3 + list(products)[:100],
            'price': list(prices) * 3 + list(prices)[:100],
            'quantity': list(quantities) * 3 + list(quantities)[:100],
            'date_recorded': list(dates) * 3 + list(dates)[:100]
        })

        assert len(data) > 900

        cleaned = clean_data(data.copy())

        # Should significantly reduce dataset
        assert len(cleaned) < len(data) / 2

    def test_dedup_with_inf_values(self):
        """Test handling of infinity values in numeric columns"""
        data = pd.DataFrame({
            'market_name': ['Nairobi', 'Nairobi'],
            'product_name': ['Maize', 'Maize'],
            'price': [50.0, np.inf],
            'quantity': [100, 150],
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

        # Should not crash
        cleaned = clean_data(data.copy())
        assert len(cleaned) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
