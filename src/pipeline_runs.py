# src/pipeline_runs.py
"""
Run metadata logger for the telecom analytics pipeline.
Records every pipeline run in the pipeline_runs table.
"""

import sqlite3
from datetime import datetime


def _now() -> str:
    """Current timestamp as an ISO string, matching the rest of the database."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class PipelineRunLogger:
    """Start, finish, and fail records for pipeline runs."""

    def __init__(self, db_path: str = 'telecom.db'):
        self.db_path = db_path

    def start_run(self, pipeline_name: str, rows_attempted: int = 0) -> int:
        """Insert a new run with status RUNNING. Returns the run_id."""
        now = _now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO pipeline_runs
                (pipeline_name, execution_start, status,
                 rows_attempted, rows_loaded, rows_failed, created_at)
            VALUES (?, ?, 'RUNNING', ?, 0, 0, ?)
            """,
            (pipeline_name, now, rows_attempted, now),
        )
        conn.commit()
        run_id = cursor.lastrowid
        conn.close()
        print(f"▶️  Run {run_id} started: {pipeline_name}")
        return run_id

    def finish_run(self, run_id: int, rows_loaded: int, rows_failed: int = 0):
        """Mark a run SUCCESS, or PARTIAL if some rows failed."""
        status = 'PARTIAL' if rows_failed > 0 else 'SUCCESS'
        self._close_run(run_id, status, rows_loaded, rows_failed, None)
        print(f"✅ Run {run_id} finished: {status} "
              f"(loaded={rows_loaded:,}, failed={rows_failed:,})")

    def fail_run(self, run_id: int, error_summary: str, rows_loaded: int = 0):
        """Mark a run FAILED and store the error message."""
        self._close_run(run_id, 'FAILED', rows_loaded, 0, error_summary)
        print(f"❌ Run {run_id} failed: {error_summary}")

    def _close_run(self, run_id, status, rows_loaded, rows_failed, error_summary):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pipeline_runs
               SET execution_end = ?,
                   status        = ?,
                   rows_loaded   = ?,
                   rows_failed   = ?,
                   error_summary = ?
             WHERE run_id = ?
            """,
            (_now(), status, rows_loaded, rows_failed, error_summary, run_id),
        )
        conn.commit()
        conn.close()