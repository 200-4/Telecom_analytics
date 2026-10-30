# inspect_warehouse.py
import sqlite3

conn = sqlite3.connect('telecom.db')
cur = conn.cursor()

tables = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' "
    "AND (name LIKE 'dim_%' OR name LIKE 'fact_%') ORDER BY name"
)]

for t in tables:
    count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"\n{t}  ({count:,} rows)")
    print("-" * 60)
    for col in cur.execute(f"PRAGMA table_info({t})").fetchall():
        flags = []
        if col[3]:
            flags.append("NOT NULL")
        if col[5]:
            flags.append("PK")
        print(f"  {col[1]:28s} {col[2]:15s} {' '.join(flags)}")

conn.close()