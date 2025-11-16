"""Pytest configuration for Project 4 tests"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_engine():
    """Mock SQLAlchemy engine"""
    engine = Mock()
    return engine

@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002', 'TXN003'],
        'sender': ['254712345678', '254712345679', '254712345680'],
        'receiver': ['254712345681', '254712345682', '254712345683'],
        'amount': [1000.00, 2500.00, 1500.00],
        'timestamp': ['2024-01-01T10:00:00', '2024-01-02T11:00:00', '2024-01-03T12:00:00'],
        'transaction_type': ['transfer', 'withdrawal', 'deposit'],
        'status': ['success', 'success', 'failed']
    })

@pytest.fixture
def sample_dim_date():
    """Sample date dimension data"""
    return pd.DataFrame({
        'full_date': pd.date_range('2024-01-01', periods=5),
        'year': [2024, 2024, 2024, 2024, 2024],
        'month': [1, 1, 1, 1, 1],
        'day': [1, 2, 3, 4, 5],
        'quarter': [1, 1, 1, 1, 1],
        'week_of_year': [1, 1, 1, 1, 1],
        'day_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'is_weekend': [False, False, False, False, False],
        'is_holiday': [False, False, False, False, False]
    })

@pytest.fixture
def sample_dim_customer():
    """Sample customer dimension data"""
    return pd.DataFrame({
        'customer_key': ['254712345678', '254712345679', '254712345680'],
        'customer_name': ['Customer_254712345678', 'Customer_254712345679', 'Customer_254712345680'],
        'phone_number': ['254712345678', '254712345679', '254712345680'],
        'email': ['254712345678@safaricom.com', '254712345679@safaricom.com', '254712345680@safaricom.com'],
        'registration_date': ['2024-01-01', '2024-01-01', '2024-01-01'],
        'account_type': ['Premium', 'Premium', 'Premium'],
        'status': ['Active', 'Active', 'Active']
    })
