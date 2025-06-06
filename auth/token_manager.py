"""
Token encryption and management
"""

import os
import base64
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages token encryption, decryption, and storage"""
    
    def __init__(self, secret_key: str = None):
        """Initialize TokenManager with encryption key"""
        if secret_key is None:
            secret_key = os.getenv('TOKEN_ENCRYPTION_KEY', '')
            
        if not secret_key:
            # Generate a new key if none provided (for development)
            logger.warning("No encryption key provided. Generating a new one.")
            logger.warning("Set TOKEN_ENCRYPTION_KEY environment variable in production!")
            secret_key = Fernet.generate_key().decode('utf-8')
        
        self.cipher = self._create_cipher(secret_key)
    
    def _create_cipher(self, secret_key: str) -> Fernet:
        """Create Fernet cipher from secret key"""
        # Ensure the key is properly formatted
        if len(secret_key) < 32:
            # Use PBKDF2 to derive a proper key from the secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'clippy-salt-2025',  # In production, use a random salt per user
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        else:
            # Assume it's already a proper Fernet key
            key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        
        return Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token"""
        try:
            if not token:
                return ""
            
            encrypted = self.cipher.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encrypt token: {e}")
            raise
    
    def decrypt_token(self, encrypted_token: str) -> Optional[str]:
        """Decrypt a token"""
        try:
            if not encrypted_token:
                return None
            
            decoded = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to decrypt token: {e}")
            return None
    
    def generate_session_token(self) -> str:
        """Generate a secure random session token"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    
    @staticmethod
    def calculate_token_expiry(expires_in: int) -> datetime:
        """Calculate token expiry time from expires_in seconds"""
        return datetime.utcnow() + timedelta(seconds=expires_in)
    
    @staticmethod
    def is_token_expired(expires_at: datetime) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() >= expires_at
    
    def prepare_tokens_for_storage(self, tokens: dict) -> Tuple[str, str, datetime]:
        """Prepare tokens received from OAuth for encrypted storage"""
        refresh_token = tokens.get('refresh_token', '')
        access_token = tokens.get('access_token', '')
        expires_in = tokens.get('expires_in', 3600)  # Default 1 hour
        
        # Encrypt tokens
        encrypted_refresh = self.encrypt_token(refresh_token) if refresh_token else None
        encrypted_access = self.encrypt_token(access_token) if access_token else None
        
        # Calculate expiry
        expires_at = self.calculate_token_expiry(expires_in)
        
        return encrypted_refresh, encrypted_access, expires_at
    
    def get_decrypted_tokens(self, user) -> Optional[dict]:
        """Get decrypted tokens from user object"""
        if not user or not user.refresh_token:
            return None
        
        refresh_token = self.decrypt_token(user.refresh_token)
        access_token = self.decrypt_token(user.access_token) if user.access_token else None
        
        if not refresh_token:
            return None
        
        return {
            'refresh_token': refresh_token,
            'access_token': access_token,
            'expires_at': user.token_expires_at
        }


# Global token manager instance
token_manager = TokenManager()
