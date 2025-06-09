"""
Multi-platform OAuth Manager for Clippy
Supports Google/YouTube and TikTok authentication
"""

import os
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime

from flask import session, request

from .oauth_manager import OAuthManager as GoogleOAuthManager
from .tiktok.oauth_handler import TikTokOAuthHandler
from .models import User, UserSession, PlatformConnection
from .token_manager import token_manager

logger = logging.getLogger(__name__)


class MultiPlatformOAuthManager:
    """Manages OAuth for multiple platforms"""
    
    def __init__(self):
        """Initialize multi-platform OAuth manager"""
        self.google_oauth = GoogleOAuthManager()
        self.tiktok_oauth = TikTokOAuthHandler()
        
        # Check configuration
        self.platforms_available = {
            'google': True,  # Always available for primary auth
            'tiktok': self.tiktok_oauth.is_configured()
        }
        
        if not self.platforms_available['tiktok']:
            logger.warning("TikTok OAuth not configured. Set TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET.")
    
    def get_available_platforms(self) -> Dict[str, bool]:
        """Get available platforms and their configuration status"""
        return self.platforms_available.copy()
    
    def initiate_platform_auth(
        self,
        platform: str,
        redirect_uri: str,
        user: Optional[User] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Initiate OAuth flow for a specific platform
        
        Args:
            platform: Platform name ('google' or 'tiktok')
            redirect_uri: OAuth callback URI
            user: Optional user for connecting additional platforms
            
        Returns:
            Tuple of (authorization_url, state) or (None, None) if failed
        """
        if platform == 'google':
            return self.google_oauth.get_authorization_url(redirect_uri)
        
        elif platform == 'tiktok':
            if not self.platforms_available['tiktok']:
                logger.error("TikTok OAuth not configured")
                return None, None
            
            # Store platform info in session for callback
            session['oauth_platform'] = 'tiktok'
            if user:
                session['connecting_user_id'] = user.id
            
            return self.tiktok_oauth.get_authorization_url(redirect_uri)
        
        else:
            logger.error(f"Unknown platform: {platform}")
            return None, None
    
    def handle_platform_callback(
        self,
        platform: str,
        authorization_response: str,
        state: str,
        redirect_uri: str
    ) -> Optional[User]:
        """
        Handle OAuth callback for a specific platform
        
        Args:
            platform: Platform name
            authorization_response: Full callback URL
            state: OAuth state for CSRF protection
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            User object or None if failed
        """
        if platform == 'google':
            # Primary authentication via Google
            return self.google_oauth.handle_oauth_callback(
                authorization_response, state, redirect_uri
            )
        
        elif platform == 'tiktok':
            # Handle TikTok connection
            return self._handle_tiktok_callback(
                authorization_response, state, redirect_uri
            )
        
        else:
            logger.error(f"Unknown platform for callback: {platform}")
            return None
    
    def _handle_tiktok_callback(
        self,
        authorization_response: str,
        state: str,
        redirect_uri: str
    ) -> Optional[User]:
        """Handle TikTok OAuth callback"""
        try:
            # Extract code from callback URL
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(authorization_response)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]
            
            if not code:
                logger.error("No authorization code in TikTok callback")
                return None
            
            # Exchange code for tokens
            token_data = self.tiktok_oauth.exchange_code_for_token(code, redirect_uri)
            if not token_data:
                return None
            
            # Get TikTok user info
            tiktok_user_info = self.tiktok_oauth.get_user_info(
                token_data['access_token']
            )
            if not tiktok_user_info:
                return None
            
            # Check if we're connecting to existing user or creating new
            connecting_user_id = session.pop('connecting_user_id', None)
            
            if connecting_user_id:
                # Connect TikTok to existing user
                user = User.get_by_id(connecting_user_id)
                if user:
                    self._save_tiktok_connection(user, tiktok_user_info, token_data)
                    return user
                else:
                    logger.error(f"User {connecting_user_id} not found for TikTok connection")
                    return None
            else:
                # TikTok-only auth not supported - must have Google account first
                logger.error("TikTok authentication requires existing Google account")
                return None
                
        except Exception as e:
            logger.error(f"TikTok callback failed: {e}")
            return None
    
    def _save_tiktok_connection(
        self,
        user: User,
        tiktok_user_info: Dict,
        token_data: Dict
    ) -> bool:
        """Save TikTok connection for a user"""
        try:
            # Encrypt tokens
            encrypted_access = token_manager.encrypt_token(token_data['access_token'])
            encrypted_refresh = token_manager.encrypt_token(token_data['refresh_token'])
            
            # Save to platform_connections table
            connection = PlatformConnection.create_or_update(
                user_id=user.id,
                platform='tiktok',
                platform_user_id=tiktok_user_info['open_id'],
                platform_username=tiktok_user_info.get('display_name'),
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                token_expires_at=datetime.fromisoformat(token_data['expires_at']),
                scopes=','.join(token_data.get('scope', '').split()),
                metadata={
                    'avatar_url': tiktok_user_info.get('avatar_url'),
                    'bio_description': tiktok_user_info.get('bio_description'),
                    'is_verified': tiktok_user_info.get('is_verified'),
                    'follower_count': tiktok_user_info.get('follower_count'),
                    'following_count': tiktok_user_info.get('following_count'),
                    'likes_count': tiktok_user_info.get('likes_count'),
                    'video_count': tiktok_user_info.get('video_count')
                }
            )
            
            if connection:
                logger.info(f"Connected TikTok account {tiktok_user_info.get('display_name')} to user {user.email}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to save TikTok connection: {e}")
            return False
    
    def get_platform_connections(self, user: User) -> Dict[str, Dict]:
        """Get all platform connections for a user"""
        connections = {}
        
        # Google/YouTube is always primary
        connections['google'] = {
            'connected': True,
            'email': user.email,
            'name': user.name,
            'picture_url': user.picture_url
        }
        
        # Get other platform connections
        platform_conns = PlatformConnection.get_user_connections(user.id)
        
        for conn in platform_conns:
            connections[conn['platform']] = {
                'connected': conn['is_active'],
                'username': conn['platform_username'],
                'connected_at': conn['connected_at'],
                'metadata': conn.get('metadata', {})
            }
        
        return connections
    
    def disconnect_platform(self, user: User, platform: str) -> bool:
        """Disconnect a platform from user account"""
        if platform == 'google':
            # Can't disconnect primary authentication
            logger.error("Cannot disconnect primary Google authentication")
            return False
        
        try:
            connection = PlatformConnection.get_connection(user.id, platform)
            if not connection:
                return True  # Already disconnected
            
            # Revoke tokens based on platform
            if platform == 'tiktok':
                # Get decrypted token
                access_token = token_manager.decrypt_token(connection['access_token'])
                if access_token:
                    self.tiktok_oauth.revoke_token(access_token)
            
            # Mark as inactive in database
            return PlatformConnection.deactivate_connection(user.id, platform)
            
        except Exception as e:
            logger.error(f"Failed to disconnect {platform}: {e}")
            return False
    
    def get_tiktok_client(self, user: User) -> Optional['TikTokAPIClient']:
        """Get TikTok API client for a user"""
        try:
            connection = PlatformConnection.get_connection(user.id, 'tiktok')
            if not connection or not connection['is_active']:
                logger.error("No active TikTok connection for user")
                return None
            
            # Check token expiry
            if connection['token_expires_at'] < datetime.utcnow():
                # Refresh token
                refresh_token = token_manager.decrypt_token(connection['refresh_token'])
                new_tokens = self.tiktok_oauth.refresh_access_token(refresh_token)
                
                if new_tokens:
                    # Update tokens
                    PlatformConnection.update_tokens(
                        user.id,
                        'tiktok',
                        token_manager.encrypt_token(new_tokens['access_token']),
                        token_manager.encrypt_token(new_tokens['refresh_token']),
                        datetime.fromisoformat(new_tokens['expires_at'])
                    )
                    
                    access_token = new_tokens['access_token']
                else:
                    logger.error("Failed to refresh TikTok token")
                    return None
            else:
                # Use existing token
                access_token = token_manager.decrypt_token(connection['access_token'])
            
            if not access_token:
                logger.error("No valid TikTok access token")
                return None
            
            # Import here to avoid circular imports
            from .tiktok.api_client import TikTokAPIClient
            return TikTokAPIClient(access_token)
            
        except Exception as e:
            logger.error(f"Failed to get TikTok client: {e}")
            return None


# Global multi-platform OAuth manager
multi_platform_oauth = MultiPlatformOAuthManager()
