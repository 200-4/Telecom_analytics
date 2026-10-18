# inspect_failed_records.py
import sqlite3

conn = sqlite3.connect('telecom.db')
cursor = conn.cursor()

print("COLUMNS IN raw_failed_records:")
print("-" * 60)
for col in cursor.execute("PRAGMA table_info(raw_failed_records)").fetchall():
    # col = (cid, name, type, notnull, default_value, pk)
    flags = []
    if col[3]:
        flags.append("NOT NULL")
    if col[5]:
        flags.append("PRIMARY KEY")
    print(f"{col[1]:25s} {col[2]:15s} {' '.join(flags)}")

print("\nROW COUNT:", cursor.execute("SELECT COUNT(*) FROM raw_failed_records").fetchone()[0])
conn.close()