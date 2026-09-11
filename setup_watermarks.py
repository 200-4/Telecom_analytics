import sqlite3
from datetime import datetime

#watermark tracking table creation
def create_watermark_table():
    """create watermark tracking table if it doesn't exist"""
    conn = sqlite3.connect('telecom.db')
    cursor = conn.cursor()

    sql = """
    CREATE TABLE IF NOT EXISTS pipeline_watermarks (
        watermark_id INTERGER PRIMARY KEY AUTOINCREMENT,
        data_source TEXT NOT NULL UNIQUE,
        last_watermark TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP);

    """
    cursor.execute(sql)
    conn.commit()

    print("watermark table created")

    #Initialize watermarks for each data source
    sources = ['subscriber', 'cdr','transactions']

    for source in sources:
        cursor.execute(
            "INSERT OR IGNORE INTO pipeline_watermarks (data_source, last_watermark) VALUES (?, ?)",
            (source, '1970-01-01')

        )
    conn.commit()
    conn.close()

    print("Watermarks initialised")

if __name__ == "__main__":
    create_watermark_table()