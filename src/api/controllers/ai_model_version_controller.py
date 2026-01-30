from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_roles, require_role
from infrastructure.repositories.ai_model_version_repository import AiModelVersionRepository
from infrastructure.databases.mssql import session
from services.ai_model_version_service import AiModelVersionService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import AiModelVersionCreateRequestSchema, AiModelVersionUpdateRequestSchema, AiModelVersionResponseSchema
from datetime import datetime

ai_model_version_bp = Blueprint('ai_model_version', __name__, url_prefix='/api/ai-model-versions')

# Initialize repository (only for service initialization)
model_repo = AiModelVersionRepository(session)

# Initialize SERVICE (Business Logic Layer) ✅
model_service = AiModelVersionService(model_repo)


@ai_model_version_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - AI Model Version
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "AI Model Version service is running")


@ai_model_version_bp.route('', methods=['POST'])
@require_role('Admin')
def create_model_version():
    """
    Create a new AI model version
    ---
    tags:
      - AI Model Version
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
            - model_name
            - version
            - threshold_config
          properties:
            model_name:
              type: string
              example: "Retinal Disease Detection"
            version:
              type: string
              example: "v2.0"
            threshold_config:
              type: string
              example: '{"confidence": 0.8}'
            trained_at:
              type: string
              format: date-time
              example: "2024-01-15T10:30:00"
            active_flag:
              type: boolean
              default: true
              example: true
    responses:
      201:
        description: Model version created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Model version created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        schema = AiModelVersionCreateRequestSchema()
        data = schema.load(request.get_json())
        
        model_version = model_service.create_model_version(
            model_name=data['model_name'],
            version=data['version'],
            threshold_config=data['threshold_config'],
            trained_at=datetime.now(),
            active_flag=data.get('active_flag', True)
        )
        
        response_schema = AiModelVersionResponseSchema()
        return success_response(response_schema.dump(model_version), 'Model version created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/<int:model_version_id>', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_model_version(model_version_id):
    """
    Get model version by ID
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_version_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Model version found
      404:
        description: Model version not found
    """
    try:
        model_version = model_service.get_model_by_id(model_version_id)
        if not model_version:
            return not_found_response('Model version not found')
        
        schema = AiModelVersionResponseSchema()
        return success_response(schema.dump(model_version))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/model/<model_name>', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_versions_by_name(model_name):
    """
    Get all versions of a model
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_name
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of model versions
    """
    try:
        versions = model_service.get_models_by_name(model_name)
        
        return success_response({
            'model_name': model_name,
            'count': len(versions),
            'versions': AiModelVersionResponseSchema(many=True).dump(versions)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/active', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_active_models():
    """
    Get all active AI model versions
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    responses:
      200:
        description: List of active models
    """
    try:
        models = model_service.get_active_models()
        
        return success_response({
            'count': len(models),
            'models': [{
                'ai_model_version_id': m.ai_model_version_id,
                'model_name': m.model_name,
                'version': m.version,
                'trained_at': m.trained_at.isoformat() if m.trained_at else None
            } for m in models]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/latest', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_latest_active():
    """
    Get latest active model version
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_name
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: Latest active model
      404:
        description: No active model found
    """
    try:
        model_name = request.args.get('model_name')
        model = model_service.get_latest_version_active(model_name)
        
        if not model:
            return not_found_response('No active model found')
        
        return success_response({
            'ai_model_version_id': model.ai_model_version_id,
            'model_name': model.model_name,
            'version': model.version,
            'threshold_config': model.threshold_config,
            'trained_at': model.trained_at.isoformat() if model.trained_at else None,
            'active_flag': model.active_flag
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('', methods=['GET'])
def get_all_models():
    """
    Get all AI model versions
    ---
    tags:
      - AI Model Version
    responses:
      200:
        description: List of all model versions
    """
    try:
        models = model_service.get_all_models()
        
        return success_response({
            'count': len(models),
            'models': [{
                'ai_model_version_id': m.ai_model_version_id,
                'model_name': m.model_name,
                'version': m.version,
                'active_flag': m.active_flag
            } for m in models]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/<int:model_version_id>/activate', methods=['PUT'])
@require_role('Admin')
def activate_model(model_version_id):
    """
    Activate model version
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_version_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Model activated
      404:
        description: Model not found
    """
    try:
        model = model_service.activate_model(model_version_id)
        if not model:
            return not_found_response('Model version not found')
        
        return success_response({
            'ai_model_version_id': model.ai_model_version_id,
            'active_flag': model.active_flag
        }, 'Model activated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/<int:model_version_id>/deactivate', methods=['PUT'])
@require_role('Admin')
def deactivate_model(model_version_id):
    """
    Deactivate model version
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_version_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Model deactivated
      404:
        description: Model not found
    """
    try:
        model = model_service.deactivate_model(model_version_id)
        if not model:
            return not_found_response('Model version not found')
        
        return success_response({
            'ai_model_version_id': model.ai_model_version_id,
            'active_flag': model.active_flag
        }, 'Model deactivated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/<int:model_version_id>/threshold', methods=['PUT'])
@require_role('Admin')
def update_threshold(model_version_id):
    """
    Update threshold configuration
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_version_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: model_version_id
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
            - threshold_config
          properties:
            threshold_config:
              type: string
              example: '{"confidence": 0.85}'
    responses:
      200:
        description: Threshold updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Threshold updated successfully
            data:
              type: object
      400:
        description: Threshold config is required
      404:
        description: Model not found
    """
    try:
        data = request.get_json()
        if not data.get('threshold_config'):
            return validation_error_response({'threshold_config': 'Threshold config is required'})
        
        model = model_service.update_model_threshold_config(model_version_id, data['threshold_config'])
        if not model:
            return not_found_response('Model version not found')
        
        return success_response({
            'ai_model_version_id': model.ai_model_version_id,
            'threshold_config': model.threshold_config
        }, 'Threshold updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/<int:model_version_id>', methods=['DELETE'])
@require_role('Admin')
def delete_model(model_version_id):
    """
    Delete model version
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    parameters:
      - name: model_version_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Model deleted successfully
      404:
        description: Model not found
    """
    try:
        result = model_service.delete_model(model_version_id)
        if not result:
            return not_found_response('Model version not found')
        
        return success_response(None, 'Model version deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_model_version_bp.route('/stats', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_stats():
    """
    Get model version statistics
    ---
    tags:
      - AI Model Version
    security:
      - Bearer: []
    responses:
      200:
        description: Model statistics
    """
    try:
        total = model_service.count_models_total()
        active = model_service.count_models_active()
        
        return success_response({
            'total_models': total,
            'active_models': active,
            'inactive_models': total - active
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

