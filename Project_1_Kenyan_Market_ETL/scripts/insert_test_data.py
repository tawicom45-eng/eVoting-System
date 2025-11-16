"""Insert test data for Power BI export."""
from dotenv import load_dotenv
load_dotenv()

from config.db_config import get_db_connection
from sqlalchemy import text
from datetime import date

engine = get_db_connection()
with engine.begin() as c:
    c.execute(text("""
        INSERT INTO market_data (market_name, product_name, price, quantity, date_recorded, source_file, created_at)
        VALUES 
        ('Nairobi Market', 'Maize', 45.50, 100, :date, 'test', now()),
        ('Mombasa Market', 'Rice', 65.75, 150, :date, 'test', now()),
        ('Kisumu Market', 'Beans', 55.25, 200, :date, 'test', now())
    """), {'date': date(2024, 1, 15)})
    print('✓ Inserted 3 test rows')
