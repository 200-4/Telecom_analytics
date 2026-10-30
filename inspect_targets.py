# inspect_targets.py
import sqlite3

conn = sqlite3.connect('telecom.db')
cursor = conn.cursor()

for table in ['staging_cdr', 'fact_calls']:
    print(f"\nCOLUMNS IN {table}:")
    print("-" * 60)
    for col in cursor.execute(f"PRAGMA table_info({table})").fetchall():
        # col = (cid, name, type, notnull, default_value, pk)
        flags = []
        if col[3]:
            flags.append("NOT NULL")
        if col[5]:
            flags.append("PRIMARY KEY")
        print(f"{col[1]:25s} {col[2]:15s} {' '.join(flags)}")

    print("ROW COUNT:", cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    indexes = cursor.execute(f"PRAGMA index_list({table})").fetchall()
    print("INDEXES:", [i[1] for i in indexes] or "none")

conn.close()