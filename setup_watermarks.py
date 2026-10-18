"""Create and initialize the pipeline watermark table."""

import sqlite3
from contextlib import closing

from src.database import DEFAULT_DB_PATH


SOURCES = ("subscribers", "cdr", "transactions")


def create_watermark_table(db_path=DEFAULT_DB_PATH):
    """Create the tracking table and insert missing source watermarks."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS pipeline_watermarks (
                    watermark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source TEXT NOT NULL UNIQUE,
                    last_watermark TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )"""
            )
            conn.executemany(
                "INSERT OR IGNORE INTO pipeline_watermarks (data_source, last_watermark) "
                "VALUES (?, ?)",
                [(source, "1970-01-01") for source in SOURCES],
            )
    print(f"Watermark table initialized in {db_path}")


if __name__ == "__main__":
    create_watermark_table()
