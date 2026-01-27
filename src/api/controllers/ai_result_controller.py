from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.ai_result_repository import AiResultRepository
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.repositories.notification_repository import NotificationRepository
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.databases.mssql import session
from services.ai_result_service import AiResultService
from services.ai_analysis_service import AiAnalysisService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import AiResultCreateRequestSchema, AiResultUpdateRequestSchema, AiResultResponseSchema

ai_result_bp = Blueprint('ai_result', __name__, url_prefix='/api/ai-results')

# Initialize repositories
result_repo = AiResultRepository(session)
analysis_repo = AiAnalysisRepository(session)
notification_repo = NotificationRepository(session)
image_repo = RetinalImageRepository(session)

# Initialize SERVICES with dependency injection ✅
result_service = AiResultService(
    repository=result_repo,
    notification_repository=notification_repo,
    analysis_repository=analysis_repo,
    image_repository=image_repo
)
analysis_service = AiAnalysisService(analysis_repo)


@ai_result_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - AI Result
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "AI Result service is running")


@ai_result_bp.route('', methods=['POST'])
def create_result():
    """
    Create a new AI result
    ---
    tags:
      - AI Result
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
            - disease_type
            - risk_level
            - confidence_score
          properties:
            analysis_id:
              type: integer
              example: 1
            disease_type:
              type: string
              example: "diabetic_retinopathy"
            risk_level:
              type: string
              enum: [low, medium, high, critical]
              example: "high"
            confidence_score:
              type: number
              format: float
              example: 85.5
    responses:
      201:
        description: Result created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Result created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        schema = AiResultCreateRequestSchema()
        data = schema.load(request.get_json())
        
        analysis = analysis_service.get_analysis_by_id(data['analysis_id'])
        if not analysis:
            return not_found_response('Analysis not found')
        
        result = result_service.create_result(
            analysis_id=data['analysis_id'],
            disease_type=data['disease_type'],
            risk_level=data['risk_level'],
            confidence_score=float(data['confidence_score'])
        )
        
        response_schema = AiResultResponseSchema()
        return success_response(response_schema.dump(result), 'Result created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/<int:result_id>', methods=['GET'])
def get_result(result_id):
    """
    Get result by ID
    ---
    tags:
      - AI Result
    parameters:
      - name: result_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Result found
      404:
        description: Result not found
    """
    try:
        result = result_service.get_result_by_id(result_id)
        if not result:
            return not_found_response('Result not found')
        
        schema = AiResultResponseSchema()
        return success_response(schema.dump(result))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_results_by_analysis(analysis_id):
    """
    Get all results for an analysis
    ---
    tags:
      - AI Result
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
    responses:
      200:
        description: List of results for the analysis
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                analysis_id:
                  type: integer
                  example: 1
                count:
                  type: integer
                  example: 2
                results:
                  type: array
                  items:
                    type: object
                    properties:
                      result_id:
                        type: integer
                      analysis_id:
                        type: integer
                      disease_type:
                        type: string
                        example: diabetic_retinopathy
                      risk_level:
                        type: string
                        enum: [low, medium, high, critical]
                        example: high
                      confidence_score:
                        type: number
                        format: float
                        example: 85.5
                      detected_at:
                        type: string
                        format: date-time
      404:
        description: Analysis not found
    """
    try:
        results = result_service.get_results_by_analysis(analysis_id)
        
        # Serialize response with schema
        schema = AiResultResponseSchema(many=True)
        return success_response({
            'analysis_id': analysis_id,
            'count': len(results),
            'results': schema.dump(results)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/disease/<disease_type>', methods=['GET'])
def get_results_by_disease(disease_type):
    """
    Get results by disease type
    ---
    tags:
      - AI Result
    parameters:
      - name: disease_type
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of results
    """
    try:
        results = result_service.get_results_by_disease(disease_type)
        
        return success_response({
            'disease_type': disease_type,
            'count': len(results),
            'results': [{
                'result_id': r.result_id,
                'analysis_id': r.analysis_id,
                'risk_level': r.risk_level,
                'confidence_score': float(r.confidence_score)
            } for r in results]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/risk/<risk_level>', methods=['GET'])
def get_results_by_risk(risk_level):
    """
    Get results by risk level
    ---
    tags:
      - AI Result
    parameters:
      - name: risk_level
        in: path
        required: true
        schema:
          type: string
          enum: [low, medium, high]
    responses:
      200:
        description: List of results
    """
    try:
        results = result_service.get_results_by_risk_level(risk_level)
        
        return success_response({
            'risk_level': risk_level,
            'count': len(results),
            'results': [{
                'result_id': r.result_id,
                'analysis_id': r.analysis_id,
                'disease_type': r.disease_type,
                'confidence_score': float(r.confidence_score)
            } for r in results]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/high-confidence', methods=['GET'])
def get_high_confidence_results():
    """
    Get high confidence results
    ---
    tags:
      - AI Result
    parameters:
      - name: threshold
        in: query
        required: false
        schema:
          type: number
          default: 0.8
    responses:
      200:
        description: List of high confidence results
    """
    try:
        threshold = request.args.get('threshold', 0.8, type=float)
        # Filter by confidence threshold (need to add to service or filter here)
        all_results = result_service.list_all_results()
        results = [r for r in all_results if float(r.confidence_score) >= threshold]
        
        return success_response({
            'threshold': threshold,
            'count': len(results),
            'results': [{
                'result_id': r.result_id,
                'analysis_id': r.analysis_id,
                'disease_type': r.disease_type,
                'risk_level': r.risk_level,
                'confidence_score': float(r.confidence_score)
            } for r in results]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('', methods=['GET'])
def get_all_results():
    """
    Get all results
    ---
    tags:
      - AI Result
    responses:
      200:
        description: List of all results
    """
    try:
        results = result_service.list_all_results()
        
        return success_response({
            'count': len(results),
            'results': [{
                'result_id': r.result_id,
                'analysis_id': r.analysis_id,
                'disease_type': r.disease_type,
                'risk_level': r.risk_level
            } for r in results]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    """
    Update result
    ---
    tags:
      - AI Result
    parameters:
      - name: result_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: result_id
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
            disease_type:
              type: string
              example: "diabetic_retinopathy"
            risk_level:
              type: string
              example: "high"
            confidence_score:
              type: number
              format: float
              example: 0.95
    responses:
      200:
        description: Result updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Result updated successfully
            data:
              type: object
      404:
        description: Result not found
    """
    try:
        data = request.get_json()
        
        result = result_service.update_result(result_id, **data)
        if not result:
            return not_found_response('Result not found')
        
        return success_response({
            'result_id': result.result_id,
            'disease_type': result.disease_type,
            'risk_level': result.risk_level,
            'confidence_score': float(result.confidence_score)
        }, 'Result updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    """
    Delete result
    ---
    tags:
      - AI Result
    parameters:
      - name: result_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Result deleted successfully
      404:
        description: Result not found
    """
    try:
        success = result_service.delete_result(result_id)
        if not success:
            return not_found_response('Result not found')
        
        return success_response(None, 'Result deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_result_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get result statistics
    ---
    tags:
      - AI Result
    responses:
      200:
        description: Result statistics
    """
    try:
        # Use service method to get statistics
        stats = result_service.get_result_statistics()
        
        # Calculate average confidence
        all_results = result_service.list_all_results()
        avg_confidence = sum([float(r.confidence_score) for r in all_results]) / len(all_results) if all_results else 0
        
        # Add average confidence to stats
        stats['average_confidence'] = round(avg_confidence, 2)
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

