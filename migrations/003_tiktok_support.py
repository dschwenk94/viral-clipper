#!/usr/bin/env python3
"""
Migration to add TikTok authentication support
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get a direct database connection for migrations"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME', 'clippy'),
        user=os.getenv('DB_USER', 'clippy_user'),
        password=os.getenv('DB_PASSWORD', 'clippy_password')
    )

def run_migration():
    """Add TikTok authentication support"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Add TikTok columns to users table
        cur.execute('''
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS tiktok_id VARCHAR(255),
            ADD COLUMN IF NOT EXISTS tiktok_username VARCHAR(255),
            ADD COLUMN IF NOT EXISTS tiktok_display_name VARCHAR(255),
            ADD COLUMN IF NOT EXISTS tiktok_avatar_url TEXT,
            ADD COLUMN IF NOT EXISTS tiktok_access_token TEXT,
            ADD COLUMN IF NOT EXISTS tiktok_refresh_token TEXT,
            ADD COLUMN IF NOT EXISTS tiktok_token_expires_at TIMESTAMP,
            ADD COLUMN IF NOT EXISTS tiktok_scopes TEXT,
            ADD COLUMN IF NOT EXISTS tiktok_connected_at TIMESTAMP;
            
            CREATE INDEX IF NOT EXISTS idx_users_tiktok_id ON users(tiktok_id);
        ''')
        
        # Create TikTok upload history table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tiktok_upload_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                job_id VARCHAR(255),
                publish_id VARCHAR(255) UNIQUE,
                video_title TEXT,
                video_description TEXT,
                video_path TEXT,
                share_url TEXT,
                privacy_level VARCHAR(50),
                upload_type VARCHAR(20), -- 'direct' or 'draft'
                upload_status VARCHAR(50),
                error_message TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_tiktok_history_user ON tiktok_upload_history(user_id);
            CREATE INDEX IF NOT EXISTS idx_tiktok_history_job ON tiktok_upload_history(job_id);
        ''')
        
        # Create platform connections table for multi-platform support
        cur.execute('''
            CREATE TABLE IF NOT EXISTS platform_connections (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                platform VARCHAR(50) NOT NULL, -- 'youtube', 'tiktok', etc.
                platform_user_id VARCHAR(255),
                platform_username VARCHAR(255),
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                scopes TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                metadata JSONB,
                UNIQUE(user_id, platform)
            );
            
            CREATE INDEX IF NOT EXISTS idx_platform_connections_user ON platform_connections(user_id);
            CREATE INDEX IF NOT EXISTS idx_platform_connections_platform ON platform_connections(platform);
        ''')
        
        conn.commit()
        print("✅ Migration 003: TikTok authentication support added successfully")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"❌ Migration 003 failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
