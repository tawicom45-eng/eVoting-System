Power BI Dashboard (placeholder)

This folder contains a placeholder `powerbi_dashboard.pbix` file. Power BI Desktop report files are binary; they must be created using Power BI Desktop.

Quick guide to create `powerbi_dashboard.pbix` for Project 1 (Kenyan Market ETL)

1) Data sources
- CSV: `data/sample_market_data.csv` — easiest for local testing.
- SQLite (local test DB): `kenyan_market_test.db` — use ODBC or an appropriate connector to query `market_data` table.
- Postgres (production): set up connection using credentials in `.env` and connect from Power BI using the Postgres connector.

2) Steps (Power BI Desktop)
- Open Power BI Desktop.
- Get Data -> CSV -> choose `data/sample_market_data.csv` (or Get Data -> More -> PostgreSQL database for Postgres).
- Load data and check types: `market_name` (Text), `product_name` (Text), `price` (Decimal Number), `quantity` (Whole Number), `date_recorded` (Date).
- Create visuals: bar charts for top markets/products, time series for price/quantity, slicers for market/product, KPIs for average price and total quantity.
- Save the report: File -> Save As -> `dashboards/powerbi_dashboard.pbix`.

3) Publish (optional)
- Publish to Power BI Service if you have an account: Home -> Publish.
- Configure refresh credentials if you connect to Postgres or other live data sources.

4) Tips for reproducible dashboards
- Use a dedicated `dashboards/` dataset export (CSV) for deterministic development.
- If you connect to the SQLite DB, consider exporting a flattened CSV snapshot for the PBIX to avoid runtime refresh issues.

5) Want me to help?
- I can: export a ready CSV snapshot to `dashboards/powerbi_sample_export.csv`, create a Power BI data model spec, or (if you provide credentials) validate a direct Postgres connection and produce a dataset.

Commands to create a CSV snapshot from the repo (run from project root):

```powershell
# From project root: create a clean load, then export snapshot
$env:DB_TYPE='sqlite'; $env:DB_NAME='kenyan_market_test'; python run_pipeline.py --truncate
python .\scripts\export_powerbi_snapshot.py

# Or export directly from Postgres (replace with your connection details):
# python -c "import pandas as pd; df=pd.read_sql('SELECT market_name,product_name,price,quantity,date_recorded FROM market_data', 'postgresql://user:pass@host:5432/kenyan_market'); df.to_csv('dashboards/powerbi_sample_export.csv', index=False)"
```

Notes:
- The `--truncate` flag forces a clean load by removing existing rows in `market_data` before loading new data.
- `export_powerbi_snapshot.py` generates `dashboards/powerbi_sample_export.csv` that you can open directly in Power BI Desktop.
