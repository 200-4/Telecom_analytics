# check_after_ingestion.py
import sqlite3

conn = sqlite3.connect('telecom.db')
total = conn.execute("SELECT COUNT(*) FROM staging_cdr").fetchone()[0]
distinct = conn.execute("SELECT COUNT(DISTINCT call_id) FROM staging_cdr").fetchone()[0]
runs = conn.execute(
    "SELECT run_id, pipeline_name, status, rows_loaded FROM pipeline_runs "
    "WHERE pipeline_name = 'cdr_daily_load' ORDER BY run_id DESC LIMIT 1"
).fetchone()
conn.close()

print(f"staging_cdr rows:  {total:,}  (was 91,087 before the run)")
print(f"distinct call_ids: {distinct:,}")
print(f"latest run record: {runs}")