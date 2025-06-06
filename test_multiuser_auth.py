#!/usr/bin/env python3
"""Test multiuser authentication setup"""

import os
import sys

print("Python executable:", sys.executable)
print("Python version:", sys.version)

# Check if .env file exists
if os.path.exists('.env'):
    print("✅ .env file found")
    # Load it
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env loaded successfully")
    except ImportError:
        print("❌ python-dotenv not installed")
else:
    print("❌ .env file not found")

# Check database configuration
print("\nDatabase configuration:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'NOT SET'}")

# Check if psycopg2 is available
try:
    import psycopg2
    print("\n✅ psycopg2 is installed")
    
    # Try to connect
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        print("✅ Successfully connected to database")
        
        # Check if tables exist
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        
        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("❌ No tables found - need to run migrations")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        
except ImportError:
    print("\n❌ psycopg2 not installed")
    print("Run: pip install psycopg2-binary")

# Check client_secrets.json
if os.path.exists('client_secrets.json'):
    print("\n✅ client_secrets.json found")
else:
    print("\n❌ client_secrets.json not found")
