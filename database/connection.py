"""
Database connection management for Clippy
Handles PostgreSQL connections with connection pooling
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from flask import g, current_app

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL database connections with pooling"""
    
    def __init__(self):
        self.connection_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._initialized = False
    
    def init_app(self, app):
        """Initialize database connection with Flask app"""
        # Get database configuration from environment or app config
        self.db_config = {
            'host': app.config.get('DB_HOST', os.getenv('DB_HOST', 'localhost')),
            'port': app.config.get('DB_PORT', os.getenv('DB_PORT', 5432)),
            'database': app.config.get('DB_NAME', os.getenv('DB_NAME', 'clippy')),
            'user': app.config.get('DB_USER', os.getenv('DB_USER', 'clippy_user')),
            'password': app.config.get('DB_PASSWORD', os.getenv('DB_PASSWORD', 'clippy_password'))
        }
        
        # Create connection pool
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                **self.db_config
            )
            self._initialized = True
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        if not self._initialized:
            raise RuntimeError("Database connection not initialized. Call init_app() first.")
        
        return self.connection_pool.getconn()
    
    def return_connection(self, connection):
        """Return a connection to the pool"""
        if self.connection_pool:
            self.connection_pool.putconn(connection)
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All database connections closed")


# Global database connection instance
db_connection = DatabaseConnection()


def init_db(app):
    """Initialize database connection with Flask app"""
    db_connection.init_app(app)
    
    # Register teardown function
    app.teardown_appcontext(close_db)


def get_db():
    """Get database connection for current request context"""
    if 'db_conn' not in g:
        g.db_conn = db_connection.get_connection()
    return g.db_conn


def close_db(error=None):
    """Close database connection for current request context"""
    conn = g.pop('db_conn', None)
    if conn is not None:
        if error:
            conn.rollback()
        db_connection.return_connection(conn)


@contextmanager
def get_db_cursor(commit=True):
    """Context manager for database operations with automatic commit/rollback"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        cursor.close()


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, commit: bool = True):
    """Execute a database query with error handling"""
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params)
        
        if fetch_one:
            return cursor.fetchone()
        elif cursor.description:  # Only fetch if there are results
            return cursor.fetchall()
        return None


def init_database_tables():
    """Initialize database tables if they don't exist"""
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        google_id VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255),
        name VARCHAR(255),
        picture_url TEXT,
        refresh_token TEXT,
        access_token TEXT,
        token_expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    );
    
    CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    """
    
    create_upload_history_table = """
    CREATE TABLE IF NOT EXISTS upload_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        video_id VARCHAR(255),
        video_title TEXT,
        video_url TEXT,
        upload_status VARCHAR(50),
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_upload_history_user_id ON upload_history(user_id);
    """
    
    create_sessions_table = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address VARCHAR(45),
        user_agent TEXT
    );
    
    CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
    CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
    """
    
    try:
        execute_query(create_users_table)
        execute_query(create_upload_history_table)
        execute_query(create_sessions_table)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise
