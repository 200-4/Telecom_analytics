# src/watermark.py
"""Watermark management for incremental loads"""

import sqlite3
from datetime import datetime

class WatermarkManager:
    """Manage data load watermarks"""
    
    def __init__(self, db_path: str = 'telecom.db'):
        self.db_path = db_path
    
    def get_watermark(self, data_source: str) -> str:
        """
        Get last watermark for a data source
        
        Args:
            data_source: Name of source (subscribers, cdr, transactions)
        
        Returns:
            Last watermark timestamp string
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT last_watermark FROM pipeline_watermarks WHERE data_source = ?",
            (data_source,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        watermark = result[0] if result else '1970-01-01'
        print(f"📍 Watermark for {data_source}: {watermark}")
        return watermark
    
    def update_watermark(self, data_source: str, new_watermark: str):
        """
        Update watermark after successful load
        
        Args:
            data_source: Name of source
            new_watermark: New timestamp to mark as loaded
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE pipeline_watermarks 
               SET last_watermark = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE data_source = ?""",
            (new_watermark, data_source)
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ Watermark updated for {data_source}: {new_watermark}")
    
    def show_all_watermarks(self):
        """Display all watermarks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT data_source, last_watermark, updated_at FROM pipeline_watermarks")
        rows = cursor.fetchall()
        conn.close()
        
        print("\n📍 CURRENT WATERMARKS:")
        print("-" * 70)
        for source, watermark, updated in rows:
            print(f"{source:20s} {watermark:20s} (updated: {updated})")
        print("-" * 70)