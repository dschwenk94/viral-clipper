"""
Initial database migration for multi-user support
Run this script to create the necessary database tables
"""

import os
import sys
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection, init_database_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    """Run the initial database migration"""
    print("Running initial database migration...")
    
    # Initialize connection
    class FakeApp:
        config = {
            'DB_HOST': os.getenv('DB_HOST', 'localhost'),
            'DB_PORT': os.getenv('DB_PORT', 5432),
            'DB_NAME': os.getenv('DB_NAME', 'clippy'),
            'DB_USER': os.getenv('DB_USER', 'clippy_user'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', 'clippy_password')
        }
    
    try:
        # Initialize database connection
        db_connection.init_app(FakeApp())
        
        # Create tables
        init_database_tables()
        
        print("✅ Database migration completed successfully!")
        print("Tables created:")
        print("  - users")
        print("  - upload_history")
        print("  - user_sessions")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        db_connection.close_all_connections()


if __name__ == "__main__":
    run_migration()
