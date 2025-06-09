"""
TikTok OAuth Handler for Clippy
Handles TikTok OAuth 2.0 authentication flow
"""

import os
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from urllib.parse import urlencode, urlparse, parse_qs

import requests
from flask import current_app, session

logger = logging.getLogger(__name__)


class TikTokOAuthHandler:
    """Handles TikTok OAuth 2.0 authentication"""
    
    # TikTok OAuth endpoints (v2)
    AUTHORIZATION_BASE_URL = 'https://www.tiktok.com/v2/auth/authorize/'
    TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token/'
    REVOKE_URL = 'https://open.tiktokapis.com/v2/oauth/revoke/'
    USER_INFO_URL = 'https://open.tiktokapis.com/v2/user/info/'
    
    # Required scopes for video upload
    REQUIRED_SCOPES = [
        'user.info.basic',      # Basic user info
        'video.upload',         # Upload videos
        'video.publish',        # Publish videos
        'video.list',          # List user's videos
    ]
    
    def __init__(self):
        """Initialize TikTok OAuth handler"""
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        
        if not self.client_key or not self.client_secret:
            logger.warning("TikTok OAuth credentials not configured")
    
    def is_configured(self) -> bool:
        """Check if TikTok OAuth is properly configured"""
        return bool(self.client_key and self.client_secret)
    
    def get_authorization_url(self, redirect_uri: str) -> Tuple[str, str]:
        """
        Generate TikTok authorization URL
        
        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.is_configured():
            raise ValueError("TikTok OAuth not configured")
        
        # Generate secure state token
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        params = {
            'client_key': self.client_key,
            'scope': ','.join(self.REQUIRED_SCOPES),
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'state': state
        }
        
        authorization_url = self.AUTHORIZATION_BASE_URL + '?' + urlencode(params)
        
        logger.info(f"Generated TikTok auth URL with scopes: {self.REQUIRED_SCOPES}")
        
        return authorization_url, state
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Optional[Dict]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from TikTok
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Token response dict or None if failed
        """
        if not self.is_configured():
            raise ValueError("TikTok OAuth not configured")
        
        try:
            # Prepare token request
            data = {
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }
            
            # Request access token
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            if 'access_token' in token_data:
                logger.info(f"Successfully obtained TikTok access token for user: {token_data.get('open_id')}")
                
                # Add timestamps
                token_data['obtained_at'] = datetime.utcnow().isoformat()
                token_data['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 86400))
                ).isoformat()
                
                return token_data
            else:
                logger.error(f"TikTok token response missing access_token: {token_data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to exchange TikTok code for token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error exchanging TikTok code: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """
        Refresh TikTok access token
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token response dict or None if failed
        """
        if not self.is_configured():
            raise ValueError("TikTok OAuth not configured")
        
        try:
            data = {
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }
            
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            if 'access_token' in token_data:
                logger.info("Successfully refreshed TikTok access token")
                
                # Add timestamps
                token_data['obtained_at'] = datetime.utcnow().isoformat()
                token_data['expires_at'] = (
                    datetime.utcnow() + timedelta(seconds=token_data.get('expires_in', 86400))
                ).isoformat()
                
                return token_data
            else:
                logger.error(f"TikTok refresh response missing access_token: {token_data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refresh TikTok token: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error refreshing TikTok token: {e}")
            return None
    
    def revoke_token(self, access_token: str) -> bool:
        """
        Revoke TikTok access token
        
        Args:
            access_token: Access token to revoke
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            raise ValueError("TikTok OAuth not configured")
        
        try:
            data = {
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'token': access_token
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cache-Control': 'no-cache'
            }
            
            response = requests.post(
                self.REVOKE_URL,
                data=data,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            logger.info("Successfully revoked TikTok access token")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to revoke TikTok token: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error revoking TikTok token: {e}")
            return False
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """
        Get TikTok user information
        
        Args:
            access_token: Valid TikTok access token
            
        Returns:
            User info dict or None if failed
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            params = {
                'fields': 'open_id,union_id,avatar_url,avatar_url_100,display_name,bio_description,profile_deep_link,is_verified,follower_count,following_count,likes_count,video_count'
            }
            
            response = requests.get(
                self.USER_INFO_URL,
                headers=headers,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if 'data' in data and 'user' in data['data']:
                user_info = data['data']['user']
                logger.info(f"Retrieved TikTok user info for: {user_info.get('display_name')}")
                return user_info
            else:
                logger.error(f"Invalid TikTok user info response: {data}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get TikTok user info: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting TikTok user info: {e}")
            return None
    
    def validate_token(self, access_token: str) -> bool:
        """
        Validate TikTok access token by making a test API call
        
        Args:
            access_token: Access token to validate
            
        Returns:
            True if valid, False otherwise
        """
        user_info = self.get_user_info(access_token)
        return user_info is not None
