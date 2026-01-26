from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.ai_annotation_repository import AiAnnotationRepository
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.databases.mssql import session
from services.ai_annotation_service import AiAnnotationService
from services.ai_analysis_service import AiAnalysisService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import AiAnnotationCreateRequestSchema, AiAnnotationUpdateRequestSchema, AiAnnotationResponseSchema

ai_annotation_bp = Blueprint('ai_annotation', __name__, url_prefix='/api/ai-annotations')

# Initialize repositories (only for service initialization)
annotation_repo = AiAnnotationRepository(session)
analysis_repo = AiAnalysisRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
annotation_service = AiAnnotationService(annotation_repo)
analysis_service = AiAnalysisService(analysis_repo)


@ai_annotation_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - AI Annotation
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "AI Annotation service is running")


@ai_annotation_bp.route('', methods=['POST'])
def create_annotation():
    """
    Create a new AI annotation
    ---
    tags:
      - AI Annotation
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
            - analysis_id
            - heatmap_url
          properties:
            analysis_id:
              type: integer
              example: 1
            heatmap_url:
              type: string
              example: "https://example.com/heatmap.jpg"
            description:
              type: string
              example: "Vascular abnormalities detected in upper quadrant"
    responses:
      201:
        description: Annotation created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Annotation created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        schema = AiAnnotationCreateRequestSchema()
        data = schema.load(request.get_json())
        
        analysis = analysis_service.get_analysis_by_id(data['analysis_id'])
        if not analysis:
            return not_found_response('Analysis not found')
        
        annotation = annotation_service.create_annotation(
            analysis_id=data['analysis_id'],
            heatmap_url=data['heatmap_url'],
            description=data.get('description')
        )
        
        response_schema = AiAnnotationResponseSchema()
        return success_response(response_schema.dump(annotation), 'Annotation created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/<int:annotation_id>', methods=['GET'])
def get_annotation(annotation_id):
    """
    Get annotation by ID
    ---
    tags:
      - AI Annotation
    parameters:
      - name: annotation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Annotation found
      404:
        description: Annotation not found
    """
    try:
        annotation = annotation_service.get_annotation_by_id(annotation_id)
        if not annotation:
            return not_found_response('Annotation not found')
        
        schema = AiAnnotationResponseSchema()
        return success_response(schema.dump(annotation))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_annotation_by_analysis(analysis_id):
    """
    Get annotation for a specific analysis
    ---
    tags:
      - AI Annotation
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Annotation found
      404:
        description: Annotation not found
    """
    try:
        annotation = annotation_service.get_annotation_by_analysis(analysis_id)
        if not annotation:
            return not_found_response('Annotation not found for this analysis')
        
        schema = AiAnnotationResponseSchema()
        return success_response(schema.dump(annotation))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('', methods=['GET'])
def get_all_annotations():
    """
    Get all annotations
    ---
    tags:
      - AI Annotation
    responses:
      200:
        description: List of all annotations
    """
    try:
        annotations = annotation_service.get_all_annotations()
        
        return success_response({
            'count': len(annotations),
            'annotations': [{
                'annotation_id': a.annotation_id,
                'analysis_id': a.analysis_id,
                'heatmap_url': a.heatmap_url,
                'description': a.description
            } for a in annotations]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/<int:annotation_id>', methods=['PUT'])
def update_annotation(annotation_id):
    """
    Update annotation
    ---
    tags:
      - AI Annotation
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: annotation_id
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
            heatmap_url:
              type: string
              example: "https://example.com/heatmap.jpg"
            description:
              type: string
              example: "Updated annotation description"
    responses:
      200:
        description: Annotation updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Annotation updated successfully
            data:
              type: object
      404:
        description: Annotation not found
    """
    try:
        data = request.get_json()
        
        annotation = annotation_service.update_annotation(annotation_id, **data)
        if not annotation:
            return not_found_response('Annotation not found')
        
        return success_response({
            'annotation_id': annotation.annotation_id,
            'heatmap_url': annotation.heatmap_url,
            'description': annotation.description
        }, 'Annotation updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/<int:annotation_id>/heatmap', methods=['PUT'])
def update_heatmap(annotation_id):
    """
    Update heatmap URL
    ---
    tags:
      - AI Annotation
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: annotation_id
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
            - heatmap_url
          properties:
            heatmap_url:
              type: string
              example: "https://example.com/heatmap.jpg"
    responses:
      200:
        description: Heatmap updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Heatmap updated successfully
            data:
              type: object
      400:
        description: Heatmap URL is required
      404:
        description: Annotation not found
    """
    try:
        data = request.get_json()
        if not data.get('heatmap_url'):
            return validation_error_response({'heatmap_url': 'Heatmap URL is required'})
        
        annotation = annotation_service.update_annotation_heatmap(annotation_id, data['heatmap_url'])
        if not annotation:
            return not_found_response('Annotation not found')
        
        return success_response({
            'annotation_id': annotation.annotation_id,
            'heatmap_url': annotation.heatmap_url
        }, 'Heatmap updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/<int:annotation_id>/description', methods=['PUT'])
def update_description(annotation_id):
    """
    Update annotation description
    ---
    tags:
      - AI Annotation
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: annotation_id
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
            - description
          properties:
            description:
              type: string
              example: "Updated annotation description"
    responses:
      200:
        description: Description updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Description updated successfully
            data:
              type: object
      400:
        description: Description is required
      404:
        description: Annotation not found
    """
    try:
        data = request.get_json()
        if not data.get('description'):
            return validation_error_response({'description': 'Description is required'})
        
        annotation = annotation_service.update_annotation_description(annotation_id, data['description'])
        if not annotation:
            return not_found_response('Annotation not found')
        
        return success_response({
            'annotation_id': annotation.annotation_id,
            'description': annotation.description
        }, 'Description updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/<int:annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id):
    """
    Delete annotation
    ---
    tags:
      - AI Annotation
    parameters:
      - name: annotation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Annotation deleted successfully
      404:
        description: Annotation not found
    """
    try:
        result = annotation_service.delete_annotation(annotation_id)
        if not result:
            return not_found_response('Annotation not found')
        
        return success_response(None, 'Annotation deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_annotation_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get annotation statistics
    ---
    tags:
      - AI Annotation
    responses:
      200:
        description: Annotation statistics
    """
    try:
        total = annotation_service.count_annotations_total()
        
        return success_response({
            'total_annotations': total
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

