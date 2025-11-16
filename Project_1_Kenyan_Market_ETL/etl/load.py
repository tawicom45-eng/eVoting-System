"""
Data Loading Module

This module handles loading transformed data into the target database and optionally
to CSV. It creates the target schema if missing and performs idempotent upserts when
running against PostgreSQL (uses ON CONFLICT on unique constraint).

The target table schema:
  market_data(market_name TEXT, product_name TEXT, price NUMERIC(10,2), quantity INT,
              date_recorded DATE, source_file TEXT, created_at TIMESTAMPTZ)

The loader attempts to coerce incoming dataframe columns to the correct types and
supports batched loading for large datasets.
"""

import csv
from datetime import datetime, timezone
import logging
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, MetaData, Numeric, Date, Text, DateTime
from sqlalchemy import inspect, text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_table_if_not_exists(engine, table_name='market_data'):
    """Create the canonical `market_data` table if it does not exist.

    Matches the DDL in `sql/create_tables.sql`.
    """
    metadata = MetaData()
    inspector = inspect(engine)

    if not inspector.has_table(table_name):
        market_table = Table(
            table_name,
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('market_name', Text, nullable=False),
            Column('product_name', Text, nullable=False),
            Column('price', Numeric(10, 2), nullable=False),
            Column('quantity', Integer, nullable=False),
            Column('date_recorded', Date, nullable=False),
            Column('source_file', Text, nullable=True),
            Column('created_at', DateTime, nullable=False),
        )
        metadata.create_all(engine)
        logger.info(f"Created table: {table_name}")

    # Always ensure constraints and indexes exist (idempotent)
    _ensure_indexes_and_constraints(engine, table_name)


def _ensure_indexes_and_constraints(engine, table_name='market_data'):
    """Ensure that required unique constraint and indexes exist on the table."""
    dialect = engine.dialect.name.lower()
    try:
        with engine.begin() as conn:
            if dialect == 'postgresql':
                # Check if constraint exists; if not, create it
                constraint_check = text("""
                    SELECT constraint_name FROM information_schema.table_constraints
                    WHERE table_name = :table_name AND constraint_type = 'UNIQUE'
                """)
                result = conn.execute(constraint_check, {'table_name': table_name}).fetchall()
                if not result:
                    # Constraint doesn't exist, create it
                    conn.execute(text(
                        f"ALTER TABLE {table_name} ADD CONSTRAINT {table_name}_unique_market_product_date "
                        f"UNIQUE (market_name, product_name, date_recorded)"
                    ))
                    logger.info(f"Created UNIQUE constraint on {table_name}")
            else:
                # For SQLite and others, create unique index if not exists
                conn.execute(text(
                    f"CREATE UNIQUE INDEX IF NOT EXISTS idx_market_unique ON {table_name} (market_name, product_name, date_recorded)"
                ))
            # Create additional indexes
            conn.execute(text(
                f"CREATE INDEX IF NOT EXISTS idx_market_market ON {table_name} (market_name)"
            ))
            conn.execute(text(
                f"CREATE INDEX IF NOT EXISTS idx_market_product ON {table_name} (product_name)"
            ))
            conn.execute(text(
                f"CREATE INDEX IF NOT EXISTS idx_market_date ON {table_name} (date_recorded)"
            ))
    except Exception as e:
        logger.debug(f"Could not ensure constraints/indexes on {table_name}: {e}")


