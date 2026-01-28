"""
Admin Controller - API endpoints for admin operations
Phase 4: Admin Requirements (FR-31 to FR-39)
"""

from flask import Blueprint, request
from marshmallow import ValidationError
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.clinic_repository import ClinicRepository
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.doctor_profile_repository import DoctorProfileRepository
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.repositories.ai_result_repository import AiResultRepository
from infrastructure.repositories.payment_repository import PaymentRepository
from infrastructure.repositories.subscription_repository import SubscriptionRepository
from infrastructure.repositories.ai_model_version_repository import AiModelVersionRepository
from infrastructure.databases.mssql import session
from services.admin_service import AdminService
from api.responses import success_response, error_response, validation_error_response
from api.schemas import AdminDashboardResponseSchema, AdminAnalyticsResponseSchema, AiConfigurationUpdateRequestSchema

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize repositories
account_repo = AccountRepository(session)
clinic_repo = ClinicRepository(session)
patient_repo = PatientProfileRepository(session)
doctor_repo = DoctorProfileRepository(session)
image_repo = RetinalImageRepository(session)
analysis_repo = AiAnalysisRepository(session)
result_repo = AiResultRepository(session)
payment_repo = PaymentRepository(session)
subscription_repo = SubscriptionRepository(session)
model_version_repo = AiModelVersionRepository(session)

# Initialize SERVICE (Business Logic Layer) ✅
admin_service = AdminService(
    account_repository=account_repo,
    clinic_repository=clinic_repo,
    patient_repository=patient_repo,
    doctor_repository=doctor_repo,
    image_repository=image_repo,
    analysis_repository=analysis_repo,
    result_repository=result_repo,
    payment_repository=payment_repo,
    subscription_repository=subscription_repo,
    model_version_repository=model_version_repo
)


@admin_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Admin
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Admin service is running")


# ========== FR-35: Global Dashboard ==========

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """
    Get global dashboard summary (FR-35)
    Shows usage, revenue, and AI performance metrics
    ---
    tags:
      - Admin
    responses:
      200:
        description: Dashboard summary retrieved successfully
        schema:
          type: object
          properties:
            message:
              type: string
            data:
              type: object
              properties:
                users:
                  type: object
                  properties:
                    total_users:
                      type: integer
                    total_doctors:
                      type: integer
                    total_clinics:
                      type: integer
                usage:
                  type: object
                  properties:
                    total_images:
                      type: integer
                    total_analyses:
                      type: integer
                    completed_analyses:
                      type: integer
                    success_rate:
                      type: number
                revenue:
                  type: object
                  properties:
                    total_revenue:
                      type: number
                    total_payments:
                      type: integer
                ai_performance:
                  type: object
                  properties:
                    average_confidence:
                      type: number
                    risk_distribution:
                      type: object
                    active_model:
                      type: object
    """
    try:
        dashboard_data = admin_service.get_dashboard_summary()
        return success_response(dashboard_data, "Dashboard summary retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ========== FR-36: System Analytics ==========

@admin_bp.route('/analytics/images', methods=['GET'])
def get_image_analytics():
    """
    Get image analytics (FR-36)
    ---
    tags:
      - Admin
    parameters:
      - name: days
        in: query
        required: false
        schema:
          type: integer
          default: 30
        description: Number of days to look back
    responses:
      200:
        description: Image analytics retrieved successfully
    """
    try:
        days = request.args.get('days', 30, type=int)
        analytics = admin_service.get_image_analytics(days=days)
        return success_response(analytics, "Image analytics retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/analytics/risk-distribution', methods=['GET'])
def get_risk_distribution_analytics():
    """
    Get risk distribution analytics (FR-36)
    ---
    tags:
      - Admin
    responses:
      200:
        description: Risk distribution analytics retrieved successfully
    """
    try:
        analytics = admin_service.get_risk_distribution_analytics()
        return success_response(analytics, "Risk distribution analytics retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/analytics/revenue', methods=['GET'])
def get_revenue_analytics():
    """
    Get revenue analytics (FR-36)
    ---
    tags:
      - Admin
    parameters:
      - name: days
        in: query
        required: false
        schema:
          type: integer
          default: 30
        description: Number of days to look back (omit or set to 0 for all time)
    responses:
      200:
        description: Revenue analytics retrieved successfully
    """
    try:
        days_param = request.args.get('days', '30')
        # Allow 'all' or 0 to get all-time data
        if days_param in ['all', '0', '']:
            days = None
        else:
            days = int(days_param) if days_param else 30
        
        analytics = admin_service.get_revenue_analytics(days=days)
        return success_response(analytics, "Revenue analytics retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/analytics/error-rates', methods=['GET'])
def get_error_rate_analytics():
    """
    Get error rate analytics (FR-36)
    ---
    tags:
      - Admin
    responses:
      200:
        description: Error rate analytics retrieved successfully
    """
    try:
        analytics = admin_service.get_error_rate_analytics()
        return success_response(analytics, "Error rate analytics retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ========== FR-33: AI Configuration ==========

@admin_bp.route('/ai-config', methods=['GET'])
def get_ai_configuration():
    """
    Get AI configuration (FR-33)
    Returns: model versions, thresholds, and retraining policies
    ---
    tags:
      - Admin
    responses:
      200:
        description: AI configuration retrieved successfully
    """
    try:
        config = admin_service.get_ai_configuration()
        return success_response(config, "AI configuration retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-config', methods=['PUT'])
def update_ai_configuration():
    """
    Update AI configuration (FR-33)
    Updates thresholds and retraining policies
    ---
    tags:
      - Admin
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            threshold_config:
              type: string
              description: JSON string with threshold configuration
            retraining_policy:
              type: object
              description: Retraining policy settings
    responses:
      200:
        description: AI configuration updated successfully
      400:
        description: Invalid request
      404:
        description: No active AI model found
    """
    try:
        from domain.exceptions import NotFoundException
        
        # Validate request
        schema = AiConfigurationUpdateRequestSchema()
        data = schema.load(request.get_json() or {})
        
        threshold_config = data.get('threshold_config')
        retraining_policy = data.get('retraining_policy')
        
        updated_config = admin_service.update_ai_configuration(
            threshold_config=threshold_config,
            retraining_policy=retraining_policy
        )
        
        return success_response(updated_config, "AI configuration updated successfully")
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except NotFoundException as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)