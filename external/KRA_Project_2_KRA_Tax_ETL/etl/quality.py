import sqlite3
from typing import Dict, Tuple

import pandas as pd


def row_count(engine, table: str) -> int:
    cur = engine.execute(f"SELECT COUNT(1) FROM {table}")
    return int(cur.scalar()) if hasattr(cur, 'scalar') else int(cur.fetchone()[0])


def referential_counts(engine) -> Dict[str, int]:
    """Return counts of missing foreign keys for fact tables referencing dim_taxpayer."""
    sqls = {
        'tax_returns_missing_taxpayers': "SELECT COUNT(1) FROM fact_tax_returns r LEFT JOIN dim_taxpayer d ON r.taxpayer_id = d.taxpayer_id WHERE d.taxpayer_id IS NULL",
        'withholding_missing_taxpayers': "SELECT COUNT(1) FROM fact_withholding w LEFT JOIN dim_taxpayer d ON w.taxpayer_id = d.taxpayer_id WHERE d.taxpayer_id IS NULL",
        'vat_missing_taxpayers': "SELECT COUNT(1) FROM fact_vat v LEFT JOIN dim_taxpayer d ON v.taxpayer_id = d.taxpayer_id WHERE d.taxpayer_id IS NULL",
    }
    res = {}
    conn = engine.connect()
    for k, q in sqls.items():
        r = conn.execute(q)
        try:
            val = int(r.scalar())
        except Exception:
            val = int(r.fetchone()[0])
        res[k] = val
    conn.close()
    return res


def basic_checks(engine) -> Tuple[bool, Dict[str, int]]:
    """Run basic DQ checks. Return (ok, details)."""
    details = {}
    try:
        details['dim_taxpayer_count'] = row_count(engine, 'dim_taxpayer')
        details['fact_tax_returns_count'] = row_count(engine, 'fact_tax_returns')
        details['fact_withholding_count'] = row_count(engine, 'fact_withholding')
        details['fact_vat_count'] = row_count(engine, 'fact_vat')
    except Exception as e:
        return False, {'error': str(e)}

    refs = referential_counts(engine)
    details.update(refs)

    # simple pass/fail criteria: no missing references
    ok = all(v == 0 for k, v in refs.items())
    return ok, details