def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and coerce types to match table schema.

    Expected CSV columns: 'Market Name','Product Name','Price','Quantity','Date Recorded'
    """
    # Accept existing column naming conventions and normalize to lowercase underscored
    df = df.rename(columns=lambda c: c.strip())
    col_map = {
        'Market Name': 'market_name',
        'Product Name': 'product_name',
        'Price': 'price',
        'Quantity': 'quantity',
        'Date Recorded': 'date_recorded'
    }
    # If columns already lower/underscored, keep them
    for src, dst in col_map.items():
        if src in df.columns and dst not in df.columns:
            df = df.rename(columns={src: dst})

    # Ensure required columns exist
    required = ['market_name', 'product_name', 'price', 'quantity', 'date_recorded']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Coerce types
    df['market_name'] = df['market_name'].astype(str)
    df['product_name'] = df['product_name'].astype(str)

    # Price: remove any currency symbols and coerce to numeric
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(float)

    # Quantity: integer
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)

    # Date: support ISO date or timestamp; coerce to date only
    df['date_recorded'] = pd.to_datetime(df['date_recorded'], errors='coerce').dt.date

    # Add optional source_file and created_at if missing
    if 'source_file' not in df.columns:
        df['source_file'] = None
    df['created_at'] = pd.Timestamp(datetime.now(timezone.utc))

    # Reorder columns to match the table
    df = df[['market_name', 'product_name', 'price', 'quantity', 'date_recorded', 'source_file', 'created_at']]
    
    # Ensure no duplicates on the unique key before loading
    initial_len = len(df)
    df = df.drop_duplicates(subset=['market_name', 'product_name', 'date_recorded'], keep='first')
    if len(df) < initial_len:
        logger.warning(f"Removed {initial_len - len(df)} duplicate rows based on unique key")
    
    return df


def load_to_database(df: pd.DataFrame, engine, table_name='market_data', batch_size=1000):
    """Load dataframe to database with batched inserts.

    If running on PostgreSQL, performs an idempotent upsert using the unique
    constraint (market_name, product_name, date_recorded).
    """
    if df.empty:
        logger.warning("No data to load")
        return 0

    create_table_if_not_exists(engine, table_name)

    df = _prepare_dataframe(df)
    total = 0

    dialect = engine.dialect.name.lower()

    if dialect == 'postgresql':
        # Use a temporary table + single INSERT ... ON CONFLICT for upsert (Postgres)
        temp_table = f"tmp_{table_name}"
        try:
            with engine.begin() as conn:
                # Write into a temporary table in batches
                for i in range(0, len(df), batch_size):
                    batch = df.iloc[i:i+batch_size]
                    batch.to_sql(temp_table, con=engine, if_exists='append', index=False)
                    total += len(batch)

                # Insert from temp table into target with ON CONFLICT
                ts_fn = 'now()' if dialect == 'postgresql' else 'CURRENT_TIMESTAMP'
                insert_sql = f"""
INSERT INTO {table_name} (market_name, product_name, price, quantity, date_recorded, source_file, created_at)
SELECT market_name, product_name, price, quantity, date_recorded, source_file, {ts_fn} FROM {temp_table}
ON CONFLICT (market_name, product_name, date_recorded)
DO UPDATE SET
  price = EXCLUDED.price,
  quantity = EXCLUDED.quantity,
  source_file = EXCLUDED.source_file,
  created_at = {ts_fn};
"""
                conn.execute(text(insert_sql))
                # Drop temp table
                conn.execute(text(f"DROP TABLE IF EXISTS {temp_table}"))
                logger.info(f"Upserted {total} rows into {table_name} (via temp table)")
        finally:
            pass
        return total

    else:
        # Fallback generic path: use pandas.to_sql append in batches
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            batch.to_sql(table_name, con=engine, if_exists='append', index=False)
            total += len(batch)
            logger.info(f"Appended {total} rows to {table_name}")
        return total


def load_to_csv(df: pd.DataFrame, output_path: str):
    # Ensure parent directory exists
    import os
    parent = os.path.dirname(output_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    df.to_csv(output_path, index=False)
    logger.info(f"Wrote {len(df)} rows to {output_path}")
    return len(df)


def generate_load_report(rows_loaded, table_name, load_type='database'):
    report = {
        'timestamp': datetime.utcnow(),
        'load_type': load_type,
        'table_name': table_name,
        'rows_loaded': rows_loaded,
        'status': 'SUCCESS' if rows_loaded > 0 else 'FAILED'
    }
    logger.info(f"LOAD REPORT: {report}")
    return report


def load_data(transformed_data: pd.DataFrame, connection, table_name='market_data', output_csv=None):
    """Main entry point for loading data. `connection` is a SQLAlchemy engine."""
    if transformed_data is None or transformed_data.empty:
        logger.warning("No data to load")
        return

    logger.info("Starting loading pipeline")
    # If connection is provided, attempt database load; otherwise fall back to CSV only
    if connection is not None:
        rows = load_to_database(transformed_data, connection, table_name)
        generate_load_report(rows, table_name, 'database')
    else:
        logger.info("No DB connection provided; skipping DB load and writing CSV backup only")

    if output_csv:
        try:
            csv_rows = load_to_csv(transformed_data, output_csv)
            generate_load_report(csv_rows, output_csv, 'csv')
        except Exception as e:
            logger.error(f"Failed to write CSV backup: {e}")
            raise

