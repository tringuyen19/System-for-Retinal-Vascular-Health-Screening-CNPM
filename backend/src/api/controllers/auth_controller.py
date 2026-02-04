"""
Authentication Controller - Login and Registration
"""

from flask import Blueprint, request, redirect
from flask_jwt_extended import create_access_token, verify_jwt_in_request
from marshmallow import ValidationError

from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.role_repository import RoleRepository
from infrastructure.repositories.clinic_repository import ClinicRepository
from infrastructure.databases.mssql import session
from services.account_service import AccountService
from services.role_service import RoleService
from services.clinic_service import ClinicService
from api.responses import success_response, error_response, validation_error_response
from api.schemas import LoginRequestSchema, RegisterRequestSchema, AuthResponseSchema, AccountResponseSchema
from domain.exceptions import NotFoundException, ValidationException, ConflictException
from config import Config
from urllib.parse import urlencode, quote
import os

# Google OAuth dependencies (FR-1)
try:
    import requests as http_requests
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
except Exception:  # pragma: no cover - optional at runtime
    http_requests = None
    google_id_token = None
    google_requests = None

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize repositories
account_repo = AccountRepository(session)
role_repo = RoleRepository(session)
clinic_repo = ClinicRepository(session)

# Initialize services
account_service = AccountService(account_repo)
role_service = RoleService(role_repo)
clinic_service = ClinicService(clinic_repo)


def fix_authorization_header():
    """Auto-fix Authorization header: Add 'Bearer ' prefix if missing"""
    auth_header = request.headers.get('Authorization', '')
    if auth_header and not auth_header.startswith('Bearer '):
        # Check if it looks like a JWT token (starts with eyJ or is long enough)
        if auth_header.startswith('eyJ') or len(auth_header) > 50:
            # It's likely a token without Bearer prefix, modify the header
            # Flask request.headers is immutable, so we need to modify environ
            request.environ['HTTP_AUTHORIZATION'] = f'Bearer {auth_header}'


@auth_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Authentication service is running")


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - role_id
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              format: password
              minLength: 6
              example: password123
            role_id:
              type: integer
              example: 3
              description: Role ID (1=Admin, 2=Doctor, 3=Patient, 4=ClinicManager)
            clinic_id:
              type: integer
              example: 1
    responses:
      201:
        description: Account created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            data:
              type: object
              properties:
                access_token:
                  type: string
                account_id:
                  type: integer
                email:
                  type: string
                role_id:
                  type: integer
      400:
        description: Invalid input or email already exists
    """
    try:
        # Validate request data
        schema = RegisterRequestSchema()
        data = schema.load(request.get_json())
        
        # Validate role exists
        role = role_service.get_role_by_id(data['role_id'])
        if not role:
            return error_response('Role not found', 404)

        # ClinicManager must be created via clinic registration flow (FR-22)
        if data.get('role_id') == 4:
            return error_response('Vui lòng đăng ký phòng khám tại /clinic-register.html để tạo tài khoản quản lý phòng khám.', 400)
        
        # Validate clinic_id exists (if provided)
        if data.get('clinic_id'):
            clinic = clinic_service.get_clinic_by_id(data['clinic_id'])
            if not clinic:
                return error_response('Clinic not found', 404)
        
        # Create account (Service handles email validation, password hashing, and duplicate check)
        account = account_service.create_account(
            email=data['email'],
            password=data['password'],  # Plain password - Service will hash it
            role_id=data['role_id'],
            clinic_id=data.get('clinic_id'),
            status='active'
        )
        
        # Generate JWT token
        additional_claims = {
            'role_id': account.role_id,
            'email': account.email,
            'clinic_id': account.clinic_id
        }
        access_token = create_access_token(
            identity=str(account.account_id),  # JWT identity must be a string
            additional_claims=additional_claims
        )
        
        # Prepare response
        response_data = {
            'access_token': access_token,
            'account_id': account.account_id,
            'email': account.email,
            'role_id': account.role_id,
            'clinic_id': account.clinic_id
        }
        
        response_schema = AuthResponseSchema()
        return success_response(response_schema.dump(response_data), 'Account created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValidationException as e:
        return error_response(str(e), 400)
    except ConflictException as e:
        return error_response(str(e), 409)
    except NotFoundException as e:
        return error_response(str(e), 404)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              format: password
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
            data:
              type: object
              properties:
                access_token:
                  type: string
                account_id:
                  type: integer
                email:
                  type: string
                role_id:
                  type: integer
      401:
        description: Invalid credentials
      400:
        description: Invalid input
    """
    try:
        # Validate request data
        schema = LoginRequestSchema()
        data = schema.load(request.get_json())
        
        # Authenticate user (Service handles email check, status check, and password verification)
        account = account_service.authenticate(data['email'], data['password'])
        
        # Generate JWT token
        additional_claims = {
            'role_id': account.role_id,
            'email': account.email,
            'clinic_id': account.clinic_id
        }
        access_token = create_access_token(
            identity=str(account.account_id),  # JWT identity must be a string
            additional_claims=additional_claims
        )
        
        # Prepare response
        response_data = {
            'access_token': access_token,
            'account_id': account.account_id,
            'email': account.email,
            'role_id': account.role_id,
            'clinic_id': account.clinic_id
        }
        
        response_schema = AuthResponseSchema()
        return success_response(response_schema.dump(response_data), 'Login successful')
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValidationException as e:
        return error_response(str(e), 400)
    except ConflictException as e:
        return error_response(str(e), 409)
    except NotFoundException as e:
        return error_response(str(e), 404)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Forgot password - stub (chức năng đang phát triển).
    Trả về 501 để frontend hiển thị thông báo thân thiện, tránh 404.
    """
    return error_response(
        'Chức năng quên mật khẩu đang được cập nhật. Vui lòng liên hệ quản trị viên.',
        501
    )


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password - stub (chức năng đang phát triển).
    """
    return error_response(
        'Chức năng đặt lại mật khẩu đang được cập nhật. Vui lòng liên hệ quản trị viên.',
        501
    )


