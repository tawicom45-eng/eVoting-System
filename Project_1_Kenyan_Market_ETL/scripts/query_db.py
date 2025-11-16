"""Simple DB query helper to show counts and samples from the SQLite DB used in tests."""
from sqlalchemy import create_engine, text

def main():
    db_file = 'kenyan_market_test.db'
    engine = create_engine(f"sqlite:///{db_file}")
    with engine.connect() as conn:
        cnt = conn.execute(text('SELECT COUNT(*) FROM market_data')).scalar()
        print('market_data count:', cnt)
        rows = conn.execute(text('SELECT market_name, product_name, price, quantity, date_recorded FROM market_data LIMIT 5'))
        for r in rows:
            print(r)

if __name__ == '__main__':
    main()
