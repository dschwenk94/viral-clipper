#!/usr/bin/env python3
"""Check if TikTok database tables exist"""

import sys
import os
sys.path.insert(0, '/Users/davisschwenke/Clippy')

from database import get_db_connection

try:
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if TikTok tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('platform_connections', 'tiktok_upload_history')
        ORDER BY table_name
    """)
    
    tables = [row[0] for row in cur.fetchall()]
    
    print("TikTok Database Status:")
    print("-" * 40)
    
    if 'platform_connections' in tables:
        print("✓ Table 'platform_connections' EXISTS")
        # Check columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'platform_connections' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print("  Columns:", [f"{col[0]} ({col[1]})" for col in columns])
    else:
        print("✗ Table 'platform_connections' NOT FOUND")
    
    if 'tiktok_upload_history' in tables:
        print("✓ Table 'tiktok_upload_history' EXISTS")
        # Check columns
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tiktok_upload_history' 
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        print("  Columns:", [f"{col[0]} ({col[1]})" for col in columns])
    else:
        print("✗ Table 'tiktok_upload_history' NOT FOUND")
    
    print("-" * 40)
    
    if len(tables) == 2:
        print("✅ TikTok migration appears to be COMPLETE")
        print("   Running the migration again will be SAFE (it checks for existing tables)")
    else:
        print("❌ TikTok migration needs to be run")
        print("   Run: python migrations/003_tiktok_support.py")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error checking database: {e}")
