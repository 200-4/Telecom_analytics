# run_sql.py
"""Run every statement in a .sql file against telecom.db.
Usage: python run_sql.py query.sql
"""
import sqlite3
import sys


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'query.sql'
    db = 'telecom.db'

    with open(path, encoding='utf-8') as f:
        statements = [s.strip() for s in f.read().split(';') if s.strip()]

    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        for i, stmt in enumerate(statements, 1):
            cur.execute(stmt)
            if cur.description:  # SELECT: print the rows
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                print(f"\n[{i}] {len(rows)} row(s)")
                print(" | ".join(cols))
                for row in rows:
                    print(" | ".join(str(v) for v in row))
            else:  # INSERT / UPDATE / DELETE
                print(f"[{i}] OK, rows affected: {cur.rowcount}")
        conn.commit()
        print("\nAll statements committed.")
    except Exception as exc:
        conn.rollback()
        print(f"\nError: {exc}\nNo changes were saved.")
    finally:
        conn.close()


if __name__ == '__main__':
    main()