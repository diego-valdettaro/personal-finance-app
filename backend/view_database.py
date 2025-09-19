#!/usr/bin/env python3
"""
Database Viewer Script
This script connects to the SQLite database and displays all data in a readable format.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def format_value(value):
    """Format values for better display"""
    if value is None:
        return "NULL"
    elif isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, float):
        return f"{value:.2f}"
    else:
        return str(value)

def print_table_data(cursor, table_name):
    """Print all data from a table"""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name.upper()}")
    print(f"{'='*80}")
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    if not columns:
        print(f"Table '{table_name}' not found or empty.")
        return
    
    # Get all data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"No data found in table '{table_name}'.")
        return
    
    # Print column headers
    col_names = [col[1] for col in columns]
    print(f"Columns: {', '.join(col_names)}")
    print(f"Rows: {len(rows)}")
    print("-" * 80)
    
    # Print data
    for i, row in enumerate(rows, 1):
        print(f"Row {i}:")
        for j, value in enumerate(row):
            col_name = col_names[j]
            formatted_value = format_value(value)
            print(f"  {col_name}: {formatted_value}")
        print("-" * 40)

def print_table_summary(cursor, table_name):
    """Print a summary of table data"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    col_names = [col[1] for col in columns]
    
    print(f"{table_name:20} | {count:6} rows | {len(col_names):2} columns | {', '.join(col_names[:3])}{'...' if len(col_names) > 3 else ''}")

def main():
    # Database path
    db_path = Path("app.db")
    
    if not db_path.exists():
        print(f"❌ Database file not found: {db_path.absolute()}")
        print("Make sure you're running this from the backend directory and the database exists.")
        return
    
    print(f"🔍 Viewing database: {db_path.absolute()}")
    print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("❌ No tables found in the database.")
            return
        
        print(f"\n📊 Found {len(tables)} tables:")
        print("-" * 80)
        
        # Print summary of all tables
        for table in tables:
            print_table_summary(cursor, table)
        
        print("\n" + "="*80)
        print("DETAILED DATA VIEW")
        print("="*80)
        
        # Ask user if they want detailed view
        response = input("\nDo you want to see detailed data for all tables? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            for table in tables:
                print_table_data(cursor, table)
        else:
            print("\nSkipping detailed view. Run the script again and choose 'y' to see detailed data.")
        
        # Show some sample queries
        print(f"\n{'='*80}")
        print("SAMPLE QUERIES")
        print(f"{'='*80}")
        
        # Count active records
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE active = 1")
                active_count = cursor.fetchone()[0]
                print(f"{table}: {active_count} active records")
            except:
                # Table might not have 'active' column
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_count = cursor.fetchone()[0]
                print(f"{table}: {total_count} total records")
        
        conn.close()
        print(f"\n✅ Database view completed successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
