"""
Audit Log Controller - API endpoints for audit log operations
FR-37: Handle data compliance, audit logs, and privacy settings
"""

from flask import Blueprint, request
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_role
from infrastructure.repositories.audit_log_repository import AuditLogRepository
from infrastructure.databases.mssql import session
from services.audit_log_service import AuditLogService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import AuditLogCreateRequestSchema, AuditLogResponseSchema, AuditLogSearchRequestSchema
from domain.exceptions import NotFoundException, ValidationException

audit_log_bp = Blueprint('audit_log', __name__, url_prefix='/api/admin/audit-logs')

# Initialize repository
audit_log_repo = AuditLogRepository(session)

# Initialize SERVICE (Business Logic Layer) ✅
audit_log_service = AuditLogService(audit_log_repo)


@audit_log_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Audit Log
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Audit log service is running")


# ========== FR-37: Audit Log Management ==========

@audit_log_bp.route('', methods=['POST'])
@require_role('Admin')
def create_audit_log():
    """
    Create audit log entry (FR-37)
    ---
    tags:
      - Audit Log
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
            - action_type
            - entity_type
          properties:
            account_id:
              type: integer
              description: Account ID of user performing action (null for system actions)
            action_type:
              type: string
              example: "create"
              enum: [create, update, delete, approve, suspend, login, logout]
            entity_type:
              type: string
              example: "clinic"
              enum: [account, clinic, patient, doctor, ai_config, subscription]
            entity_id:
              type: integer
              description: ID of entity being modified
            old_values:
              type: object
              description: Dictionary of old values (will be converted to JSON)
            new_values:
              type: object
              description: Dictionary of new values (will be converted to JSON)
            description:
              type: string
              example: "Clinic approved by admin"
            ip_address:
              type: string
              example: "192.168.1.1"
            user_agent:
              type: string
              example: "Mozilla/5.0..."
    responses:
      201:
        description: Audit log created successfully
      400:
        description: Invalid input
    """
    try:
        # Get IP address and user agent from request
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Validate request
        schema = AuditLogCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # Create audit log
        audit_log = audit_log_service.create_log(
            account_id=data.get('account_id'),
            action_type=data['action_type'],
            entity_type=data['entity_type'],
            entity_id=data.get('entity_id'),
            old_values=data.get('old_values'),
            new_values=data.get('new_values'),
            description=data.get('description'),
            ip_address=ip_address or data.get('ip_address'),
            user_agent=user_agent or data.get('user_agent')
        )
        
        response_schema = AuditLogResponseSchema()
        return success_response(response_schema.dump(audit_log), "Audit log created successfully", 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValidationException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@audit_log_bp.route('/<int:audit_log_id>', methods=['GET'])
@require_role('Admin')
def get_audit_log(audit_log_id):
    """
    Get audit log by ID (FR-37)
    ---
    tags:
      - Audit Log
    security:
      - Bearer: []
    parameters:
      - name: audit_log_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Audit log retrieved successfully
      404:
        description: Audit log not found
    """
    try:
        audit_log = audit_log_service.get_by_id(audit_log_id)
        schema = AuditLogResponseSchema()
        return success_response(schema.dump(audit_log))
    except NotFoundException as e:
        return not_found_response(str(e))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@audit_log_bp.route('', methods=['GET'])
def get_audit_logs():
    """
    Get audit logs with filters and pagination (FR-37)
    ---
    tags:
      - Audit Log
    parameters:
      - name: account_id
        in: query
        required: false
        schema:
          type: integer
      - name: action_type
        in: query
        required: false
        schema:
          type: string
          enum: [create, update, delete, approve, suspend, login, logout]
      - name: entity_type
        in: query
        required: false
        schema:
          type: string
          enum: [account, clinic, patient, doctor, ai_config, subscription]
      - name: entity_id
        in: query
        required: false
        schema:
          type: integer
      - name: start_date
        in: query
        required: false
        schema:
          type: string
          format: date
      - name: end_date
        in: query
        required: false
        schema:
          type: string
          format: date
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 50
          maximum: 1000
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
    responses:
      200:
        description: Audit logs retrieved successfully
    """
    try:
        from datetime import datetime as dt
        
        # Parse query parameters
        account_id = request.args.get('account_id', type=int)
        action_type = request.args.get('action_type')
        entity_type = request.args.get('entity_type')
        entity_id = request.args.get('entity_id', type=int)
        
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        start_date = dt.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = dt.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate with schema
        schema = AuditLogSearchRequestSchema()
        search_data = schema.load({
            'account_id': account_id,
            'action_type': action_type,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'start_date': start_date,
            'end_date': end_date,
            'limit': limit,
            'offset': offset
        })
        
        # Search audit logs
        audit_logs = audit_log_service.search_logs(
            account_id=search_data.get('account_id'),
            action_type=search_data.get('action_type'),
            entity_type=search_data.get('entity_type'),
            entity_id=search_data.get('entity_id'),
            start_date=search_data.get('start_date'),
            end_date=search_data.get('end_date'),
            limit=search_data.get('limit'),
            offset=search_data.get('offset', 0)
        )
        
        response_schema = AuditLogResponseSchema(many=True)
        total_count = audit_log_service.count()
        
        return success_response({
            'count': len(audit_logs),
            'total': total_count,
            'offset': offset,
            'limit': limit,
            'logs': response_schema.dump(audit_logs)
        })
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValidationException as e:
        return error_response(str(e), 400)
    except ValueError as e:
        return error_response(f'Invalid date format: {str(e)}', 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@audit_log_bp.route('/stats', methods=['GET'])
@require_role('Admin')
def get_audit_statistics():
    """
    Get audit log statistics (FR-37)
    ---
    tags:
      - Audit Log
    security:
      - Bearer: []
    responses:
      200:
        description: Audit log statistics retrieved successfully
    """
    try:
        stats = audit_log_service.get_statistics()
        return success_response(stats, "Audit log statistics retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@audit_log_bp.route('/by-account/<int:account_id>', methods=['GET'])
@require_role('Admin')
def get_logs_by_account(account_id):
    """
    Get audit logs by account ID (FR-37)
    ---
    tags:
      - Audit Log
    security:
      - Bearer: []
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 50
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
    responses:
      200:
        description: Audit logs retrieved successfully
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        audit_logs = audit_log_service.get_by_account(account_id, limit=limit, offset=offset)
        schema = AuditLogResponseSchema(many=True)
        
        return success_response({
            'count': len(audit_logs),
            'account_id': account_id,
            'logs': schema.dump(audit_logs)
        })
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@audit_log_bp.route('/by-action/<action_type>', methods=['GET'])
@require_role('Admin')
def get_logs_by_action(action_type):
    """
    Get audit logs by action type (FR-37)
    ---
    tags:
      - Audit Log
    security:
      - Bearer: []
    parameters:
      - name: action_type
        in: path
        required: true
        schema:
          type: string
          enum: [create, update, delete, approve, suspend, login, logout]
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 50
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
    responses:
      200:
        description: Audit logs retrieved successfully
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        audit_logs = audit_log_service.get_by_action_type(action_type, limit=limit, offset=offset)
        schema = AuditLogResponseSchema(many=True)
        
        return success_response({
            'count': len(audit_logs),
            'action_type': action_type,
            'logs': schema.dump(audit_logs)
        })
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@audit_log_bp.route('/by-entity/<entity_type>/<int:entity_id>', methods=['GET'])
@require_role('Admin')
def get_logs_by_entity(entity_type, entity_id):
    """
    Get audit logs for a specific entity (FR-37)
    ---
    tags:
      - Audit Log
    security:
      - Bearer: []
    parameters:
      - name: entity_type
        in: path
        required: true
        schema:
          type: string
      - name: entity_id
        in: path
        required: true
        schema:
          type: integer
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 50
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
    responses:
      200:
        description: Audit logs retrieved successfully
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        audit_logs = audit_log_service.get_by_entity(entity_type, entity_id, limit=limit, offset=offset)
        schema = AuditLogResponseSchema(many=True)
        
        return success_response({
            'count': len(audit_logs),
            'entity_type': entity_type,
            'entity_id': entity_id,
            'logs': schema.dump(audit_logs)
        })
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)