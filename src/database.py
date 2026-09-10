# src/database.py
"""
Database connection module for telecom analytics platform
Handles secure connection to SQLite database
"""

import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / 'telecom.db'

class DatabaseConnection:
    """Secure database connection handler"""
    
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        database_path = Path(db_path)
        self.db_path = database_path if database_path.is_absolute() else PROJECT_ROOT / database_path
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """
        Establish connection to database
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if database exists
            if not self.db_path.is_file():
                print(f"❌ Error: Database not found at {self.db_path}")
                return False
            
            # Create connection
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            
            # Test connection with simple query
            self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = self.cursor.fetchone()[0]
            
            print(f"✅ Connected to {self.db_path}")
            print(f"✅ Database contains {table_count} tables")
            
            return True
        
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Disconnected from database")
    
    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        Execute a SELECT query
        
        Args:
            query: SQL query string
            params: Query parameters (tuple)
        
        Returns:
            List of results
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            results = self.cursor.fetchall()
            return results
        
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return []
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count from a table"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.execute_query(query)
        return result[0][0] if result else 0
    
    def verify_connection(self) -> dict:
        """Verify connection and return status"""
        return {
            'status': 'connected' if self.connection else 'disconnected',
            'database': self.db_path,
            'timestamp': datetime.utcnow().isoformat(),
            'tables': {
                'staging_subscribers': self.get_table_count('staging_subscribers'),
                'staging_cdr': self.get_table_count('staging_cdr'),
                'staging_transactions': self.get_table_count('staging_transactions'),
            }
        }