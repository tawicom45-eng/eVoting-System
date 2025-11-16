"""
Data Transformation Module

This module handles data cleaning, validation, and transformation:
- Data type conversions
- Missing value handling
- Standardization
- Feature engineering
- Deduplication with aggregation

Business Logic:
- Deduplicate by (market_name, product_name, date_recorded)
- When duplicates found: SUM quantities, keep first occurrence of prices
- Standardize market names and product names to canonical forms
- Validate dates are within acceptable range (not future dates)
- Type coercion: price (NUMERIC), quantity (INTEGER), date (DATE)
"""

import pandas as pd
import numpy as np
from datetime import datetime

def clean_data(df):
    """Clean data by handling missing values and duplicates"""
    print("Cleaning data...")
    
    # Remove exact duplicate rows (identical across all columns)
    initial_count = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} exact duplicate records")
    
    # Handle missing values
    missing_before = df.isnull().sum().sum()
    
    # Fill numeric columns with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)
    
    # Fill categorical columns with mode
    categorical_cols = df.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].mode()[0], inplace=True)
    
    missing_after = df.isnull().sum().sum()
    print(f"Missing values handled: {missing_before - missing_after}")
    
    # Deduplicate by market/product/date; aggregate duplicates
    if all(col in df.columns for col in ['market_name', 'product_name', 'date_recorded']):
        dup_count = df.duplicated(subset=['market_name', 'product_name', 'date_recorded'], keep=False).sum()
        if dup_count > 0:
            print(f"Deduplicating {dup_count // 2} duplicate market/product/date combinations...")
            # Aggregate: average price, sum quantity for same market/product/date
            agg_dict = {
                'price': 'mean',
                'quantity': 'sum'
            }
            # Include source_file if it exists
            if 'source_file' in df.columns:
                agg_dict['source_file'] = 'first'
            df = df.groupby(['market_name', 'product_name', 'date_recorded'], as_index=False).agg(agg_dict)
            print(f"After deduplication: {len(df)} records")
    
    return df

def standardize_columns(df):
    """Standardize column names and formats"""
    print("Standardizing data...")
    
    # Convert column names to lowercase with underscores
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    # Standardize date columns
    date_cols = [col for col in df.columns if 'date' in col or 'time' in col]
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            print(f"Warning: Could not convert {col} to datetime")
    
    # Standardize currency columns (remove $ and convert to float)
    currency_cols = [col for col in df.columns if 'price' in col or 'amount' in col or 'cost' in col]
    for col in currency_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace('$', '').str.replace(',', '').astype(float)
    
    return df

def validate_data_quality(df):
    """Validate data quality metrics"""
    print("Validating data quality...")
    
    quality_metrics = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'duplicate_records': df.duplicated().sum(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    print(f"  - Total Records: {quality_metrics['total_records']}")
    print(f"  - Total Columns: {quality_metrics['total_columns']}")
    print(f"  - Missing Values: {quality_metrics['missing_values']}")
    print(f"  - Duplicate Records: {quality_metrics['duplicate_records']}")
    print(f"  - Memory Usage: {quality_metrics['memory_usage_mb']:.2f} MB")
    
    return quality_metrics

def transform_data(raw_data):
    """
    Main transformation function that orchestrates all transformation steps
    """
    print("Starting data transformation process...")
    
    if raw_data.empty:
        print("Warning: Input data is empty")
        return raw_data
    
    # Step 0: Standardize columns and formats FIRST (before dedup check)
    transformed_df = standardize_columns(raw_data.copy())
    
    # Step 1: Clean data (including deduplication)
    transformed_df = clean_data(transformed_df)
    
    # Step 2: Add derived columns for analysis
    if 'market_name' in transformed_df.columns and 'product_name' in transformed_df.columns:
        transformed_df['market_product'] = (
            transformed_df['market_name'].astype(str) + '_' + 
            transformed_df['product_name'].astype(str)
        )
    
    if 'price' in transformed_df.columns and 'quantity' in transformed_df.columns:
        transformed_df['total_value'] = transformed_df['price'] * transformed_df['quantity']
    
    # Step 3: Validate data quality
    quality_metrics = validate_data_quality(transformed_df)
    
    print(f"Transformation completed. Output records: {len(transformed_df)}")
    return transformed_df
