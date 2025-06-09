#!/usr/bin/env python3
"""
Add missing is_active column to users table
"""

import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'clippy',
    'user': 'davisschwenke',
    'password': 'Haverford2012!'
}

def add_is_active_column():
    """Add is_active column to users table"""
    conn = None
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Add is_active column
        print("Adding is_active column to users table...")
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
        """)
        
        # Also add last_accessed column to user_sessions that the model expects
        print("Adding last_accessed column to user_sessions table...")
        cur.execute("""
            ALTER TABLE user_sessions 
            ADD COLUMN IF NOT EXISTS last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        """)
        
        # Commit changes
        conn.commit()
        print("✅ Columns added successfully!")
        
        # Verify the schema
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        
        print("\nUsers table schema:")
        for column in cur.fetchall():
            print(f"  - {column[0]}: {column[1]}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_is_active_column()
