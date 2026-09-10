import sqlite3
from pathlib import Path

# Connect to database
database_path = Path(__file__).resolve().parent / 'telecom.db'
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Query 1: Count subscribers
print("=" * 50)
print("QUERY 1: Total Subscribers")
print("=" * 50)
result = cursor.execute("SELECT COUNT(*) as total FROM staging_subscribers").fetchone()
print(f"Total subscribers: {result[0]:,}")

# Query 2: Subscribers by region
print("\n" + "=" * 50)
print("QUERY 2: Subscribers by Region")
print("=" * 50)
results = cursor.execute("""
    SELECT region, COUNT(*) as count 
    FROM staging_subscribers 
    WHERE account_status = 'ACTIVE' 
    GROUP BY region 
    ORDER BY count DESC
""").fetchall()
for region, count in results:
    print(f"{region:20s} {count:6d} subscribers")

# Query 3: Call types
print("\n" + "=" * 50)
print("QUERY 3: CDR by Call Type")
print("=" * 50)
results = cursor.execute("""
    SELECT call_type, COUNT(*) as count 
    FROM staging_cdr 
    GROUP BY call_type
""").fetchall()
for call_type, count in results:
    print(f"{call_type:15s} {count:6d} calls")

# Query 4: Transaction success rate
print("\n" + "=" * 50)
print("QUERY 4: Transaction Success Rate")
print("=" * 50)
result = cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) as successful,
        ROUND(100.0 * SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
    FROM staging_transactions
""").fetchone()
print(f"Total transactions: {result[0]:,}")
print(f"Successful: {result[1]:,}")
print(f"Success rate: {result[2]:.1f}%")

conn.close()
print("\n✓ Done!")