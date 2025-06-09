"""
User model and database operations
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from database.connection import execute_query, get_db_cursor
import json

logger = logging.getLogger(__name__)


class User:
    """User model for Clippy"""
    
    def __init__(self, user_id: int = None, google_id: str = None, 
                 email: str = None, name: str = None, picture_url: str = None,
                 refresh_token: str = None, access_token: str = None,
                 token_expires_at: datetime = None, created_at: datetime = None,
                 last_login: datetime = None, is_active: bool = True):
        self.id = user_id
        self.google_id = google_id
        self.email = email
        self.name = name
        self.picture_url = picture_url
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.token_expires_at = token_expires_at
        self.created_at = created_at
        self.last_login = last_login
        self.is_active = is_active
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User instance from dictionary"""
        return cls(
            user_id=data.get('id'),
            google_id=data.get('google_id'),
            email=data.get('email'),
            name=data.get('name'),
            picture_url=data.get('picture_url'),
            refresh_token=data.get('refresh_token'),
            access_token=data.get('access_token'),
            token_expires_at=data.get('token_expires_at'),
            created_at=data.get('created_at'),
            last_login=data.get('last_login'),
            is_active=data.get('is_active', True)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to dictionary"""
        return {
            'id': self.id,
            'google_id': self.google_id,
            'email': self.email,
            'name': self.name,
            'picture_url': self.picture_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def save(self) -> bool:
        """Save user to database"""
        try:
            if self.id:
                # Update existing user
                query = """
                UPDATE users 
                SET email = %s, name = %s, picture_url = %s, 
                    refresh_token = %s, access_token = %s, token_expires_at = %s,
                    last_login = %s, is_active = %s
                WHERE id = %s
                RETURNING id
                """
                params = (
                    self.email, self.name, self.picture_url,
                    self.refresh_token, self.access_token, self.token_expires_at,
                    self.last_login, self.is_active, self.id
                )
            else:
                # Insert new user
                query = """
                INSERT INTO users (google_id, email, name, picture_url, 
                                 refresh_token, access_token, token_expires_at, 
                                 last_login, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (google_id) 
                DO UPDATE SET 
                    email = EXCLUDED.email,
                    name = EXCLUDED.name,
                    picture_url = EXCLUDED.picture_url,
                    refresh_token = EXCLUDED.refresh_token,
                    access_token = EXCLUDED.access_token,
                    token_expires_at = EXCLUDED.token_expires_at,
                    last_login = EXCLUDED.last_login
                RETURNING id
                """
                params = (
                    self.google_id, self.email, self.name, self.picture_url,
                    self.refresh_token, self.access_token, self.token_expires_at,
                    self.last_login, self.is_active
                )
            
            result = execute_query(query, params, fetch_one=True)
            if result:
                self.id = result['id']
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
            return False
    
    @classmethod
    def get_by_id(cls, user_id: int) -> Optional['User']:
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
        result = execute_query(query, (user_id,), fetch_one=True)
        
        if result:
            return cls.from_dict(result)
        return None
    
    @classmethod
    def get_by_google_id(cls, google_id: str) -> Optional['User']:
        """Get user by Google ID"""
        query = "SELECT * FROM users WHERE google_id = %s"
        result = execute_query(query, (google_id,), fetch_one=True)
        
        if result:
            return cls.from_dict(result)
        return None
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional['User']:
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s AND is_active = TRUE"
        result = execute_query(query, (email,), fetch_one=True)
        
        if result:
            return cls.from_dict(result)
        return None
    
    def update_tokens(self, refresh_token: str, access_token: str, expires_at: datetime) -> bool:
        """Update user tokens"""
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.token_expires_at = expires_at
        return self.save()
    
    def update_last_login(self) -> bool:
        """Update user's last login timestamp"""
        self.last_login = datetime.utcnow()
        return self.save()
    
    def deactivate(self) -> bool:
        """Deactivate user account"""
        self.is_active = False
        return self.save()
    
    def add_upload_history(self, video_id: str, video_title: str, 
                          video_url: str, status: str = 'completed') -> bool:
        """Add upload history for user"""
        query = """
        INSERT INTO upload_history (user_id, video_id, video_title, video_url, upload_status)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            execute_query(query, (self.id, video_id, video_title, video_url, status))
            return True
        except Exception as e:
            logger.error(f"Failed to add upload history: {e}")
            return False
    
    def get_upload_history(self, limit: int = 50) -> list:
        """Get user's upload history"""
        query = """
        SELECT * FROM upload_history 
        WHERE user_id = %s 
        ORDER BY uploaded_at DESC 
        LIMIT %s
        """
        return execute_query(query, (self.id, limit))


class UserSession:
    """Manages user sessions"""
    
    @staticmethod
    def create_session(user_id: int, session_token: str, expires_at: datetime,
                      ip_address: str = None, user_agent: str = None) -> bool:
        """Create a new user session"""
        query = """
        INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            execute_query(query, (user_id, session_token, expires_at, ip_address, user_agent))
            return True
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return False
    
    @staticmethod
    def get_user_by_session(session_token: str) -> Optional[User]:
        """Get user by valid session token"""
        query = """
        SELECT u.* FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE s.session_token = %s 
        AND s.expires_at > NOW()
        AND u.is_active = TRUE
        """
        result = execute_query(query, (session_token,), fetch_one=True)
        
        if result:
            # Update last accessed
            update_query = """
            UPDATE user_sessions 
            SET last_accessed = NOW() 
            WHERE session_token = %s
            """
            execute_query(update_query, (session_token,))
            
            return User.from_dict(result)
        return None
    
    @staticmethod
    def invalidate_session(session_token: str) -> bool:
        """Invalidate a session"""
        query = "DELETE FROM user_sessions WHERE session_token = %s"
        try:
            execute_query(query, (session_token,))
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate session: {e}")
            return False
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """Clean up expired sessions"""
        query = "DELETE FROM user_sessions WHERE expires_at < NOW()"
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")
            return 0


class PlatformConnection:
    """Manages platform connections for users"""
    
    @staticmethod
    def create_or_update(user_id: int, platform: str, platform_user_id: str,
                        platform_username: str = None, access_token: str = None,
                        refresh_token: str = None, token_expires_at: datetime = None,
                        scopes: str = None, metadata: Dict = None) -> bool:
        """Create or update a platform connection"""
        query = """
        INSERT INTO platform_connections 
        (user_id, platform, platform_user_id, platform_username, 
         access_token, refresh_token, token_expires_at, scopes, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, platform) 
        DO UPDATE SET 
            platform_user_id = EXCLUDED.platform_user_id,
            platform_username = EXCLUDED.platform_username,
            access_token = EXCLUDED.access_token,
            refresh_token = EXCLUDED.refresh_token,
            token_expires_at = EXCLUDED.token_expires_at,
            scopes = EXCLUDED.scopes,
            metadata = EXCLUDED.metadata,
            is_active = TRUE,
            last_used_at = NOW()
        RETURNING id
        """
        
        try:
            # Convert metadata dict to JSON
            metadata_json = json.dumps(metadata) if metadata else None
            
            result = execute_query(
                query, 
                (user_id, platform, platform_user_id, platform_username,
                 access_token, refresh_token, token_expires_at, scopes, metadata_json),
                fetch_one=True
            )
            return result is not None
        except Exception as e:
            logger.error(f"Failed to create/update platform connection: {e}")
            return False
    
    @staticmethod
    def get_connection(user_id: int, platform: str) -> Optional[Dict]:
        """Get a specific platform connection for a user"""
        query = """
        SELECT * FROM platform_connections 
        WHERE user_id = %s AND platform = %s AND is_active = TRUE
        """
        
        result = execute_query(query, (user_id, platform), fetch_one=True)
        if result:
            # Parse JSON metadata
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            return result
        return None
    
    @staticmethod
    def get_user_connections(user_id: int) -> list:
        """Get all platform connections for a user"""
        query = """
        SELECT * FROM platform_connections 
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY connected_at DESC
        """
        
        results = execute_query(query, (user_id,))
        
        # Parse JSON metadata for each result
        for result in results:
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
        
        return results
    
    @staticmethod
    def update_tokens(user_id: int, platform: str, access_token: str,
                     refresh_token: str, expires_at: datetime) -> bool:
        """Update tokens for a platform connection"""
        query = """
        UPDATE platform_connections 
        SET access_token = %s, refresh_token = %s, token_expires_at = %s,
            last_used_at = NOW()
        WHERE user_id = %s AND platform = %s AND is_active = TRUE
        """
        
        try:
            execute_query(
                query,
                (access_token, refresh_token, expires_at, user_id, platform)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update platform tokens: {e}")
            return False
    
    @staticmethod
    def deactivate_connection(user_id: int, platform: str) -> bool:
        """Deactivate a platform connection"""
        query = """
        UPDATE platform_connections 
        SET is_active = FALSE 
        WHERE user_id = %s AND platform = %s
        """
        
        try:
            execute_query(query, (user_id, platform))
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate platform connection: {e}")
            return False
    
    @staticmethod
    def update_last_used(user_id: int, platform: str) -> bool:
        """Update last used timestamp for a connection"""
        query = """
        UPDATE platform_connections 
        SET last_used_at = NOW() 
        WHERE user_id = %s AND platform = %s AND is_active = TRUE
        """
        
        try:
            execute_query(query, (user_id, platform))
            return True
        except Exception as e:
            logger.error(f"Failed to update last used: {e}")
            return False
