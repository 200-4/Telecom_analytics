# src/cdr_loader.py
"""
Idempotent loader for staging_cdr.
Rows whose call_id already exists are skipped, so reloading a batch is safe.
"""

import sqlite3
from datetime import datetime


INSERT_SQL = """
INSERT OR IGNORE INTO staging_cdr (
    call_id, subscriber_id, peer_msisdn, call_type, duration_seconds,
    data_mb, timestamp_start, timestamp_end, cell_id, region,
    tariff_code, charge_amount, currency, loaded_at, source_system
) VALUES (
    :call_id, :subscriber_id, :peer_msisdn, :call_type, :duration_seconds,
    :data_mb, :timestamp_start, :timestamp_end, :cell_id, :region,
    :tariff_code, :charge_amount, :currency, :loaded_at, :source_system
)
"""


class CdrLoader:
    """Load CDR records into staging_cdr without creating duplicates."""

    def __init__(self, db_path: str = 'telecom.db', source_system: str = 'ingestion'):
        self.db_path = db_path
        self.source_system = source_system

    def load(self, batch: list) -> int:
        """
        Insert a batch of CDR dicts. Returns the number of NEW rows inserted.
        Records whose call_id already exists are ignored.
        """
        if not batch:
            return 0

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rows = []
        for rec in batch:
            row = {
                'peer_msisdn': None, 'duration_seconds': None, 'data_mb': None,
                'cell_id': None, 'region': None, 'tariff_code': None,
                'charge_amount': None, 'currency': None,
            }
            row.update(rec)  # caller's values override the defaults above
            row['loaded_at'] = now
            row['source_system'] = self.source_system
            rows.append(row)

        conn = sqlite3.connect(self.db_path)
        try:
            before = conn.total_changes
            conn.executemany(INSERT_SQL, rows)
            conn.commit()
            inserted = conn.total_changes - before
        finally:
            conn.close()

        return inserted