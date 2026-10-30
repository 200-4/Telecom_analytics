# check_call_id_key.py
import sqlite3

conn = sqlite3.connect('telecom.db')
cursor = conn.cursor()

total, distinct = cursor.execute(
    "SELECT COUNT(*), COUNT(DISTINCT call_id) FROM staging_cdr"
).fetchone()
print(f"Total rows:        {total:,}")
print(f"Distinct call_ids: {distinct:,}")
print(f"Duplicates:        {total - distinct:,}")

print("\nUNIQUE constraint check:")
sql = cursor.execute(
    "SELECT sql FROM sqlite_master WHERE name = 'staging_cdr'"
).fetchone()[0]
print("  call_id declared UNIQUE:", 'UNIQUE' in sql.upper())

print("\nNULL call_ids:",
      cursor.execute("SELECT COUNT(*) FROM staging_cdr WHERE call_id IS NULL").fetchone()[0])

conn.close()