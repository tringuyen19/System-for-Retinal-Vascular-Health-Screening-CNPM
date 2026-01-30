"""
Authentication Controller - Login and Registration
"""

from flask import Blueprint, request
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