#!/usr/bin/env python3
"""
Migration to add support for anonymous clips
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import psycopg2
import os

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
    """Add anonymous clips support"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create anonymous_clips table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS anonymous_clips (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                job_id VARCHAR(255) UNIQUE NOT NULL,
                video_url TEXT NOT NULL,
                clip_path TEXT,
                clip_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
                converted_to_user_id INTEGER REFERENCES users(id),
                converted_at TIMESTAMP
            );
            
            CREATE INDEX idx_anonymous_clips_session ON anonymous_clips(session_id);
            CREATE INDEX idx_anonymous_clips_expires ON anonymous_clips(expires_at);
            CREATE INDEX idx_anonymous_clips_job ON anonymous_clips(job_id);
        ''')
        
        # Add session_id column to existing clips table (if needed)
        cur.execute('''
            ALTER TABLE upload_history 
            ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);
        ''')
        
        # Create cleanup function for expired anonymous clips
        cur.execute('''
            CREATE OR REPLACE FUNCTION cleanup_expired_anonymous_clips()
            RETURNS void AS $$
            BEGIN
                DELETE FROM anonymous_clips 
                WHERE expires_at < CURRENT_TIMESTAMP 
                AND converted_to_user_id IS NULL;
            END;
            $$ LANGUAGE plpgsql;
        ''')
        
        conn.commit()
        print("✅ Migration 002: Anonymous clips support added successfully")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"❌ Migration 002 failed: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
