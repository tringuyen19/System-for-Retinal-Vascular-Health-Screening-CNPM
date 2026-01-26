from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.doctor_review_repository import DoctorReviewRepository
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.repositories.doctor_profile_repository import DoctorProfileRepository
from infrastructure.databases.mssql import session
from services.doctor_review_service import DoctorReviewService
from services.ai_analysis_service import AiAnalysisService
from services.doctor_profile_service import DoctorProfileService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import DoctorReviewCreateRequestSchema, DoctorReviewUpdateRequestSchema, DoctorReviewResponseSchema
from domain.exceptions import NotFoundException, ValidationException

doctor_review_bp = Blueprint('doctor_review', __name__, url_prefix='/api/doctor-reviews')

# Initialize repositories (only for service initialization)
review_repo = DoctorReviewRepository(session)
analysis_repo = AiAnalysisRepository(session)
doctor_repo = DoctorProfileRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
review_service = DoctorReviewService(review_repo)
analysis_service = AiAnalysisService(analysis_repo)
doctor_service = DoctorProfileService(doctor_repo)


@doctor_review_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Doctor Review
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Doctor review service is running")


@doctor_review_bp.route('', methods=['POST'])
def create_review():
    """
    Create a new doctor review for AI analysis
    ---
    tags:
      - Doctor Review
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
            - doctor_id
            - validation_status
          properties:
            analysis_id:
              type: integer
              example: 1
            doctor_id:
              type: integer
              example: 2
            validation_status:
              type: string
              enum: [approved, rejected, needs_revision, pending]
              example: "approved"
            comment:
              type: string
              example: "AI diagnosis is accurate. Patient should follow up in 3 months."
    responses:
      201:
        description: Review created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Review created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        schema = DoctorReviewCreateRequestSchema()
        data = schema.load(request.get_json())
        
        analysis = analysis_service.get_analysis_by_id(data['analysis_id'])
        if not analysis:
            return not_found_response('Analysis not found')
        
        doctor = doctor_service.get_doctor_by_id(data['doctor_id'])
        if not doctor:
            return not_found_response('Doctor not found')
        
        review = review_service.create_review(
            analysis_id=data['analysis_id'],
            doctor_id=data['doctor_id'],
            validation_status=data['validation_status'],
            comment=data.get('comment')
        )
        
        response_schema = DoctorReviewResponseSchema()
        return success_response(response_schema.dump(review), 'Review created successfully', 201)
        
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


@doctor_review_bp.route('/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """
    Get review by ID
    ---
    tags:
      - Doctor Review
    parameters:
      - name: review_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Review found
      404:
        description: Review not found
    """
    try:
        review = review_service.get_review_by_id(review_id)
        if not review:
            return not_found_response('Review not found')
        
        schema = DoctorReviewResponseSchema()
        return success_response(schema.dump(review))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
def get_review_by_analysis(analysis_id):
    """
    Get review for a specific analysis
    ---
    tags:
      - Doctor Review
    parameters:
      - name: analysis_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Review found
      404:
        description: Review not found
    """
    try:
        review = review_service.get_review_by_analysis(analysis_id)
        if not review:
            return not_found_response('Review not found for this analysis')
        
        schema = DoctorReviewResponseSchema()
        return success_response(schema.dump(review))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_reviews_by_doctor(doctor_id):
    """
    Get all reviews by a doctor
    ---
    tags:
      - Doctor Review
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of reviews
    """
    try:
        reviews = review_service.get_reviews_by_doctor(doctor_id)
        
        return success_response({
            'doctor_id': doctor_id,
            'count': len(reviews),
            'reviews': [{
                'review_id': r.review_id,
                'analysis_id': r.analysis_id,
                'validation_status': r.validation_status,
                'reviewed_at': r.reviewed_at.isoformat() if r.reviewed_at else None
            } for r in reviews]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/status/<status>', methods=['GET'])
def get_reviews_by_status(status):
    """
    Get reviews by validation status
    ---
    tags:
      - Doctor Review
    parameters:
      - name: status
        in: path
        required: true
        schema:
          type: string
          enum: [approved, rejected, needs_revision]
    responses:
      200:
        description: List of reviews
    """
    try:
        reviews = review_service.get_reviews_by_status(status)
        
        return success_response({
            'status': status,
            'count': len(reviews),
            'reviews': [{
                'review_id': r.review_id,
                'analysis_id': r.analysis_id,
                'doctor_id': r.doctor_id,
                'reviewed_at': r.reviewed_at.isoformat() if r.reviewed_at else None
            } for r in reviews]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/pending', methods=['GET'])
def get_pending_reviews():
    """
    Get pending reviews (analyses without review)
    ---
    tags:
      - Doctor Review
    responses:
      200:
        description: List of analyses pending review
    """
    try:
        pending = review_service.get_pending_reviews()
        
        return success_response({
            'count': len(pending),
            'pending_analyses': [{
                'analysis_id': a.analysis_id,
                'image_id': a.image_id,
                'status': a.status,
                'completed_at': a.completed_at.isoformat() if a.completed_at else None
            } for a in pending]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/<int:review_id>/approve', methods=['PUT'])
def approve_review(review_id):
    """
    Approve AI analysis result
    ---
    tags:
      - Doctor Review
    parameters:
      - name: review_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Review approved
      404:
        description: Review not found
    """
    try:
        review = review_service.approve_review(review_id)
        if not review:
            return not_found_response('Review not found')
        
        return success_response({
            'review_id': review.review_id,
            'validation_status': review.validation_status
        }, 'Review approved successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/<int:review_id>/reject', methods=['PUT'])
def reject_review(review_id):
    """
    Reject AI analysis result
    ---
    tags:
      - Doctor Review
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: review_id
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
            - comment
          properties:
            comment:
              type: string
              example: "AI diagnosis needs revision. Please review the retinal image again."
    responses:
      200:
        description: Review rejected
        schema:
          type: object
          properties:
            message:
              type: string
              example: Review rejected
            data:
              type: object
      400:
        description: Comment is required
      404:
        description: Review not found
    """
    try:
        data = request.get_json()
        if not data.get('comment'):
            return validation_error_response({'comment': 'Comment is required for rejection'})
        
        review = review_service.reject_review(review_id, data['comment'])
        if not review:
            return not_found_response('Review not found')
        
        return success_response({
            'review_id': review.review_id,
            'validation_status': review.validation_status,
            'comment': review.comment
        }, 'Review rejected')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/<int:review_id>/comment', methods=['PUT'])
def update_comment(review_id):
    """
    Update review comment
    ---
    tags:
      - Doctor Review
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: review_id
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
            - comment
          properties:
            comment:
              type: string
              example: "Updated comment: Patient should follow up in 2 months."
    responses:
      200:
        description: Comment updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Comment updated successfully
            data:
              type: object
      400:
        description: Comment is required
      404:
        description: Review not found
    """
    try:
        data = request.get_json()
        if not data.get('comment'):
            return validation_error_response({'comment': 'Comment is required'})
        
        review = review_service.update_review(review_id, comment=data['comment'])
        if not review:
            return not_found_response('Review not found')
        
        return success_response({
            'review_id': review.review_id,
            'comment': review.comment
        }, 'Comment updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Delete review
    ---
    tags:
      - Doctor Review
    parameters:
      - name: review_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Review deleted successfully
      404:
        description: Review not found
    """
    try:
        result = review_service.delete_review(review_id)
        if not result:
            return not_found_response('Review not found')
        
        return success_response(None, 'Review deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get review statistics
    ---
    tags:
      - Doctor Review
    parameters:
      - name: doctor_id
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
        description: Review statistics
    """
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        status = request.args.get('status')
        
        if doctor_id:
            count = review_service.count_by_doctor(doctor_id)
            return success_response({
                'doctor_id': doctor_id,
                'total_reviews': count
            })
        elif status:
            count = review_service.count_by_status(status)
            return success_response({
                'status': status,
                'count': count
            })
        else:
            stats = review_service.get_review_statistics()
            total = stats.get('total_reviews', 0)
            approved = stats.get('approved', 0)
            rejected = stats.get('rejected', 0)
            needs_revision = stats.get('needs_revision', 0)
            return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_review_bp.route('/feedback/aggregation', methods=['GET'])
def get_feedback_aggregation():
    """
    Get aggregated feedback for AI improvement (FR-19)
    ---
    tags:
      - Doctor Review
    parameters:
      - name: doctor_id
        in: query
        required: false
        schema:
          type: integer
        description: Filter by doctor ID (optional)
    responses:
      200:
        description: Aggregated feedback statistics
        schema:
          type: object
          properties:
            total_feedback_items:
              type: integer
            validation_status_distribution:
              type: object
            estimated_ai_accuracy:
              type: number
            needs_improvement_count:
              type: integer
            improvement_rate:
              type: number
            feedback_summary:
              type: object
    """
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        
        # Call SERVICE ✅
        feedback = review_service.get_feedback_aggregation(doctor_id=doctor_id)
        
        return success_response(feedback, 'Feedback aggregation retrieved successfully')
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

