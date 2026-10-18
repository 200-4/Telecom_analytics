import sqlite3

conn = sqlite3.connect("telecom.db")
cursor = conn.cursor()

print("COLUMNS IN pipeline_runs:")
print("-" * 60)

for col in cursor.execute("PRAGMA table_info(pipeline_runs)").fetchall():
    # col = (cid, name, type, notnull, default_value, pk)
    print(f"{col[1]:25s} {col[2]:15s} {'PRIMARY KEY' if col[5] else ''}")
print("\nROW COUNT:", cursor.execute("SELECT COUNT(*) FROM pipeline_runs").fetchone()[0])
conn.close()    