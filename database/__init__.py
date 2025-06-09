"""Database package for Clippy multi-user support"""

import os
import psycopg2
from .connection import get_db, init_db, close_db

def get_db_connection():
    """Get a direct database connection (for use outside Flask request context)"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME', 'clippy'),
        user=os.getenv('DB_USER', 'clippy_user'),
        password=os.getenv('DB_PASSWORD', 'clippy_password')
    )

__all__ = ['get_db', 'init_db', 'close_db', 'get_db_connection']
