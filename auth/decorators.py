"""
Authentication decorators and helper functions
"""

import logging
from functools import wraps
from typing import Optional

from flask import session, jsonify, g, request

from .models import User, UserSession

logger = logging.getLogger(__name__)


def get_current_user() -> Optional[User]:
    """Get the current authenticated user"""
    # Check if already loaded in this request
    if hasattr(g, 'current_user'):
        return g.current_user
    
    # Try to get user from session
    user_id = session.get('user_id')
    session_token = session.get('session_token')
    
    if not user_id or not session_token:
        return None
    
    # Validate session and get user
    user = UserSession.get_user_by_session(session_token)
    
    if user and user.id == user_id:
        # Cache for this request
        g.current_user = user
        return user
    
    # Invalid session - clear it
    session.pop('user_id', None)
    session.pop('session_token', None)
    return None


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            # Check if this is an API request
            if request.path.startswith('/api/'):
                return jsonify({
                    'error': 'Authentication required',
                    'status': 'unauthenticated'
                }), 401
            else:
                # For web routes, you might want to redirect to login
                return jsonify({
                    'error': 'Please sign in with Google to continue'
                }), 401
        
        # User is authenticated
        return f(*args, **kwargs)
    
    return decorated_function


def youtube_service_required(f):
    """Decorator to ensure YouTube service is available"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        from .oauth_manager import oauth_manager
        
        user = get_current_user()
        youtube_service = oauth_manager.get_youtube_service(user)
        
        if not youtube_service:
            return jsonify({
                'error': 'YouTube service unavailable. Please re-authenticate.',
                'status': 'service_error'
            }), 503
        
        # Add service to g for use in the route
        g.youtube_service = youtube_service
        
        return f(*args, **kwargs)
    
    return decorated_function


def logout_user():
    """Logout the current user"""
    session_token = session.get('session_token')
    
    if session_token:
        # Invalidate session in database
        UserSession.invalidate_session(session_token)
    
    # Clear Flask session
    session.pop('user_id', None)
    session.pop('session_token', None)
    
    # Clear cached user
    if hasattr(g, 'current_user'):
        delattr(g, 'current_user')
