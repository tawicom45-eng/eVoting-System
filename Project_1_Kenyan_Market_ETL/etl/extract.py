"""
Data Extraction Module

This module handles data extraction from multiple sources including:
- CSV files from Kenyan market data providers (daily price reports)
- APIs for market data feeds
- Databases for historical records

Business Context:
- Kenyan markets (Nairobi, Mombasa, Kisumu) report daily commodity prices
- Sources: Ministry of Agriculture, trader associations, market reporters
- Data arrives via CSV, APIs, or database dumps with duplicates
- Key commodities: maize, tomatoes, beans, onions tracked across regions
"""

import pandas as pd
import os
from pathlib import Path

def extract_from_csv(file_path):
    """Extract data from CSV file"""
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully extracted {len(df)} records from {file_path}")
        return df
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return pd.DataFrame()

def extract_from_api(endpoint, params=None):
    """Extract data from API endpoint"""
    import requests
    
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        print(f"Successfully extracted {len(df)} records from API")
        return df
    except requests.RequestException as e:
        print(f"Error fetching from API: {str(e)}")
        return pd.DataFrame()

def extract_from_database(connection, query):
    """Extract data from database using SQL query"""
    try:
        df = pd.read_sql(query, connection)
        print(f"Successfully extracted {len(df)} records from database")
        return df
    except Exception as e:
        print(f"Error reading from database: {str(e)}")
        return pd.DataFrame()

def extract_data():
    """
    Main extraction function that combines data from multiple sources
    Returns consolidated dataframe with all extracted data
    """
    print("Starting data extraction process...")
    
    all_data = []
    
    # Extract from CSV files in 'data/raw' and from any CSVs in 'data/' (including sample files)
    csv_dirs = ["data/raw", "data"]
    for csv_dir in csv_dirs:
        if os.path.exists(csv_dir):
            for file in Path(csv_dir).glob("*.csv"):
                df = extract_from_csv(str(file))
                if not df.empty:
                    all_data.append(df)
    
    # Combine all extracted data
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"Total records extracted: {len(combined_df)}")
        return combined_df
    else:
        print("No data extracted from sources")
        return pd.DataFrame()
