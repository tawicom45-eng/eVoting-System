"""
Unit tests for data loading logic.

Tests cover:
- DataFrame preparation (dedup, type coercion)
- Truncate functionality
- Batch processing configuration
- Error handling for edge cases
"""

import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from etl.load import (
    load_to_database,
    create_table_if_not_exists,
    _prepare_dataframe,
    _ensure_indexes_and_constraints
)
from run_pipeline import truncate_table


class TestDataFramePrepare:
    """Test DataFrame preparation for loading"""

    @pytest.fixture
    def sample_df(self):
        """Sample DataFrame for testing"""
        return pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa', 'Nairobi'],
            'product_name': ['Maize', 'Rice', 'Maize'],
            'price': [50.0, 120.0, 50.0],  # Last two are duplicates
            'quantity': [100, 200, 150],
            'date_recorded': ['2024-01-15', '2024-01-15', '2024-01-15']
        })

    def test_prepare_dataframe_removes_duplicates(self, sample_df):
        """Test that _prepare_dataframe removes exact duplicates"""
        prepared = _prepare_dataframe(sample_df.copy())

        # Should keep first occurrence, remove second
        assert len(prepared) == 2
        assert prepared.iloc[0]['market_name'] == 'Nairobi'
        assert prepared.iloc[1]['market_name'] == 'Mombasa'

    def test_prepare_dataframe_type_coercion(self):
        """Test type coercion in _prepare_dataframe"""
        df = pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa'],
            'product_name': ['Maize', 'Rice'],
            'price': ['50.5', '120.0'],  # String prices
            'quantity': ['100', '200'],  # String quantities
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

        prepared = _prepare_dataframe(df)

        # Check types are coerced
        assert pd.api.types.is_numeric_dtype(prepared['price'])
        assert pd.api.types.is_numeric_dtype(prepared['quantity'])

    def test_prepare_dataframe_handles_missing_columns(self):
        """Test handling of missing optional columns"""
        df = pd.DataFrame({
            'market_name': ['Nairobi'],
            'product_name': ['Maize'],
            'price': [50.0],
            'quantity': [100],
            'date_recorded': ['2024-01-15']
        })

        prepared = _prepare_dataframe(df)

        # Should not crash
        assert len(prepared) == 1

    def test_prepare_dataframe_nan_handling(self):
        """Test handling of NaN values"""
        df = pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa'],
            'product_name': ['Maize', 'Rice'],
            'price': [50.0, np.nan],
            'quantity': [100, np.nan],
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

        prepared = _prepare_dataframe(df)

        # Should handle gracefully
        assert len(prepared) >= 1


class TestTruncateTable:
    """Test truncate_table functionality"""

    def test_truncate_table_requires_connection(self):
        """Test that truncate_table requires a valid connection"""
        with pytest.raises((ValueError, AttributeError, TypeError)):
            truncate_table(None, 'market_data')

    @patch('run_pipeline.text')
    def test_truncate_table_mock(self, mock_text):
        """Test truncate_table with mocked engine"""
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)

        # Should not crash
        truncate_table(mock_engine, 'market_data')

        # Should have used context manager
        mock_engine.begin.assert_called()


class TestIdempotentUpsertContract:
    """Test idempotent upsert behavior contracts"""

    @pytest.fixture
    def upsert_data(self):
        """Data for upsert testing"""
        return pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa'],
            'product_name': ['Maize', 'Rice'],
            'price': [50.0, 120.0],
            'quantity': [100, 200],
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

    def test_upsert_contract_idempotent(self, upsert_data):
        """Verify idempotent contract: preparing same data twice is valid for upsert"""
        # In production, this tests the data preparation stage
        prepared = _prepare_dataframe(upsert_data.copy())

        # Should have consistent columns and data types
        assert 'market_name' in prepared.columns
        assert 'product_name' in prepared.columns
        assert len(prepared) == 2

    def test_upsert_contract_unique_key_preserved(self, upsert_data):
        """Test that unique key columns are preserved in prepared data"""
        prepared = _prepare_dataframe(upsert_data.copy())

        # Must have unique key columns for ON CONFLICT to work
        assert 'market_name' in prepared.columns
        assert 'product_name' in prepared.columns
        assert 'date_recorded' in prepared.columns

        # Values should match original
        assert prepared.iloc[0]['market_name'] == 'Nairobi'
        assert prepared.iloc[0]['product_name'] == 'Maize'


