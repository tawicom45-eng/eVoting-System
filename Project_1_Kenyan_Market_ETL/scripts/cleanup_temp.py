"""Clean up temp tables."""
from config.db_config import get_db_connection
from sqlalchemy import text

conn = get_db_connection()
with conn.begin() as cx:
    cx.execute(text('DROP TABLE IF EXISTS tmp_market_data'))
    print('✓ Dropped temp table')
