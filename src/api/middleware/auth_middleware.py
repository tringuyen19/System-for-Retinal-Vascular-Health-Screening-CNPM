"""
Authentication Middleware for JWT token validation
"""

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from api.responses import error_response

def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return error_response('Authentication required. Please provide a valid token.', 401)
    return decorated_function

def get_current_user():
    """Get current authenticated user ID from JWT token"""
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception:
        return None

def get_current_user_role():
    """Get current user's role from JWT token claims"""
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        return claims.get('role_id')
    except Exception:
        return None

def require_role(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role_id = claims.get('role_id')
                
                if user_role_id not in allowed_roles:
                    return error_response('Insufficient permissions. Required role not found.', 403)
                
                return f(*args, **kwargs)
            except Exception as e:
                return error_response('Authentication required. Please provide a valid token.', 401)
        return decorated_function
    return decorator

