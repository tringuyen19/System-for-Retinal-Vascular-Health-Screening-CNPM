"""
Notification Template Controller - API endpoints for notification template operations
FR-39: Manage notification templates and communication policies
"""

from flask import Blueprint, request
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_role
from infrastructure.repositories.notification_template_repository import NotificationTemplateRepository
from infrastructure.databases.mssql import session
from services.notification_template_service import NotificationTemplateService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import (
    NotificationTemplateCreateRequestSchema,
    NotificationTemplateUpdateRequestSchema,
    NotificationTemplateRenderRequestSchema,
    NotificationTemplateResponseSchema
)
from domain.exceptions import NotFoundException, ValidationException

notification_template_bp = Blueprint('notification_template', __name__, 
                                     url_prefix='/api/admin/notification-templates')

# Initialize repository and service
notification_template_repo = NotificationTemplateRepository(session)
notification_template_service = NotificationTemplateService(notification_template_repo)


@notification_template_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Notification Templates
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Notification template service is running")


# ========== FR-39: Notification Template Management ==========

@notification_template_bp.route('', methods=['POST'])
@require_role('Admin')
def create_template():
    """
    Create notification template (FR-39)
    ---
    tags:
      - Notification Templates
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
            - template_name
            - template_type
            - content_template
          properties:
            template_name:
              type: string
              example: "AI Result Ready"
            template_type:
              type: string
              example: "ai_result_ready"
            subject:
              type: string
              example: "Your AI Analysis is Ready"
            content_template:
              type: string
              example: "Hello {{patient_name}}, your AI analysis for image {{image_id}} is ready."
            variables_schema:
              type: object
              example: {"patient_name": "string", "image_id": "integer"}
            is_active:
              type: boolean
              default: false
    responses:
      201:
        description: Template created successfully
      400:
        description: Invalid input
    """
    try:
        schema = NotificationTemplateCreateRequestSchema()
        data = schema.load(request.get_json())
        
        template = notification_template_service.create_template(
            template_name=data['template_name'],
            template_type=data['template_type'],
            subject=data.get('subject'),
            content_template=data['content_template'],
            variables_schema=data.get('variables_schema'),
            is_active=data.get('is_active', False)
        )
        
        response_schema = NotificationTemplateResponseSchema()
        return success_response(response_schema.dump(template), 
                               "Notification template created successfully", 201)
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValidationException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('', methods=['GET'])
@require_role('Admin')
def get_all_templates():
    """
    Get all notification templates (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: include_inactive
        in: query
        required: false
        schema:
          type: boolean
          default: false
    responses:
      200:
        description: Templates retrieved successfully
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        templates = notification_template_service.get_all(include_inactive=include_inactive)
        
        response_schema = NotificationTemplateResponseSchema(many=True)
        return success_response({
            'count': len(templates),
            'templates': response_schema.dump(templates)
        })
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/<int:template_id>', methods=['GET'])
@require_role('Admin')
def get_template(template_id):
    """
    Get notification template by ID (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Template retrieved successfully
      404:
        description: Template not found
    """
    try:
        template = notification_template_service.get_by_id(template_id)
        response_schema = NotificationTemplateResponseSchema()
        return success_response(response_schema.dump(template))
    except NotFoundException as e:
        return not_found_response(str(e))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/type/<template_type>', methods=['GET'])
@require_role('Admin')
def get_templates_by_type(template_type):
    """
    Get notification templates by type (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_type
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Templates retrieved successfully
    """
    try:
        templates = notification_template_service.get_by_type(template_type)
        response_schema = NotificationTemplateResponseSchema(many=True)
        return success_response({
            'count': len(templates),
            'template_type': template_type,
            'templates': response_schema.dump(templates)
        })
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/type/<template_type>/active', methods=['GET'])
@require_role('Admin')
def get_active_template_by_type(template_type):
    """
    Get active notification template by type (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_type
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Active template retrieved successfully
      404:
        description: No active template found
    """
    try:
        template = notification_template_service.get_active_template_by_type(template_type)
        if not template:
            return not_found_response(f"No active template found for type: {template_type}")
        
        response_schema = NotificationTemplateResponseSchema()
        return success_response(response_schema.dump(template))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/<int:template_id>', methods=['PUT'])
@require_role('Admin')
def update_template(template_id):
    """
    Update notification template (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_id
        in: path
        required: true
        schema:
          type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            template_name:
              type: string
            subject:
              type: string
            content_template:
              type: string
            variables_schema:
              type: object
    responses:
      200:
        description: Template updated successfully
      404:
        description: Template not found
      400:
        description: Invalid input
    """
    try:
        schema = NotificationTemplateUpdateRequestSchema()
        data = schema.load(request.get_json())
        
        template = notification_template_service.update_template(
            template_id=template_id,
            template_name=data.get('template_name'),
            subject=data.get('subject'),
            content_template=data.get('content_template'),
            variables_schema=data.get('variables_schema')
        )
        
        response_schema = NotificationTemplateResponseSchema()
        return success_response(response_schema.dump(template), 
                               "Notification template updated successfully")
    except ValidationError as e:
        return validation_error_response(e.messages)
    except NotFoundException as e:
        return not_found_response(str(e))
    except ValidationException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/<int:template_id>/activate', methods=['PUT'])
def activate_template(template_id):
    """
    Activate notification template (FR-39)
    ---
    tags:
      - Notification Templates
    parameters:
      - name: template_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Template activated successfully
      404:
        description: Template not found
    """
    try:
        template = notification_template_service.activate_template(template_id)
        response_schema = NotificationTemplateResponseSchema()
        return success_response(response_schema.dump(template), 
                               "Notification template activated successfully")
    except NotFoundException as e:
        return not_found_response(str(e))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/<int:template_id>/deactivate', methods=['PUT'])
@require_role('Admin')
def deactivate_template(template_id):
    """
    Deactivate notification template (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Template deactivated successfully
      404:
        description: Template not found
    """
    try:
        template = notification_template_service.deactivate_template(template_id)
        response_schema = NotificationTemplateResponseSchema()
        return success_response(response_schema.dump(template), 
                               "Notification template deactivated successfully")
    except NotFoundException as e:
        return not_found_response(str(e))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/<int:template_id>', methods=['DELETE'])
@require_role('Admin')
def delete_template(template_id):
    """
    Delete notification template (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Template deleted successfully
      404:
        description: Template not found
    """
    try:
        notification_template_service.delete_template(template_id)
        return success_response(None, "Notification template deleted successfully")
    except NotFoundException as e:
        return not_found_response(str(e))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_template_bp.route('/<int:template_id>/render', methods=['POST'])
@require_role('Admin')
def render_template(template_id):
    """
    Render notification template with variables (FR-39)
    ---
    tags:
      - Notification Templates
    security:
      - Bearer: []
    parameters:
      - name: template_id
        in: path
        required: true
        schema:
          type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - variables
          properties:
            variables:
              type: object
              example: {"patient_name": "John Doe", "image_id": 123}
    responses:
      200:
        description: Template rendered successfully
      404:
        description: Template not found
      400:
        description: Invalid input or unresolved variables
    """
    try:
        schema = NotificationTemplateRenderRequestSchema()
        data = schema.load(request.get_json())
        
        rendered_content = notification_template_service.render_template(
            template_id=template_id,
            variables=data['variables']
        )
        
        return success_response({
            'template_id': template_id,
            'rendered_content': rendered_content
        }, "Template rendered successfully")
    except ValidationError as e:
        return validation_error_response(e.messages)
    except NotFoundException as e:
        return not_found_response(str(e))
    except ValidationException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)