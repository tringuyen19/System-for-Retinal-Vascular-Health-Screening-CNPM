"""
Authentication Middleware for JWT token validation
RBAC (Role-Based Access Control) Middleware
"""

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from api.responses import error_response
from typing import Union, List
from infrastructure.repositories.role_repository import RoleRepository
from infrastructure.databases.mssql import session

# Cache for role name to ID mapping (to avoid DB queries on every request)
_role_cache = {}

def _get_role_id_by_name(role_name: str) -> int:
    """Get role ID by role name (with caching)"""
    if role_name in _role_cache:
        return _role_cache[role_name]
    
    role_repo = RoleRepository(session)
    role = role_repo.get_by_name(role_name)
    if not role:
        raise ValueError(f"Role '{role_name}' not found")
    
    _role_cache[role_name] = role.role_id
    return role.role_id

def _get_role_ids_by_names(role_names: List[str]) -> List[int]:
    """Get role IDs by role names"""
    return [_get_role_id_by_name(name) for name in role_names]

def _fix_authorization_header():
    """Auto-fix Authorization header: Add 'Bearer ' prefix if missing"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header and not auth_header.startswith('Bearer '):
        # Check if it looks like a JWT token (starts with eyJ or is long enough)
        if auth_header.startswith('eyJ') or len(auth_header) > 50:
            # It's likely a token without Bearer prefix, add it
            # Flask request.headers is immutable, so we need to modify environ
            request.environ['HTTP_AUTHORIZATION'] = f'Bearer {auth_header}'

def jwt_required(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Auto-fix Authorization header before verifying JWT
            _fix_authorization_header()
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

def get_current_user_role_id():
    """Get current user's role ID from JWT token claims"""
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        return claims.get('role_id')
    except Exception:
        return None

def get_current_user_role():
    """Get current user's role ID from JWT token claims (backward compatibility)"""
    return get_current_user_role_id()

def get_current_user_role_name():
    """Get current user's role name from JWT token claims"""
    try:
        role_id = get_current_user_role_id()
        if not role_id:
            return None
        
        # Reverse lookup from cache or query DB
        role_repo = RoleRepository(session)
        role = role_repo.get_by_id(role_id)
        if role:
            _role_cache[role.role_name] = role.role_id
            return role.role_name
        return None
    except Exception:
        return None

def require_role(role_name: str):
    """
    Decorator to require a specific role by name
    Usage: @require_role('Admin')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                # Auto-fix Authorization header before verifying JWT
                _fix_authorization_header()
                verify_jwt_in_request()
                claims = get_jwt()
                user_role_id = claims.get('role_id')
                
                if not user_role_id:
                    return error_response('No role found in token.', 403)
                
                # Get required role ID
                required_role_id = _get_role_id_by_name(role_name)
                
                if user_role_id != required_role_id:
                    return error_response(
                        f'Insufficient permissions. Required role: {role_name}.', 
                        403
                    )
                
                return f(*args, **kwargs)
            except ValueError as e:
                return error_response(str(e), 400)
            except Exception as e:
                return error_response('Authentication required. Please provide a valid token.', 401)
        return decorated_function
    return decorator

def require_roles(role_names: List[str]):
    """
    Decorator to require one of multiple roles by names
    Usage: @require_roles(['Admin', 'Doctor'])
    """
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                # Auto-fix Authorization header before verifying JWT
                _fix_authorization_header()
                verify_jwt_in_request()
                claims = get_jwt()
                user_role_id = claims.get('role_id')
                
                if not user_role_id:
                    return error_response('No role found in token.', 403)
                
                # Get required role IDs
                required_role_ids = _get_role_ids_by_names(role_names)
                
                if user_role_id not in required_role_ids:
                    roles_str = ', '.join(role_names)
                    return error_response(
                        f'Insufficient permissions. Required one of: {roles_str}.', 
                        403
                    )
                
                return f(*args, **kwargs)
            except ValueError as e:
                return error_response(str(e), 400)
            except Exception as e:
                return error_response('Authentication required. Please provide a valid token.', 401)
        return decorated_function
    return decorator

# Legacy decorator (kept for backward compatibility)
def require_role_ids(*allowed_role_ids: int):
    """Decorator to require specific role ID(s) - Legacy version"""
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role_id = claims.get('role_id')
                
                if user_role_id not in allowed_role_ids:
                    return error_response('Insufficient permissions. Required role not found.', 403)
                
                return f(*args, **kwargs)
            except Exception as e:
                return error_response('Authentication required. Please provide a valid token.', 401)
        return decorated_function
    return decorator

