"""SQLite connection helpers for the telecom analytics project."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "telecom.db"


class DatabaseConnection:
    """Manage a connection to the project's SQLite database."""

    def __init__(self, db_path=DEFAULT_DB_PATH):
        path = Path(db_path)
        self.db_path = path if path.is_absolute() else PROJECT_ROOT / path
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Connect if the database exists; return whether connection succeeded."""
        if not self.db_path.is_file():
            print(f"Error: Database not found at {self.db_path}")
            return False
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            print(f"Connected to {self.db_path} ({self.cursor.fetchone()[0]} tables)")
            return True
        except sqlite3.Error as exc:
            self.disconnect()
            print(f"Connection failed: {exc}")
            return False

    def disconnect(self):
        """Close the connection, if open."""
        if self.connection is not None:
            self.connection.close()
        self.connection = None
        self.cursor = None

    def execute_query(self, query: str, params=None) -> list:
        """Execute a read query. Errors propagate so callers cannot mistake them for empty data."""
        if self.connection is None:
            raise RuntimeError("Connect to the database before executing queries")
        cursor = self.connection.execute(query, params or ())
        return cursor.fetchall()

    def get_table_count(self, table_name: str) -> int:
        """Return a table's row count, validating the identifier against SQLite metadata."""
        if self.connection is None:
            raise RuntimeError("Connect to the database before counting rows")
        row = self.connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name = ?",
            (table_name,),
        ).fetchone()
        if row[0] == 0:
            raise ValueError(f"Table not found: {table_name}")
        # The identifier is known to exist, but SQL parameters cannot bind identifiers.
        escaped_name = table_name.replace('"', '""')
        return self.connection.execute(f'SELECT COUNT(*) FROM "{escaped_name}"').fetchone()[0]

    def verify_connection(self) -> dict:
        """Return connection status and counts for known staging tables that exist."""
        tables = {}
        if self.connection is not None:
            for name in ("staging_subscribers", "staging_cdr", "staging_transactions"):
                row = self.connection.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name = ?", (name,)
                ).fetchone()
                if row[0]:
                    tables[name] = self.get_table_count(name)
        return {
            "status": "connected" if self.connection else "disconnected",
            "database": str(self.db_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tables": tables,
        }
