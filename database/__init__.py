"""Database package for Clippy multi-user support"""

from .connection import get_db, init_db, close_db

__all__ = ['get_db', 'init_db', 'close_db']
