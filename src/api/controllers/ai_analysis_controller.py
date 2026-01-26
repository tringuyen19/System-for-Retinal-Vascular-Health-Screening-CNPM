from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.databases.mssql import session
from services.ai_analysis_service import AiAnalysisService
from services.retinal_image_service import RetinalImageService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import AiAnalysisCreateRequestSchema, AiAnalysisUpdateRequestSchema, AiAnalysisResponseSchema
from domain.exceptions import NotFoundException, ValidationException

ai_analysis_bp = Blueprint('ai_analysis', __name__, url_prefix='/api/ai-analysis')

# Initialize repositories (only for service initialization)
analysis_repo = AiAnalysisRepository(session)
image_repo = RetinalImageRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
analysis_service = AiAnalysisService(analysis_repo)
image_service = RetinalImageService(image_repo)


@ai_analysis_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - AI Analysis
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "AI Analysis service is running")


@ai_analysis_bp.route('', methods=['POST'])
def create_analysis():
    """
    Create a new AI analysis request
    ---
    tags:
      - AI Analysis
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
            - image_id
            - ai_model_version_id
          properties:
            image_id:
              type: integer
              example: 1
            ai_model_version_id:
              type: integer
              example: 1
            status:
              type: string
              enum: [pending, processing, completed, failed]
              example: "pending"
              default: pending
            processing_time:
              type: integer
              example: 12
              description: Processing time in seconds (optional)
    responses:
      201:
        description: Analysis created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Analysis created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # Validate request data with schema
        schema = AiAnalysisCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # Check if image exists (via SERVICE) ✅
        image = image_service.get_image_by_id(data['image_id'])
        if not image:
            return not_found_response('Image not found')
        
        # Create analysis
        analysis = analysis_service.create_analysis(
            image_id=data['image_id'],
            ai_model_version_id=data['ai_model_version_id'],
            status=data.get('status', 'pending'),
            processing_time=data.get('processing_time')
        )
        
        # Serialize response with schema
        response_schema = AiAnalysisResponseSchema()
        return success_response(response_schema.dump(analysis), 'Analysis created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValidationException as e:
        return error_response(str(e), 400)
    except NotFoundException as e:
        return error_response(str(e), 404)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/<int:analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """
    Get AI analysis by ID
    ---
    tags:
      - AI Analysis
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Analysis found
      404:
        description: Analysis not found
    """
    try:
        analysis = analysis_service.get_analysis_by_id(analysis_id)
        if not analysis:
            return not_found_response('Analysis not found')
        
        # Serialize response with schema
        schema = AiAnalysisResponseSchema()
        return success_response(schema.dump(analysis))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_patient_analyses(patient_id):
    """
    Get analysis history for a patient with pagination (FR-17)
    ---
    tags:
      - AI Analysis
    parameters:
      - name: patient_id
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
        description: Maximum number of results
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
        description: Number of results to skip
      - name: start_date
        in: query
        required: false
        schema:
          type: string
          format: date
        description: Start date filter (YYYY-MM-DD)
      - name: end_date
        in: query
        required: false
        schema:
          type: string
          format: date
        description: End date filter (YYYY-MM-DD)
    responses:
      200:
        description: List of analyses for patient
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                patient_id:
                  type: integer
                  example: 1
                count:
                  type: integer
                  example: 2
                analyses:
                  type: array
                  items:
                    type: object
                    properties:
                      analysis_id:
                        type: integer
                      image_id:
                        type: integer
                      ai_model_version_id:
                        type: integer
                      analysis_time:
                        type: string
                        format: date-time
                      processing_time:
                        type: integer
                        description: Processing time in seconds
                      status:
                        type: string
                        enum: [pending, processing, completed, failed]
    """
    try:
        limit = request.args.get('limit', type=int, default=50)
        offset = request.args.get('offset', type=int, default=0)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        from datetime import date as date_type
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = date_type.fromisoformat(start_date_str)
            except ValueError:
                return error_response('Invalid start_date format. Use YYYY-MM-DD', 400)
        
        if end_date_str:
            try:
                end_date = date_type.fromisoformat(end_date_str)
            except ValueError:
                return error_response('Invalid end_date format. Use YYYY-MM-DD', 400)
        
        # Call SERVICE ✅
        analyses = analysis_service.get_patient_history(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        
        schema = AiAnalysisResponseSchema(many=True)
        return success_response({
            'patient_id': patient_id,
            'count': len(analyses),
            'analyses': schema.dump(analyses)
        })
        
    except ValidationException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/image/<int:image_id>', methods=['GET'])
def get_analysis_by_image(image_id):
    """
    Get AI analysis for a specific image
    ---
    tags:
      - AI Analysis
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Analysis found
      404:
        description: Analysis not found
    """
    try:
        analysis = analysis_service.get_analysis_by_image(image_id)
        if not analysis:
            return not_found_response('Analysis not found for this image')
        
        # Serialize response with schema
        schema = AiAnalysisResponseSchema()
        return success_response(schema.dump(analysis))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/status/<status>', methods=['GET'])
def get_analyses_by_status(status):
    """
    Get analyses by status
    ---
    tags:
      - AI Analysis
    parameters:
      - name: status
        in: path
        required: true
        schema:
          type: string
          enum: [pending, processing, completed, failed]
    responses:
      200:
        description: List of analyses
    """
    try:
        analyses = analysis_service.get_analyses_by_status(status)
        
        return success_response({
            'status': status,
            'count': len(analyses),
            'analyses': [{
                'analysis_id': a.analysis_id,
                'image_id': a.image_id,
                'ai_model_version_id': a.ai_model_version_id,
                'analysis_time': a.analysis_time.isoformat() if a.analysis_time else None
            } for a in analyses]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/pending', methods=['GET'])
def get_pending_analyses():
    """
    Get pending analyses
    ---
    tags:
      - AI Analysis
    responses:
      200:
        description: List of pending analyses
    """
    try:
        analyses = analysis_service.get_pending_analyses()
        
        return success_response({
            'count': len(analyses),
            'analyses': [{
                'analysis_id': a.analysis_id,
                'image_id': a.image_id,
                'ai_model_version_id': a.ai_model_version_id,
                'analysis_time': a.analysis_time.isoformat() if a.analysis_time else None
            } for a in analyses]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/processing', methods=['GET'])
def get_processing_analyses():
    """
    Get analyses currently processing
    ---
    tags:
      - AI Analysis
    responses:
      200:
        description: List of processing analyses
    """
    try:
        analyses = analysis_service.get_processing_analyses()
        
        return success_response({
            'count': len(analyses),
            'analyses': [{
                'analysis_id': a.analysis_id,
                'image_id': a.image_id,
                'ai_model_version_id': a.ai_model_version_id,
                'analysis_time': a.analysis_time.isoformat() if a.analysis_time else None
            } for a in analyses]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/completed', methods=['GET'])
def get_completed_analyses():
    """
    Get completed analyses
    ---
    tags:
      - AI Analysis
    responses:
      200:
        description: List of completed analyses
    """
    try:
        analyses = analysis_service.get_completed_analyses()
        
        return success_response({
            'count': len(analyses),
            'analyses': [{
                'analysis_id': a.analysis_id,
                'image_id': a.image_id,
                'ai_model_version_id': a.ai_model_version_id,
                'processing_time': a.processing_time,
                'analysis_time': a.analysis_time.isoformat() if a.analysis_time else None
            } for a in analyses]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/<int:analysis_id>/processing', methods=['PUT'])
def mark_as_processing(analysis_id):
    """
    Mark analysis as processing
    ---
    tags:
      - AI Analysis
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Analysis marked as processing
      404:
        description: Analysis not found
    """
    try:
        analysis = analysis_service.mark_as_processing(analysis_id)
        if not analysis:
            return not_found_response('Analysis not found')
        
        return success_response({
            'analysis_id': analysis.analysis_id,
            'status': analysis.status
        }, 'Analysis marked as processing')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/<int:analysis_id>/complete', methods=['PUT'])
def mark_as_completed(analysis_id):
    """
    Mark analysis as completed
    ---
    tags:
      - AI Analysis
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: analysis_id
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
            processing_time:
              type: integer
              description: Processing time in seconds
              example: 12
    responses:
      200:
        description: Analysis marked as completed
        schema:
          type: object
          properties:
            message:
              type: string
              example: Analysis marked as completed
            data:
              type: object
      404:
        description: Analysis not found
    """
    try:
        data = request.get_json() or {}
        processing_time = data.get('processing_time')
        
        analysis = analysis_service.mark_as_completed(analysis_id, processing_time)
        if not analysis:
            return not_found_response('Analysis not found')
        
        return success_response({
            'analysis_id': analysis.analysis_id,
            'status': analysis.status,
            'processing_time': analysis.processing_time,
            'analysis_time': analysis.analysis_time.isoformat() if analysis.analysis_time else None
        }, 'Analysis completed successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/<int:analysis_id>/fail', methods=['PUT'])
def mark_as_failed(analysis_id):
    """
    Mark analysis as failed
    ---
    tags:
      - AI Analysis
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Analysis marked as failed
      404:
        description: Analysis not found
    """
    try:
        analysis = analysis_service.mark_as_failed(analysis_id)
        if not analysis:
            return not_found_response('Analysis not found')
        
        return success_response({
            'analysis_id': analysis.analysis_id,
            'status': analysis.status
        }, 'Analysis marked as failed')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/<int:analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    """
    Delete AI analysis
    ---
    tags:
      - AI Analysis
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Analysis deleted successfully
      404:
        description: Analysis not found
    """
    try:
        result = analysis_service.delete_analysis(analysis_id)
        if not result:
            return not_found_response('Analysis not found')
        
        return success_response(None, 'Analysis deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get AI analysis statistics
    ---
    tags:
      - AI Analysis
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
          enum: [pending, processing, completed, failed]
        description: Optional status filter. If provided, returns count for that status only. If omitted, returns full statistics.
        example: pending
    responses:
      200:
        description: Analysis statistics
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              description: If status parameter provided, returns {status, count}. Otherwise returns full statistics {total_analyses, pending, processing, completed, failed, avg_processing_time}
    """
    try:
        status = request.args.get('status')
        
        if status:
            count = analysis_service.count_by_status(status)
            return success_response({
                'status': status,
                'count': count
            })
        else:
            stats = analysis_service.get_analysis_statistics()
            
            return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/failed', methods=['GET'])
