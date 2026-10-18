"""Count source rows newer than each source's saved watermark."""

import sqlite3
from contextlib import closing
from pathlib import Path

from src.database import DEFAULT_DB_PATH, PROJECT_ROOT
from src.watermark import WatermarkManager


class DataExtractor:
    """Inspect incremental source rows in the telecom SQLite database."""

    SOURCES = {
        "subscribers": ("staging_subscribers", "loaded_at"),
        "cdr": ("staging_cdr", "timestamp_start"),
        "transactions": ("staging_transactions", "timestamp"),
    }

    def __init__(self, db_path=DEFAULT_DB_PATH):
        path = Path(db_path)
        self.db_path = path if path.is_absolute() else PROJECT_ROOT / path
        self.watermark_mgr = WatermarkManager(self.db_path)

    def _extract_since_watermark(self, source: str) -> dict:
        if source not in self.SOURCES:
            raise ValueError(f"Unknown data source: {source}")
        table, timestamp_column = self.SOURCES[source]
        last_watermark = self.watermark_mgr.get_watermark(source)
        query = (
            f'SELECT COUNT(*), MAX("{timestamp_column}") FROM "{table}" '
            f'WHERE "{timestamp_column}" > ?'
        )
        with closing(sqlite3.connect(self.db_path)) as conn:
            count, latest = conn.execute(query, (last_watermark,)).fetchone()

        label = {"subscribers": "Subscribers", "cdr": "CDR Records", "transactions": "Transactions"}[source]
        print("\n" + "=" * 60)
        print(f"EXTRACTING: {label}")
        print("=" * 60)
        print(f"Records to load: {count:,}")
        print(f"Latest timestamp: {latest}")
        if latest is not None:
            self.watermark_mgr.update_watermark(source, latest)
        return {
            "source": source,
            "records_extracted": count,
            "new_watermark": latest or last_watermark,
            "status": "SUCCESS",
        }

    def extract_subscribers(self) -> dict:
        return self._extract_since_watermark("subscribers")

    def extract_cdr(self) -> dict:
        return self._extract_since_watermark("cdr")

    def extract_transactions(self) -> dict:
        return self._extract_since_watermark("transactions")
