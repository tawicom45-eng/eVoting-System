"""
Configuration for Project 2 tests
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_transactions():
    """Provide sample transactions for testing"""
    from generator.transaction_generator import TransactionGenerator
    generator = TransactionGenerator()
    return generator.generate_transactions(count=50)

@pytest.fixture
def sample_dataframe(sample_transactions):
    """Provide sample dataframe for testing"""
    import pandas as pd
    return pd.DataFrame(sample_transactions)