def get_failed_analyses():
    """
    Get failed analyses
    ---
    tags:
      - AI Analysis
    responses:
      200:
        description: List of failed analyses
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                count:
                  type: integer
                  example: 2
                analyses:
                  type: array
                  items:
                    type: object
    """
    try:
        analyses = analysis_service.get_analyses_by_status('failed')
        
        return success_response({
            'count': len(analyses),
            'analyses': [{
                'analysis_id': a.analysis_id,
                'image_id': a.image_id,
                'ai_model_version_id': a.ai_model_version_id,
                'analysis_time': a.analysis_time.isoformat() if a.analysis_time else None,
                'status': a.status
            } for a in analyses]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@ai_analysis_bp.route('/patient/<int:patient_id>/trend', methods=['GET'])
def get_patient_trend(patient_id):
    """
    Get trend data for a patient over time (FR-17)
    ---
    tags:
      - AI Analysis
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
      - name: days
        in: query
        required: false
        schema:
          type: integer
          default: 90
        description: Number of days to look back
    responses:
      200:
        description: Patient trend data
        schema:
          type: object
          properties:
            message:
              type: string
              example: Trend data retrieved successfully
            data:
              type: object
              properties:
                patient_id:
                  type: integer
                  example: 1
                period_days:
                  type: integer
                  example: 90
                total_analyses:
                  type: integer
                  example: 5
                risk_distribution:
                  type: object
                  additionalProperties:
                    type: integer
                  example:
                    low: 2
                    medium: 2
                    high: 1
                average_confidence:
                  type: number
                  format: float
                  example: 85.5
                analysis_dates:
                  type: array
                  items:
                    type: string
                    format: date
                  example: ["2026-01-10", "2026-01-08"]
                risk_levels:
                  type: array
                  items:
                    type: string
                    enum: [low, medium, high, critical]
                  example: ["low", "medium", "high"]
                confidence_scores:
                  type: array
                  items:
                    type: number
                    format: float
                  example: [85.5, 90.2, 75.8]
                trend:
                  type: string
                  enum: [improving, worsening, stable, no_data]
                  example: stable
    """
    try:
        days = request.args.get('days', type=int, default=90)
        
        # Call SERVICE ✅
        trend_data = analysis_service.get_patient_trend_data(patient_id, days)
        
        return success_response(trend_data, 'Trend data retrieved successfully')
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