@auth_bp.route('/me', methods=['GET'])
def get_current_user_info():
    """
    Get current authenticated user information
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: User information
        schema:
          type: object
          properties:
            message:
              type: string
            data:
              type: object
              properties:
                account_id:
                  type: integer
                email:
                  type: string
                role_id:
                  type: integer
                clinic_id:
                  type: integer
                status:
                  type: string
      401:
        description: Authentication required
    """
    try:
        # Auto-fix Authorization header: Add "Bearer " prefix if missing
        fix_authorization_header()
        
        verify_jwt_in_request()
        from flask_jwt_extended import get_jwt_identity
        account_id_str = get_jwt_identity()
        
        if not account_id_str:
            return error_response('User not found', 404)
        
        # Convert string identity back to integer for database query
        try:
            account_id = int(account_id_str)
        except (ValueError, TypeError):
            return error_response('Invalid token format', 401)
        
        account = account_service.get_account_by_id(account_id)
        if not account:
            return error_response('User not found', 404)
        
        schema = AccountResponseSchema()
        return success_response(schema.dump(account), 'User information retrieved successfully')
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"JWT Verification Error: {str(e)}")
        print(traceback.format_exc())
        return error_response(f'Authentication required. Please provide a valid token. Error: {str(e)}', 401)


# ========== FR-1: Google OAuth Login ==========

@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    """
    Start Google OAuth2 login flow (FR-1).
    Redirects user to Google's consent screen.
    """
    client_id = Config.GOOGLE_CLIENT_ID
    redirect_uri = Config.GOOGLE_REDIRECT_URI
    if not client_id or not redirect_uri:
        return error_response('Google OAuth chưa được cấu hình. Vui lòng thiết lập GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET/GOOGLE_REDIRECT_URI.', 501)

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        'prompt': 'select_account',
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return redirect(url)


@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """
    Google OAuth2 callback (FR-1).
    - Nhận mã `code` từ Google
    - Đổi sang id_token, xác thực email
    - Tìm hoặc tạo account (role mặc định: Patient)
    - Sinh JWT giống login thường và redirect về frontend với ?google_token=
    """
    if http_requests is None or google_id_token is None or google_requests is None:
        return error_response('Máy chủ chưa cài đặt thư viện google-auth/requests.', 501)

    code = request.args.get('code')
    if not code:
        return error_response('Thiếu mã xác thực từ Google.', 400)

    client_id = Config.GOOGLE_CLIENT_ID
    client_secret = Config.GOOGLE_CLIENT_SECRET
    redirect_uri = Config.GOOGLE_REDIRECT_URI
    if not client_id or not client_secret or not redirect_uri:
        return error_response('Google OAuth chưa được cấu hình đầy đủ.', 501)

    try:
        # 1. Đổi code lấy token từ Google
        token_resp = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            },
            timeout=10,
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()
        id_token_str = token_data.get('id_token')
        if not id_token_str:
            return error_response('Không nhận được id_token từ Google.', 400)

        # 2. Verify id_token
        idinfo = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            client_id,
        )
        email = idinfo.get('email')
        email_verified = idinfo.get('email_verified')
        if not email or not email_verified:
            return error_response('Email Google chưa được xác minh.', 400)

        # 3. Tìm hoặc tạo account cho email này
        try:
            account = account_service.get_account_by_email(email)
        except NotFoundException:
            # Tạo account mới: mặc định Patient (role_id=3)
            # Mật khẩu random chỉ dùng nội bộ (user đăng nhập bằng Google)
            import secrets
            random_password = secrets.token_urlsafe(16)
            account = account_service.create_account(
                email=email,
                password=random_password,
                role_id=3,       # Patient
                clinic_id=None,
                status='active',
            )

        # 4. Sinh JWT như flow login/register
        additional_claims = {
            'role_id': account.role_id,
            'email': account.email,
            'clinic_id': account.clinic_id,
        }
        access_token = create_access_token(
            identity=str(account.account_id),
            additional_claims=additional_claims,
        )

        # 5. Redirect về frontend với ?google_token=
        frontend_base = Config.FRONTEND_BASE_URL.rstrip('/')
        # Dùng login.html làm điểm vào chung
        redirect_url = f"{frontend_base}/login.html?google_token={quote(access_token)}"
        return redirect(redirect_url)

    except Exception as e:
        # In log cho debug, nhưng trả về message gọn
        import traceback
        print("Google OAuth error:", e)
        print(traceback.format_exc())
        return error_response('Đăng nhập Google thất bại. Vui lòng thử lại.', 400)