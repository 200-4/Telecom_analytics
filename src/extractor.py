# src/extractor.py
"""Extract data from source with watermark tracking"""

import sqlite3
from datetime import datetime
from src.watermark import WatermarkManager

class DataExtractor:
    """Extract data from telecom database"""
    
    def __init__(self, db_path: str = 'telecom.db'):
        self.db_path = db_path
        self.watermark_mgr = WatermarkManager(db_path)
    
    def extract_subscribers(self) -> dict:
        """Extract subscriber data since last watermark"""
        
        print("\n" + "=" * 60)
        print("EXTRACTING: Subscribers")
        print("=" * 60)
        
        # Get watermark
        last_watermark = self.watermark_mgr.get_watermark('subscribers')
        
        # Query data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) as count, MAX(loaded_at) as latest
        FROM staging_subscribers
        WHERE loaded_at > ?
        """
        
        cursor.execute(query, (last_watermark,))
        result = cursor.fetchone()
        count, latest = result
        
        conn.close()
        
        print(f"Records to load: {count:,}")
        print(f"Latest timestamp: {latest}")
        
        # Update watermark
        if latest:
            self.watermark_mgr.update_watermark('subscribers', latest)
        
        return {
            'source': 'subscribers',
            'records_extracted': count,
            'new_watermark': latest,
            'status': 'SUCCESS'
        }
    
    def extract_cdr(self) -> dict:
        """Extract CDR data since last watermark"""
        
        print("\n" + "=" * 60)
        print("EXTRACTING: CDR Records")
        print("=" * 60)
        
        # Get watermark
        last_watermark = self.watermark_mgr.get_watermark('cdr')
        
        # Query data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) as count, MAX(timestamp_start) as latest
        FROM staging_cdr
        WHERE timestamp_start > ?
        """
        
        cursor.execute(query, (last_watermark,))
        result = cursor.fetchone()
        count, latest = result
        
        conn.close()
        
        print(f"Records to load: {count:,}")
        print(f"Latest timestamp: {latest}")
        
        # Update watermark
        if latest:
            self.watermark_mgr.update_watermark('cdr', latest)
        
        return {
            'source': 'cdr',
            'records_extracted': count,
            'new_watermark': latest,
            'status': 'SUCCESS'
        }
    
    def extract_transactions(self) -> dict:
        """Extract transaction data since last watermark"""
        
        print("\n" + "=" * 60)
        print("EXTRACTING: Transactions")
        print("=" * 60)
        
        # Get watermark
        last_watermark = self.watermark_mgr.get_watermark('transactions')
        
        # Query data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) as count, MAX(timestamp) as latest
        FROM staging_transactions
        WHERE timestamp > ?
        """
        
        cursor.execute(query, (last_watermark,))
        result = cursor.fetchone()
        count, latest = result
        
        conn.close()
        
        print(f"Records to load: {count:,}")
        print(f"Latest timestamp: {latest}")
        
        # Update watermark
        if latest:
            self.watermark_mgr.update_watermark('transactions', latest)
        
        return {
            'source': 'transactions',
            'records_extracted': count,
            'new_watermark': latest,
            'status': 'SUCCESS'
        }