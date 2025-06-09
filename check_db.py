#!/usr/bin/env python3
"""Check database connection and create tables if needed"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try importing psycopg2
try:
    import psycopg2
    print("✅ psycopg2 is installed")
except ImportError:
    print("❌ psycopg2 is not installed")
    print("Please run: pip install psycopg2-binary")
    sys.exit(1)

# Get database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'clippy'),
    'user': os.getenv('DB_USER', 'clippy_user'),
    'password': os.getenv('DB_PASSWORD', '')
}

print(f"\nDatabase config:")
print(f"  Host: {DB_CONFIG['host']}")
print(f"  Port: {DB_CONFIG['port']}")
print(f"  Database: {DB_CONFIG['database']}")
print(f"  User: {DB_CONFIG['user']}")
print(f"  Password: {'***' if DB_CONFIG['password'] else 'NOT SET'}")

# Try to connect
try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("\n✅ Successfully connected to database!")
    
    # Check if tables exist
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    print(f"\nExisting tables: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    # If no tables, create them
    if len(tables) == 0:
        print("\n📝 No tables found. Creating tables...")
        
        # Users table
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
        
        # Upload history table
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
        
        # User sessions table
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
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_history_user ON upload_history(user_id);")
        
        conn.commit()
        print("✅ Tables created successfully!")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Could not connect to database: {e}")
    print("\nPossible issues:")
    print("1. PostgreSQL is not running")
    print("2. Database 'clippy' does not exist")
    print("3. User credentials are incorrect")
    print("\nTo fix:")
    print("1. Make sure PostgreSQL is running: brew services start postgresql")
    print("2. Create database: createdb clippy")
    print("3. Check your .env file has correct credentials")
    
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
