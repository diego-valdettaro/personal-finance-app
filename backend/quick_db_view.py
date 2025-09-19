#!/usr/bin/env python3
"""
Quick Database Viewer - Shows all data without prompts
"""

import sqlite3
from pathlib import Path

def main():
    db_path = Path("app.db")
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path.absolute()}")
        return
    
    print(f"🔍 Database: {db_path.absolute()}")
    print("="*80)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            print(f"\n📋 TABLE: {table.upper()}")
            print("-" * 60)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            
            # Get data
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            print(f"Columns: {', '.join(col_names)}")
            print(f"Rows: {len(rows)}")
            
            if rows:
                print("\nData:")
                for i, row in enumerate(rows[:10], 1):  # Show first 10 rows
                    print(f"  {i}: {dict(zip(col_names, row))}")
                if len(rows) > 10:
                    print(f"  ... and {len(rows) - 10} more rows")
            else:
                print("  (No data)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
