"""Print a few summary metrics from the project database."""

import sqlite3

from src.database import DEFAULT_DB_PATH


def main():
    with sqlite3.connect(DEFAULT_DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM staging_subscribers").fetchone()[0]
        print("=" * 50)
        print("Total subscribers")
        print("=" * 50)
        print(f"{total:,}")

        print("\nSubscribers by region (active)")
        rows = conn.execute(
            """SELECT region, COUNT(*) AS count
               FROM staging_subscribers
               WHERE account_status = 'ACTIVE'
               GROUP BY region ORDER BY count DESC"""
        ).fetchall()
        for region, count in rows:
            print(f"{region or 'Unknown':20s} {count:>8,}")

        print("\nCDR by call type")
        rows = conn.execute(
            "SELECT call_type, COUNT(*) FROM staging_cdr GROUP BY call_type"
        ).fetchall()
        for call_type, count in rows:
            print(f"{call_type or 'Unknown':20s} {count:>8,}")

        total, successful, rate = conn.execute(
            """SELECT COUNT(*),
                      COALESCE(SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END), 0),
                      COALESCE(ROUND(100.0 * SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END)
                                     / NULLIF(COUNT(*), 0), 1), 0)
               FROM staging_transactions"""
        ).fetchone()
        print("\nTransaction success rate")
        print(f"Total: {total:,}; successful: {successful:,}; rate: {rate:.1f}%")


if __name__ == "__main__":
    main()
