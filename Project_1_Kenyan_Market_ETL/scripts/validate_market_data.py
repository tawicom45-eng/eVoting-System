#!/usr/bin/env python3
"""
Quick CSV validator for the generated market data.

Usage:
    python scripts/validate_market_data.py data/sample_market_data.csv
"""
import sys
import csv
from collections import Counter
from datetime import datetime


def validate(path):
    counts = 0
    markets = Counter()
    products = Counter()
    dates = []

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            counts += 1
            markets[row.get('Market Name', '').strip()] += 1
            products[row.get('Product Name', '').strip()] += 1
            dr = row.get('Date Recorded')
            if dr:
                try:
                    dates.append(datetime.fromisoformat(dr).date())
                except Exception:
                    pass

    print(f"Rows: {counts}")
    print(f"Unique markets: {len(markets)}")
    print(f"Top markets: {markets.most_common(5)}")
    print(f"Unique products: {len(products)}")
    print(f"Top products: {products.most_common(5)}")
    if dates:
        print(f"Date range: {min(dates)} -> {max(dates)}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_market_data.py <path-to-csv>")
        sys.exit(1)
    validate(sys.argv[1])
