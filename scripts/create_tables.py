#!/usr/bin/env python3
"""
Create database tables for Clippy multi-user mode
Run this directly with the same Python that runs your Flask app
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration from environment
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'clippy',
    'user': 'davisschwenke',
    'password': 'Haverford2012!'
}

def create_tables():
    """Create all required tables"""
    conn = None
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Creating tables...")
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                google_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                picture_url VARCHAR(512),
                refresh_token TEXT,
                access_token TEXT,
                token_expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        print("✅ Created users table")
        
        # Create upload history table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS upload_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                video_id VARCHAR(255),
                video_title VARCHAR(512),
                video_url VARCHAR(512),
                upload_status VARCHAR(50),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created upload_history table")
        
        # Create user sessions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created user_sessions table")
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_history_user ON upload_history(user_id);")
        print("✅ Created indexes")
        
        # Commit changes
        conn.commit()
        print("\n✅ All tables created successfully!")
        
        # Verify tables
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print(f"\nVerified tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_tables()
