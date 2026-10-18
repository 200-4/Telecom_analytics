# src/dead_letter.py
"""
Dead-letter queue: holds rejected records with the reason they failed,
so one bad row never stops a whole load.
"""

import json
import sqlite3
from datetime import datetime


def _now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class DeadLetterQueue:
    """Store rejected records in raw_failed_records."""

    def __init__(self, db_path: str = 'telecom.db'):
        self.db_path = db_path

    def add(self, run_id: int, data_source: str, record_type: str,
            raw_record: dict, error_reason: str) -> int:
        """Store one rejected record. Returns its failed_record_id."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = _now()
        cursor.execute(
            """
            INSERT INTO raw_failed_records
                (run_id, data_source, record_type, raw_data,
                 error_reason, error_timestamp, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, data_source, record_type,
             json.dumps(raw_record, default=str),
             error_reason, now, now),
        )
        conn.commit()
        failed_id = cursor.lastrowid
        conn.close()
        return failed_id

    def count(self, run_id: int = None) -> int:
        """Count dead-letter rows, optionally for one run."""
        conn = sqlite3.connect(self.db_path)
        if run_id is None:
            n = conn.execute("SELECT COUNT(*) FROM raw_failed_records").fetchone()[0]
        else:
            n = conn.execute(
                "SELECT COUNT(*) FROM raw_failed_records WHERE run_id = ?",
                (run_id,),
            ).fetchone()[0]
        conn.close()
        return n

    def fetch_for_run(self, run_id: int) -> list:
        """Return (failed_record_id, record_type, error_reason, raw_record) for a run."""
        conn = sqlite3.connect(self.db_path)
        rows = conn.execute(
            """
            SELECT failed_record_id, record_type, error_reason, raw_data
              FROM raw_failed_records
             WHERE run_id = ?
             ORDER BY failed_record_id
            """,
            (run_id,),
        ).fetchall()
        conn.close()
        return [(fid, rtype, reason, json.loads(raw)) for fid, rtype, reason, raw in rows]