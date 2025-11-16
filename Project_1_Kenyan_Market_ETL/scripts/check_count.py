"""Check table count."""
from dotenv import load_dotenv
load_dotenv()

from config.db_config import get_db_connection
from sqlalchemy import text

engine = get_db_connection()
with engine.connect() as c:
    result = c.execute(text('SELECT COUNT(*) FROM market_data'))
    print('Count:', result.scalar())
