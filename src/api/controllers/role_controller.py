from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_role
from infrastructure.repositories.role_repository import RoleRepository
from infrastructure.databases.mssql import session
from services.role_service import RoleService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import RoleRequestSchema, RoleResponseSchema

role_bp = Blueprint('role', __name__, url_prefix='/api/roles')

# Initialize repository (only for service initialization)
role_repo = RoleRepository(session)

# Initialize SERVICE (Business Logic Layer) ✅
role_service = RoleService(role_repo)


@role_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Role
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Role service is running")


@role_bp.route('', methods=['POST'])
@require_role('Admin')
def create_role():
    """
    Create a new role
    ---
    tags:
      - Role
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
            - role_name
          properties:
            role_name:
              type: string
              example: "Patient"
    responses:
      201:
        description: Role created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Role created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate request data with schema
        schema = RoleRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Call SERVICE to create role ✅ (Service handles duplicate check)
        role = role_service.create_role(data['role_name'])
        
        # STEP 3: Serialize response with schema
        response_schema = RoleResponseSchema()
        return success_response(response_schema.dump(role), 'Role created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('/<int:role_id>', methods=['GET'])
def get_role(role_id):
    """
    Get role by ID
    ---
    tags:
      - Role
    parameters:
      - name: role_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Role found
      404:
        description: Role not found
    """
    try:
        # Call SERVICE ✅
        role = role_service.get_role_by_id(role_id)
        if not role:
            return not_found_response('Role not found')
        
        # Serialize response with schema
        schema = RoleResponseSchema()
        return success_response(schema.dump(role))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('/name/<role_name>', methods=['GET'])
@require_role('Admin')
def get_role_by_name(role_name):
    """
    Get role by name
    ---
    tags:
      - Role
    security:
      - Bearer: []
    parameters:
      - name: role_name
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Role found
      404:
        description: Role not found
    """
    try:
        # Call SERVICE ✅
        role = role_service.get_role_by_name(role_name)
        if not role:
            return not_found_response('Role not found')
        
        # Serialize response with schema
        schema = RoleResponseSchema()
        return success_response(schema.dump(role))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('', methods=['GET'])
@require_role('Admin')
def get_all_roles():
    """
    Get all roles
    ---
    tags:
      - Role
    security:
      - Bearer: []
    responses:
      200:
        description: List of all roles
    """
    try:
        # Call SERVICE ✅
        roles = role_service.list_all_roles()
        
        # Serialize response with schema
        schema = RoleResponseSchema(many=True)
        return success_response({
            'count': len(roles),
            'roles': schema.dump(roles)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('/<int:role_id>', methods=['PUT'])
@require_role('Admin')
def update_role(role_id):
    """
    Update role name
    ---
    tags:
      - Role
    security:
      - Bearer: []
    parameters:
      - name: role_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: role_id
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
            - role_name
          properties:
            role_name:
              type: string
              example: "Updated Role Name"
    responses:
      200:
        description: Role updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Role updated successfully
            data:
              type: object
      404:
        description: Role not found
    """
    try:
        # Validate request data with schema
        schema = RoleRequestSchema()
        data = schema.load(request.get_json())
        
        # Call SERVICE ✅
        role = role_service.update_role(role_id, data['role_name'])
        if not role:
            return not_found_response('Role not found')
        
        # Serialize response with schema
        response_schema = RoleResponseSchema()
        return success_response(response_schema.dump(role), 'Role updated successfully')
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@require_role('Admin')
def delete_role(role_id):
    """
    Delete role
    ---
    tags:
      - Role
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
        description: Role deleted successfully
      404:
        description: Role not found
    """
    try:
        # Call SERVICE ✅
        result = role_service.delete_role(role_id)
        if not result:
            return not_found_response('Role not found')
        
        return success_response(None, 'Role deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('/check-exists', methods=['POST'])
def check_role_exists():
    """
    Check if role exists
    ---
    tags:
      - Role
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
            - role_name
          properties:
            role_name:
              type: string
              example: "Patient"
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
        description: Invalid input
    """
    try:
        # Validate request data with schema
        schema = RoleRequestSchema()
        data = schema.load(request.get_json())
        
        # Call SERVICE ✅
        exists = role_service.check_role_exists(data['role_name'])
        
        return success_response({
            'role_name': data['role_name'],
            'exists': exists
        })
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@role_bp.route('/stats', methods=['GET'])
@require_role('Admin')
def get_stats():
    """
    Get role statistics
    ---
    tags:
      - Role
    security:
      - Bearer: []
    responses:
      200:
        description: Role statistics
    """
    try:
        # Call SERVICE ✅
        total = role_service.count_roles()
        
        return success_response({
            'total_roles': total
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

