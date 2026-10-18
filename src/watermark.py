"""Watermark management for incremental loads."""

import sqlite3
from contextlib import closing
from pathlib import Path

from src.database import DEFAULT_DB_PATH, PROJECT_ROOT


class WatermarkManager:
    """Read and update per-source watermarks."""

    SOURCES = ("subscribers", "cdr", "transactions")

    def __init__(self, db_path=DEFAULT_DB_PATH):
        path = Path(db_path)
        self.db_path = str(path if path.is_absolute() else PROJECT_ROOT / path)

    def get_watermark(self, data_source: str) -> str:
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                row = conn.execute(
                    "SELECT last_watermark FROM pipeline_watermarks WHERE data_source = ?",
                    (data_source,),
                ).fetchone()
        if row is None:
            raise ValueError(
                f"No watermark initialized for '{data_source}'. Run setup_watermarks.py first."
            )
        watermark = row[0]
        print(f"Watermark for {data_source}: {watermark}")
        return watermark

    def update_watermark(self, data_source: str, new_watermark: str):
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                cursor = conn.execute(
                    """UPDATE pipeline_watermarks
                       SET last_watermark = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE data_source = ?""",
                    (new_watermark, data_source),
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"No watermark initialized for '{data_source}'")
        print(f"✅ Watermark updated for {data_source}: {new_watermark}")

    def reset_watermarks(self, initial_watermark="1970-01-01"):
        """Reset the three pipeline sources, for a repeatable full baseline run."""
        with closing(sqlite3.connect(self.db_path)) as conn:
            with conn:
                conn.executemany(
                    """UPDATE pipeline_watermarks
                       SET last_watermark = ?, updated_at = CURRENT_TIMESTAMP
                       WHERE data_source = ?""",
                    [(initial_watermark, source) for source in self.SOURCES],
                )
                existing = {
                    row[0]
                    for row in conn.execute(
                        "SELECT data_source FROM pipeline_watermarks WHERE data_source IN (?, ?, ?)",
                        self.SOURCES,
                    )
                }
                missing = set(self.SOURCES) - existing
                if missing:
                    raise ValueError(f"Watermarks are not initialized: {sorted(missing)}")

    def show_all_watermarks(self):
        with closing(sqlite3.connect(self.db_path)) as conn:
            rows = conn.execute(
                "SELECT data_source, last_watermark, updated_at FROM pipeline_watermarks "
                "WHERE data_source IN (?, ?, ?) "
                "ORDER BY CASE data_source WHEN 'subscribers' THEN 1 WHEN 'cdr' THEN 2 ELSE 3 END",
                self.SOURCES,
            ).fetchall()
        print("\nCURRENT WATERMARKS:")
        print("-" * 70)
        for source, watermark, updated in rows:
            print(f"{source:20s} {str(watermark):20s} (updated: {updated})")
            print("-" * 70)
