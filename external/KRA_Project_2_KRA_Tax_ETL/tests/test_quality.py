import os
import sqlite3

import pytest

from etl.load.load_to_sqlite import create_conn, ensure_tables
from etl.quality import basic_checks


def test_basic_checks_on_empty_db(tmp_path):
    db = tmp_path / "test_kra.db"
    engine = create_conn(str(db))
    ensure_tables(engine)
    ok, details = basic_checks(engine)
    # empty tables: counts should be zero and ok should be True (no missing refs)
    assert details['dim_taxpayer_count'] == 0
    assert details['fact_tax_returns_count'] == 0
    assert ok is True
