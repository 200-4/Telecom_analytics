# test_connection.py
"""Test database connection"""

from src.database import DatabaseConnection

def main():
    print("=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    # Create connection
    db = DatabaseConnection('telecom.db')
    
    # Connect
    if not db.connect():
        print("Failed to connect!")
        return
    
    # Verify
    print("\nVerifying connection...")
    status = db.verify_connection()
    print(f"Status: {status['status']}")
    print(f"Database: {status['database']}")
    print(f"\nTable Record Counts:")
    for table, count in status['tables'].items():
        print(f"  {table:30s} {count:,} records")
    
    # Disconnect
    db.disconnect()
    
    print("\n✅ Connection test complete!")

if __name__ == "__main__":
    main()