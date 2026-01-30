from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_roles, require_role
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.role_repository import RoleRepository
from infrastructure.databases.mssql import session
from services.account_service import AccountService
from services.role_service import RoleService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import AccountCreateRequestSchema, AccountUpdateRequestSchema, AccountResponseSchema
from datetime import datetime

account_bp = Blueprint('account', __name__, url_prefix='/api/accounts')

# Initialize repositories (only for service initialization)
account_repo = AccountRepository(session)
role_repo = RoleRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
account_service = AccountService(account_repo)
role_service = RoleService(role_repo)


@account_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Account
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Account service is running")


@account_bp.route('', methods=['POST'])
@require_role('Admin')
def create_account():
    """
    Create a new account
    ---
    tags:
      - Account
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
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
              example: "user@example.com"
            password:
              type: string
              format: password
              example: "MySecurePassword123!"
              description: Plain text password (will be hashed automatically)
            role_id:
              type: integer
              example: 1
            clinic_id:
              type: integer
              example: 1
            status:
              type: string
              default: active
              example: "active"
    responses:
      201:
        description: Account created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Account created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # Validate request data with schema
        schema = AccountCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # Check if email already exists via SERVICE ✅
        if account_service.check_email_exists(data['email']):
            return error_response('Email already exists', 400)
        
        # Validate role exists via SERVICE ✅
        role = role_service.get_role_by_id(data['role_id'])
        if not role:
            return not_found_response('Role not found')
        
        # Create account (service will hash password automatically)
        account = account_service.create_account(
            email=data['email'],
            password=data['password'],
            role_id=data['role_id'],
            clinic_id=data.get('clinic_id'),
            status=data.get('status', 'active')
        )
        
        # Serialize response with schema
        response_schema = AccountResponseSchema()
        return success_response(response_schema.dump(account), 'Account created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/<int:account_id>', methods=['GET'])
def get_account(account_id):
    """
    Get account by ID
    ---
    tags:
      - Account
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Account found
      404:
        description: Account not found
    """
    try:
        account = account_service.get_account_by_id(account_id)
        if not account:
            return not_found_response('Account not found')
        
        # Serialize response with schema
        schema = AccountResponseSchema()
        return success_response(schema.dump(account))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/email/<email>', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_account_by_email(email):
    """
    Get account by email
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: email
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Account found
      404:
        description: Account not found
    """
    try:
        account = account_service.get_account_by_email(email)
        if not account:
            return not_found_response('Account not found')
        
        # Serialize response with schema
        schema = AccountResponseSchema()
        return success_response(schema.dump(account))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/role/<int:role_id>', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_accounts_by_role(role_id):
    """
    Get accounts by role
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: role_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of accounts
    """
    try:
        accounts = account_service.get_accounts_by_role(role_id)
        
        # Serialize response with schema
        schema = AccountResponseSchema(many=True)
        return success_response({
            'role_id': role_id,
            'count': len(accounts),
            'accounts': schema.dump(accounts)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/clinic/<int:clinic_id>', methods=['GET'])
@require_roles(['ClinicManager', 'Admin', 'Doctor'])
def get_accounts_by_clinic(clinic_id):
    """
    Get accounts by clinic
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of accounts
    """
    try:
        accounts = account_service.get_accounts_by_clinic(clinic_id)
        
        # Serialize response with schema
        schema = AccountResponseSchema(many=True)
        return success_response({
            'clinic_id': clinic_id,
            'count': len(accounts),
            'accounts': schema.dump(accounts)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/status/<status>', methods=['GET'])
@require_role('Admin')
def get_accounts_by_status(status):
    """
    Get accounts by status
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: status
        in: path
        required: true
        schema:
          type: string
          enum: [active, inactive, suspended]
    responses:
      200:
        description: List of accounts
    """
    try:
        accounts = account_service.get_accounts_by_status(status)
        
        # Serialize response with schema
        schema = AccountResponseSchema(many=True)
        return success_response({
            'status': status,
            'count': len(accounts),
            'accounts': schema.dump(accounts)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('', methods=['GET'])
@require_role('Admin')
def get_all_accounts():
    """
    Get all accounts
    ---
    tags:
      - Account
    security:
      - Bearer: []
    responses:
      200:
        description: List of all accounts
    """
    try:
        accounts = account_service.list_all_accounts()
        
        # Serialize response with schema
        schema = AccountResponseSchema(many=True)
        return success_response({
            'count': len(accounts),
            'accounts': schema.dump(accounts)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/<int:account_id>', methods=['PUT'])
@require_roles(['Patient', 'Admin'])
def update_account(account_id):
    """
    Update account
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            email:
              type: string
              example: "updated@example.com"
            role_id:
              type: integer
              example: 2
            clinic_id:
              type: integer
              example: 1
            status:
              type: string
              example: "active"
    responses:
      200:
        description: Account updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Account updated successfully
            data:
              type: object
      404:
        description: Account not found
    """
    try:
        # Validate request data with schema
        schema = AccountUpdateRequestSchema()
        data = schema.load(request.get_json())
        
        # If updating email, check if it already exists via SERVICE ✅
        if data.get('email'):
            existing = account_service.get_account_by_email(data['email'])
            if existing and existing.account_id != account_id:
                return error_response('Email already exists', 400)
        
        account = account_service.update_account(account_id, **data)
        if not account:
            return not_found_response('Account not found')
        
        # Serialize response with schema
        response_schema = AccountResponseSchema()
        return success_response(response_schema.dump(account), 'Account updated successfully')
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/<int:account_id>/password', methods=['PUT'])
@require_roles(['Patient', 'Admin'])
def update_password(account_id):
    """
    Update account password
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - new_password_hash
          properties:
            new_password_hash:
              type: string
              example: "new_hashed_password"
    responses:
      200:
        description: Password updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password updated successfully
            data:
              type: object
      400:
        description: New password hash is required
      404:
        description: Account not found
    """
    try:
        data = request.get_json()
        if not data.get('new_password_hash'):
            return validation_error_response({'new_password_hash': 'New password hash is required'})
        
        account = account_service.update_password(account_id, data['new_password_hash'])
        if not account:
            return not_found_response('Account not found')
        
        return success_response({
            'account_id': account.account_id
        }, 'Password updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/<int:account_id>/status', methods=['PUT'])
@require_role('Admin')
def update_status(account_id):
    """
    Update account status
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [active, inactive, suspended]
              example: "active"
    responses:
      200:
        description: Status updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Status updated successfully
            data:
              type: object
      400:
        description: Status is required
      404:
        description: Account not found
    """
    try:
        data = request.get_json()
        if not data.get('status'):
            return validation_error_response({'status': 'Status is required'})
        
        account = account_service.update_status(account_id, data['status'])
        if not account:
            return not_found_response('Account not found')
        
        return success_response({
            'account_id': account.account_id,
            'status': account.status
        }, 'Status updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/<int:account_id>', methods=['DELETE'])
@require_role('Admin')
def delete_account(account_id):
    """
    Delete account
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Account deleted successfully
      404:
        description: Account not found
    """
    try:
        result = account_service.delete_account(account_id)
        if not result:
            return not_found_response('Account not found')
        
        return success_response(None, 'Account deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/check-email', methods=['POST'])
def check_email_exists():
    """
    Check if email exists (Public endpoint for registration)
    ---
    tags:
      - Account
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              example: "user@example.com"
    responses:
      200:
        description: Check result
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
      400:
        description: Email is required
    """
    try:
        data = request.get_json()
        if not data.get('email'):
            return validation_error_response({'email': 'Email is required'})
        
        exists = account_service.check_email_exists(data['email'])
        
        return success_response({
            'email': data['email'],
            'exists': exists
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@account_bp.route('/stats', methods=['GET'])
@require_role('Admin')
def get_stats():
    """
    Get account statistics
    ---
    tags:
      - Account
    security:
      - Bearer: []
    parameters:
      - name: role_id
        in: query
        required: false
        schema:
          type: integer
      - name: status
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: Account statistics
    """
    try:
        role_id = request.args.get('role_id', type=int)
        status = request.args.get('status')
        
        if role_id:
            count = account_service.count_by_role(role_id)
            return success_response({
                'role_id': role_id,
                'count': count
            })
        elif status:
            count = account_service.count_by_status(status)
            return success_response({
                'status': status,
                'count': count
            })
        else:
            stats = account_service.get_account_statistics()
            
            return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)




