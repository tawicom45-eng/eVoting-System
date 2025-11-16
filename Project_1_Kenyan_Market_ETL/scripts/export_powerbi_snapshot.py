"""
Export a CSV snapshot suitable for Power BI from the configured database.
Writes `dashboards/powerbi_sample_export.csv` with a flattened view of `market_data`.
"""
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd

# Load .env first before importing config
load_dotenv()

from config.db_config import get_db_connection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = PROJECT_ROOT / 'dashboards' / 'powerbi_sample_export.csv'

# Use the configured database engine
engine = get_db_connection()

query = '''
SELECT market_name, product_name, price, quantity, date_recorded, source_file, created_at
FROM market_data
'''

df = pd.read_sql(query, engine)
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_PATH, index=False)
print(f"Wrote {len(df)} rows to {OUT_PATH}")
