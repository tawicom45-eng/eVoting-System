"""Apply DDL schema to Postgres database."""
from config.db_config import get_db_connection
from sqlalchemy import text

conn = get_db_connection()
statements = open('sql/create_tables.sql').read().split(';')

with conn.begin() as cx:
    for s in statements:
        if s.strip():
            cx.execute(text(s.strip()))

print('✓ DDL applied successfully to Postgres')