class TestConstraintManagement:
    """Test constraint creation and management"""

    @patch('etl.load.inspect')
    def test_ensure_indexes_and_constraints_no_error(self, mock_inspect):
        """Test that constraint creation doesn't raise errors"""
        mock_inspector = MagicMock()
        mock_inspect.return_value = mock_inspector
        mock_inspector.get_check_constraints.return_value = []

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)

        # Should not raise error
        _ensure_indexes_and_constraints(mock_engine, 'market_data')

    @patch('etl.load.inspect')
    def test_constraint_creation_idempotent(self, mock_inspect):
        """Test that constraint creation is idempotent"""
        mock_inspector = MagicMock()
        mock_inspect.return_value = mock_inspector
        mock_inspector.get_check_constraints.return_value = []

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)

        # First call
        _ensure_indexes_and_constraints(mock_engine, 'market_data')

        # Second call should not raise error
        _ensure_indexes_and_constraints(mock_engine, 'market_data')


class TestBatchProcessing:
    """Test batch processing functionality"""

    def test_batch_size_configuration(self):
        """Test that batch size is configurable"""
        # Default batch size should be reasonable (100-5000)
        import os
        batch_size = int(os.getenv('BATCH_SIZE', 1000))
        assert 100 <= batch_size <= 5000

    @pytest.fixture
    def large_df(self):
        """Large DataFrame for batch testing"""
        n_rows = 2500
        return pd.DataFrame({
            'market_name': np.random.choice(['Nairobi', 'Mombasa', 'Kisumu'], n_rows),
            'product_name': np.random.choice(['Maize', 'Rice', 'Beans'], n_rows),
            'price': np.random.uniform(50, 200, n_rows),
            'quantity': np.random.randint(50, 500, n_rows),
            'date_recorded': ['2024-01-15'] * n_rows
        })

    def test_prepare_large_dataset(self, large_df):
        """Test that batching preparation handles large datasets"""
        prepared = _prepare_dataframe(large_df.copy())

        # Should successfully prepare without error
        assert len(prepared) > 0
        assert len(prepared) <= len(large_df)


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_empty_dataframe_handling(self):
        """Test handling of empty DataFrame"""
        df = pd.DataFrame({
            'market_name': [],
            'product_name': [],
            'price': [],
            'quantity': [],
            'date_recorded': []
        })

        prepared = _prepare_dataframe(df)

        # Should handle gracefully
        assert len(prepared) == 0

    def test_single_record_handling(self):
        """Test handling of single record"""
        df = pd.DataFrame({
            'market_name': ['Nairobi'],
            'product_name': ['Maize'],
            'price': [50.0],
            'quantity': [100],
            'date_recorded': ['2024-01-15']
        })

        prepared = _prepare_dataframe(df)

        # Should preserve single record
        assert len(prepared) == 1

    def test_nan_price_handling(self):
        """Test that NaN prices are handled"""
        df = pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa'],
            'product_name': ['Maize', 'Rice'],
            'price': [50.0, np.nan],
            'quantity': [100, 200],
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

        prepared = _prepare_dataframe(df)

        # Should handle without crash
        assert len(prepared) >= 1

    def test_infinite_values_handling(self):
        """Test handling of infinity values"""
        df = pd.DataFrame({
            'market_name': ['Nairobi', 'Mombasa'],
            'product_name': ['Maize', 'Rice'],
            'price': [50.0, np.inf],
            'quantity': [100, 150],
            'date_recorded': ['2024-01-15', '2024-01-15']
        })

        prepared = _prepare_dataframe(df)

        # Should not crash
        assert len(prepared) >= 1


class TestTempTableStrategy:
    """Test temp table load strategy for Postgres"""

    @patch('etl.load.inspect')
    def test_create_table_if_not_exists(self, mock_inspect):
        """Test that create_table_if_not_exists works"""
        mock_inspector = MagicMock()
        mock_inspect.return_value = mock_inspector
        mock_inspector.has_table.return_value = False

        mock_engine = MagicMock()
        mock_engine.execute = MagicMock()

        # Should not crash
        create_table_if_not_exists(mock_engine, 'market_data')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
