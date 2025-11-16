#!/usr/bin/env python3
"""
Generate a realistic Kenyan market dataset CSV for Project 1.

Usage:
    python scripts/generate_market_data.py --rows 500 --out data/sample_market_data.csv

This script is deterministic (uses a fixed seed) so generated data is reproducible.
"""
import csv
import random
import argparse
from datetime import date, timedelta


MARKETS = [
    "Nairobi Market",
    "Mombasa Market",
    "Kisumu Market",
    "Nakuru Market",
    "Eldoret Market",
    "Thika Market",
    "Kitale Market",
    "Garissa Market",
    "Malindi Market",
    "Nyeri Market",
]

PRODUCTS = {
    "Maize": (45, 70),
    "Rice": (55, 90),
    "Beans": (50, 80),
    "Potatoes": (30, 60),
    "Tomatoes": (20, 60),
    "Onions": (25, 55),
    "Sugar": (80, 110),
    "Tea": (200, 400),
    "Coffee": (300, 700),
    "Sorghum": (40, 75),
}


def generate_rows(num_rows=500, start_date=date(2024, 1, 1), days=90, seed=42):
    random.seed(seed)
    rows = []
    for i in range(num_rows):
        market = random.choice(MARKETS)
        product = random.choice(list(PRODUCTS.keys()))
        low, high = PRODUCTS[product]
        # price with two decimals
        price = round(random.uniform(low, high) + random.choice([0, 0.5, 1.0]) * random.random(), 2)
        quantity = random.randint(20, 500)
        d = start_date + timedelta(days=random.randint(0, max(0, days - 1)))
        rows.append([market, product, f"{price:.2f}", str(quantity), d.isoformat()])
    return rows


def write_csv(rows, out_path):
    header = ["Market Name", "Product Name", "Price", "Quantity", "Date Recorded"]
    with open(out_path, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Generate market data CSV")
    parser.add_argument("--rows", type=int, default=500, help="Number of rows to generate")
    parser.add_argument("--out", type=str, default="data/sample_market_data.csv", help="Output CSV path")
    args = parser.parse_args()

    rows = generate_rows(num_rows=args.rows)
    write_csv(rows, args.out)
    print(f"Generated {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
