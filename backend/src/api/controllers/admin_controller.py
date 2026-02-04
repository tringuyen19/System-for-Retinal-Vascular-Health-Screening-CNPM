"""
Admin Controller - API endpoints for admin operations
Phase 4: Admin Requirements (FR-31 to FR-39)
"""

from flask import Blueprint, request
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_role
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
from infrastructure.repositories.permission_repository import PermissionRepository
from infrastructure.repositories.role_repository import RoleRepository
from infrastructure.repositories.ai_config_repository import AiConfigRepository
from infrastructure.databases.mssql import session
from services.admin_service import AdminService
from services.role_service import RoleService
from api.responses import success_response, error_response, validation_error_response
from api.schemas import (
    AdminDashboardResponseSchema, 
    AdminAnalyticsResponseSchema, 
    AiConfigurationUpdateRequestSchema,
    PrivacySettingsUpdateRequestSchema,
    PrivacySettingsResponseSchema,
    CommunicationPolicyUpdateRequestSchema,
    CommunicationPoliciesResponseSchema
)

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
permission_repo = PermissionRepository(session)
role_repo = RoleRepository(session)
ai_config_repo = AiConfigRepository(session)

# Initialize RoleService (needed for AdminService)
role_service = RoleService(role_repo, permission_repo)

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
    model_version_repository=model_version_repo,
    permission_repository=permission_repo,
    role_service=role_service,
    ai_config_repository=ai_config_repo
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
@require_role('Admin')
def get_dashboard():
    """
    Get global dashboard summary (FR-35)
    Shows usage, revenue, and AI performance metrics
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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
@require_role('Admin')
def get_image_analytics():
    """
    Get image analytics (FR-36)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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
@require_role('Admin')
def get_risk_distribution_analytics():
    """
    Get risk distribution analytics (FR-36)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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
@require_role('Admin')
def get_revenue_analytics():
    """
    Get revenue analytics (FR-36)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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
@require_role('Admin')
def get_error_rate_analytics():
    """
    Get error rate analytics (FR-36)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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
@require_role('Admin')
def get_ai_configuration():
    """
    Get AI configuration (FR-33)
    Returns: model versions, thresholds, and retraining policies
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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
@require_role('Admin')
def update_ai_configuration():
    """
    Update AI configuration (FR-33)
    Updates thresholds and retraining policies
    ---
    tags:
      - Admin
    security:
      - Bearer: []
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


# ========== FR-37: Privacy Settings Management ==========

@admin_bp.route('/privacy-settings', methods=['GET'])
@require_role('Admin')
def get_privacy_settings():
    """
    Get privacy settings (FR-37)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Privacy settings retrieved successfully
    """
    try:
        settings = admin_service.get_privacy_settings()
        schema = PrivacySettingsResponseSchema()
        return success_response(schema.dump(settings), "Privacy settings retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/privacy-settings', methods=['PUT'])
@require_role('Admin')
def update_privacy_settings():
    """
    Update privacy settings (FR-37)
    ---
    tags:
      - Admin
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
          properties:
            data_retention_days:
              type: integer
              example: 365
            auto_anonymize_after_days:
              type: integer
              example: 730
            require_consent_for_ai_training:
              type: boolean
            allow_data_sharing:
              type: boolean
            anonymize_patient_data:
              type: boolean
            encrypt_sensitive_data:
              type: boolean
            audit_data_access:
              type: boolean
            gdpr_compliance_mode:
              type: boolean
    responses:
      200:
        description: Privacy settings updated successfully
      400:
        description: Invalid input
    """
    try:
        schema = PrivacySettingsUpdateRequestSchema()
        data = schema.load(request.get_json())
        
        updated_settings = admin_service.update_privacy_settings(data)
        response_schema = PrivacySettingsResponseSchema()
        return success_response(response_schema.dump(updated_settings), 
                               "Privacy settings updated successfully")
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ========== FR-39: Communication Policies Management ==========

@admin_bp.route('/communication-policies', methods=['GET'])
@require_role('Admin')
def get_communication_policies():
    """
    Get all communication policies (FR-39)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Communication policies retrieved successfully
    """
    try:
        policies = admin_service.get_communication_policies()
        schema = CommunicationPoliciesResponseSchema()
        return success_response(schema.dump({'policies': policies}), 
                               "Communication policies retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/communication-policies/<notification_type>', methods=['GET'])
@require_role('Admin')
def get_communication_policy(notification_type):
    """
    Get communication policy for a notification type (FR-39)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: notification_type
        in: path
        required: true
        schema:
          type: string
          example: "ai_result_ready"
    responses:
      200:
        description: Communication policy retrieved successfully
      404:
        description: Policy not found
    """
    try:
        policy = admin_service.get_communication_policy_by_type(notification_type)
        if not policy:
            return error_response(f"Communication policy for {notification_type} not found", 404)
        
        from api.schemas.admin_schema import CommunicationPolicySchema
        schema = CommunicationPolicySchema()
        return success_response(schema.dump(policy), 
                               "Communication policy retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/communication-policies/<notification_type>', methods=['PUT'])
@require_role('Admin')
def update_communication_policy(notification_type):
    """
    Update communication policy for a notification type (FR-39)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: notification_type
        in: path
        required: true
        schema:
          type: string
          example: "ai_result_ready"
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            enabled:
              type: boolean
            channels:
              type: array
              items:
                type: string
                enum: [in_app, email, sms]
            recipients:
              type: array
              items:
                type: string
                enum: [patient, doctor, clinic_manager, admin]
            frequency_limit:
              type: integer
            priority:
              type: string
              enum: [low, normal, high, urgent]
    responses:
      200:
        description: Communication policy updated successfully
      400:
        description: Invalid input
      404:
        description: Policy not found
    """
    try:
        schema = CommunicationPolicyUpdateRequestSchema()
        data = schema.load(request.get_json())
        
        updated_policy = admin_service.update_communication_policy(notification_type, data)
        from api.schemas.admin_schema import CommunicationPolicySchema
        response_schema = CommunicationPolicySchema()
        return success_response(response_schema.dump(updated_policy), 
                               "Communication policy updated successfully")
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/communication-policies/<notification_type>', methods=['POST'])
@require_role('Admin')
def create_communication_policy(notification_type):
    """
    Create new communication policy for a notification type (FR-39)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: notification_type
        in: path
        required: true
        schema:
          type: string
          example: "subscription_expired"
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - enabled
            - channels
            - recipients
            - priority
          properties:
            enabled:
              type: boolean
            channels:
              type: array
              items:
                type: string
                enum: [in_app, email, sms]
            recipients:
              type: array
              items:
                type: string
                enum: [patient, doctor, clinic_manager, admin]
            frequency_limit:
              type: integer
            priority:
              type: string
              enum: [low, normal, high, urgent]
    responses:
      201:
        description: Communication policy created successfully
      400:
        description: Invalid input
    """
    try:
        from api.schemas.admin_schema import CommunicationPolicySchema
        schema = CommunicationPolicySchema()
        data = schema.load(request.get_json())
        
        created_policy = admin_service.create_communication_policy(notification_type, data)
        response_schema = CommunicationPolicySchema()
        return success_response(response_schema.dump(created_policy), 
                               "Communication policy created successfully", 201)
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ========== FR-31: Manage Accounts, Doctors, and Clinics ==========

@admin_bp.route('/accounts', methods=['GET'])
@require_role('Admin')
def list_accounts():
    """
    List all accounts with filter and pagination (FR-31)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
          enum: [active, inactive, suspended]
        description: Filter by account status
      - name: role_id
        in: query
        required: false
        schema:
          type: integer
        description: Filter by role ID
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 20
        description: Number of results per page
      - name: page
        in: query
        required: false
        schema:
          type: integer
          default: 1
        description: Page number
    responses:
      200:
        description: Accounts retrieved successfully
    """
    try:
        status = request.args.get('status', None)
        role_id = request.args.get('role_id', None, type=int)
        limit = request.args.get('limit', 20, type=int)
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * limit
        
        accounts, total_count = admin_service.list_accounts_paginated(
            status=status, role_id=role_id, limit=limit, offset=offset
        )
        
        return success_response({
            'accounts': [{'account_id': a.account_id, 'email': a.email, 'role_id': a.role_id, 'status': a.status, 'clinic_id': a.clinic_id} for a in accounts],
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit
        }, "Accounts retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/accounts/<int:account_id>', methods=['PUT'])
@require_role('Admin')
def update_account(account_id: int):
    """
    Update account (FR-31)
    ---
    tags:
      - Admin
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
    responses:
      200:
        description: Account updated successfully
    """
    try:
        data = request.get_json()
        updated_account = admin_service.update_account(account_id, **data)
        if not updated_account:
            return error_response("Account not found", 404)
        
        return success_response({'account_id': updated_account.account_id, 'email': updated_account.email, 'status': updated_account.status}, 
                               "Account updated successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@require_role('Admin')
def delete_account(account_id: int):
    """
    Delete account (FR-31)
    ---
    tags:
      - Admin
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
    """
    try:
        result = admin_service.delete_account(account_id)
        if not result:
            return error_response("Account not found", 404)
        
        return success_response({'deleted': True}, "Account deleted successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/doctors', methods=['GET'])
@require_role('Admin')
def list_doctors():
    """
    List all doctors with filter and pagination (FR-31)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: specialization
        in: query
        required: false
        schema:
          type: string
        description: Filter by specialization
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 20
      - name: page
        in: query
        required: false
        schema:
          type: integer
          default: 1
    responses:
      200:
        description: Doctors retrieved successfully
    """
    try:
        specialization = request.args.get('specialization', None)
        limit = request.args.get('limit', 20, type=int)
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * limit
        
        doctors, total_count = admin_service.list_doctors_paginated(
            specialization=specialization, limit=limit, offset=offset
        )
        
        return success_response({
            'doctors': [{'doctor_id': d.doctor_id, 'account_id': d.account_id, 'doctor_name': d.doctor_name, 'specialization': d.specialization, 'license_number': d.license_number} for d in doctors],
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit
        }, "Doctors retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@require_role('Admin')
def update_doctor(doctor_id: int):
    """
    Update doctor (FR-31)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    responses:
      200:
        description: Doctor updated successfully
    """
    try:
        data = request.get_json()
        updated_doctor = admin_service.update_doctor(doctor_id, **data)
        if not updated_doctor:
            return error_response("Doctor not found", 404)
        
        return success_response({'doctor_id': updated_doctor.doctor_id, 'doctor_name': updated_doctor.doctor_name, 'specialization': updated_doctor.specialization}, 
                               "Doctor updated successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@require_role('Admin')
def delete_doctor(doctor_id: int):
    """
    Delete doctor (FR-31)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Doctor deleted successfully
    """
    try:
        result = admin_service.delete_doctor(doctor_id)
        if not result:
            return error_response("Doctor not found", 404)
        
        return success_response({'deleted': True}, "Doctor deleted successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/clinics', methods=['GET'])
@require_role('Admin')
def list_clinics():
    """
    List all clinics with filter and pagination (FR-31)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
          enum: [pending, verified, rejected, suspended]
        description: Filter by clinic status
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 20
      - name: page
        in: query
        required: false
        schema:
          type: integer
          default: 1
    responses:
      200:
        description: Clinics retrieved successfully
    """
    try:
        status = request.args.get('status', None)
        limit = request.args.get('limit', 20, type=int)
        page = request.args.get('page', 1, type=int)
        offset = (page - 1) * limit
        
        clinics, total_count = admin_service.list_clinics_paginated(
            status=status, limit=limit, offset=offset
        )
        
        return success_response({
            'clinics': [{'clinic_id': c.clinic_id, 'name': c.name, 'address': c.address, 'phone': c.phone, 'verification_status': c.verification_status} for c in clinics],
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit
        }, "Clinics retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/clinics/<int:clinic_id>', methods=['PUT'])
@require_role('Admin')
def update_clinic(clinic_id: int):
    """
    Update clinic (FR-31)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    responses:
      200:
        description: Clinic updated successfully
    """
    try:
        data = request.get_json()
        updated_clinic = admin_service.update_clinic(clinic_id, **data)
        if not updated_clinic:
            return error_response("Clinic not found", 404)
        
        return success_response({'clinic_id': updated_clinic.clinic_id, 'name': updated_clinic.name, 'verification_status': updated_clinic.verification_status}, 
                               "Clinic updated successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/clinics/<int:clinic_id>', methods=['DELETE'])
@require_role('Admin')
def delete_clinic(clinic_id: int):
    """
    Delete clinic (FR-31)
    ---
    tags:
      - Admin
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
        description: Clinic deleted successfully
    """
    try:
        result = admin_service.delete_clinic(clinic_id)
        if not result:
            return error_response("Clinic not found", 404)
        
        return success_response({'deleted': True}, "Clinic deleted successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ========== FR-32: Role & Permission Management Endpoints ==========

@admin_bp.route('/roles', methods=['GET'])
@require_role('Admin')
def list_roles():
    """
    List all roles with pagination
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: query
        name: limit
        type: integer
        default: 50
      - in: query
        name: offset
        type: integer
        default: 0
    responses:
      200:
        description: List of roles retrieved
        schema:
          properties:
            roles:
              type: array
            total:
              type: integer
            limit:
              type: integer
            offset:
              type: integer
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        roles, total = admin_service.list_roles(limit, offset)
        
        return success_response({
            'roles': [r.__dict__ if hasattr(r, '__dict__') else r for r in roles],
            'total': total,
            'limit': limit,
            'offset': offset
        }, "Roles retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/roles', methods=['POST'])
@require_role('Admin')
def create_role():
    """
    Create a new role
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: body
        name: body
        required: true
        schema:
          properties:
            role_name:
              type: string
    responses:
      201:
        description: Role created successfully
    """
    try:
        data = request.get_json()
        role_name = data.get('role_name')
        
        if not role_name:
            return validation_error_response({'role_name': ['Role name is required']})
        
        role = admin_service.create_role(role_name)
        return success_response(role.__dict__ if hasattr(role, '__dict__') else role, 
                              "Role created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/roles/<int:role_id>', methods=['PUT'])
@require_role('Admin')
def update_role(role_id):
    """
    Update a role
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          properties:
            role_name:
              type: string
    responses:
      200:
        description: Role updated successfully
    """
    try:
        data = request.get_json()
        role_name = data.get('role_name')
        
        if not role_name:
            return validation_error_response({'role_name': ['Role name is required']})
        
        role = admin_service.update_role(role_id, role_name)
        if not role:
            return error_response("Role not found", 404)
        
        return success_response(role.__dict__ if hasattr(role, '__dict__') else role,
                              "Role updated successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@require_role('Admin')
def delete_role(role_id):
    """
    Delete a role
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
    responses:
      200:
        description: Role deleted successfully
    """
    try:
        result = admin_service.delete_role(role_id)
        if not result:
            return error_response("Role not found", 404)
        
        return success_response({'deleted': True}, "Role deleted successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/roles/<int:role_id>/permissions', methods=['GET'])
@require_role('Admin')
def get_role_permissions(role_id):
    """
    Get all permissions for a role
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
    responses:
      200:
        description: List of permissions retrieved
    """
    try:
        permissions = admin_service.get_role_permissions(role_id)
        return success_response({'permissions': permissions}, 
                              "Permissions retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
@require_role('Admin')
def assign_permission(role_id):
    """
    Assign a permission to a role
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          properties:
            resource:
              type: string
            action:
              type: string
    responses:
      201:
        description: Permission assigned successfully
    """
    try:
        data = request.get_json()
        resource = data.get('resource')
        action = data.get('action')
        
        if not resource or not action:
            return validation_error_response({
                'resource': ['Resource is required'],
                'action': ['Action is required']
            })
        
        permission = admin_service.assign_permission(role_id, resource, action)
        return success_response(permission, "Permission assigned successfully", 201)
    except ValueError as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/roles/<int:role_id>/permissions/<resource>/<action>', methods=['DELETE'])
@require_role('Admin')
def revoke_permission(role_id, resource, action):
    """
    Revoke a permission from a role
    ---
    tags:
      - Admin Management (FR-32)
    parameters:
      - in: path
        name: role_id
        type: integer
        required: true
      - in: path
        name: resource
        type: string
        required: true
      - in: path
        name: action
        type: string
        required: true
    responses:
      200:
        description: Permission revoked successfully
    """
    try:
        result = admin_service.revoke_permission(role_id, resource, action)
        if not result:
            return error_response("Permission not found", 404)
        
        return success_response({'revoked': True}, "Permission revoked successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ============================================================================
# AI MODEL CONFIGURATION ENDPOINTS (FR-33)
# ============================================================================

@admin_bp.route('/ai-models', methods=['GET'])
@require_role('Admin')
def list_ai_models():
    """
    Get paginated list of all AI model versions
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
      - in: query
        name: offset
        type: integer
        default: 0
    responses:
      200:
        description: List of AI models retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                models:
                  type: array
                  items:
                    type: object
                total:
                  type: integer
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate pagination parameters
        if limit <= 0 or offset < 0:
            return validation_error_response({
                'limit': ['Limit must be positive'],
                'offset': ['Offset must be non-negative']
            })
        
        models, total = admin_service.list_ai_models(limit, offset)
        return success_response({
            'models': [m.to_dict() if hasattr(m, 'to_dict') else m for m in models],
            'total': total,
            'limit': limit,
            'offset': offset
        }, "AI models retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-models', methods=['POST'])
@require_role('Admin')
def create_ai_model():
    """
    Create a new AI model version with configuration
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            model_name:
              type: string
              example: "Retinal Vessel Analyzer"
            version:
              type: string
              example: "v2.1.0"
            threshold_config:
              type: object
              properties:
                confidence_threshold:
                  type: number
                  example: 0.85
                risk_level_mapping:
                  type: object
                  properties:
                    low:
                      type: object
                      properties:
                        min:
                          type: number
                        max:
                          type: number
                    medium:
                      type: object
                    high:
                      type: object
                    critical:
                      type: object
            active_flag:
              type: boolean
              example: false
    responses:
      201:
        description: AI model created successfully
      400:
        description: Invalid input
      409:
        description: Conflict (e.g., model version already exists)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['model_name', 'version', 'threshold_config']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return validation_error_response({f: [f'{f} is required'] for f in missing})
        
        # Validate threshold_config structure
        threshold_config = data['threshold_config']
        if 'confidence_threshold' not in threshold_config or 'risk_level_mapping' not in threshold_config:
            return validation_error_response({
                'threshold_config': ['Must contain confidence_threshold and risk_level_mapping']
            })
        
        # Validate risk_level_mapping
        if not admin_service.ai_config_repository.validate_risk_mapping(threshold_config['risk_level_mapping']):
            return validation_error_response({
                'risk_level_mapping': ['Invalid risk level mapping structure or ranges']
            })
        
        model = admin_service.create_ai_model(
            model_name=data['model_name'],
            version=data['version'],
            threshold_config=threshold_config,
            active_flag=data.get('active_flag', False)
        )
        
        return success_response(model.to_dict() if hasattr(model, 'to_dict') else model, 
                              "AI model created successfully", 201)
    except ValueError as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-models/<int:model_id>', methods=['GET'])
@require_role('Admin')
def get_ai_model_details(model_id):
    """
    Get detailed information about an AI model including its configuration
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: path
        name: model_id
        type: integer
        required: true
    responses:
      200:
        description: Model details retrieved successfully
      404:
        description: Model not found
    """
    try:
        details = admin_service.get_ai_model_details(model_id)
        if not details:
            return error_response("AI model not found", 404)
        
        return success_response(details, "AI model details retrieved successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-models/<int:model_id>/activate', methods=['PUT'])
@require_role('Admin')
def activate_ai_model(model_id):
    """
    Activate an AI model version (deactivates current active model)
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: path
        name: model_id
        type: integer
        required: true
    responses:
      200:
        description: AI model activated successfully
      404:
        description: Model not found
    """
    try:
        model = admin_service.activate_ai_model(model_id)
        if not model:
            return error_response("AI model not found", 404)
        
        return success_response(model.to_dict() if hasattr(model, 'to_dict') else model,
                              "AI model activated successfully")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-models/<int:model_id>/rollback', methods=['POST'])
@require_role('Admin')
def rollback_ai_model(model_id):
    """
    Rollback to the previous AI model version
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: path
        name: model_id
        type: integer
        required: true
    responses:
      200:
        description: Rollback successful
      404:
        description: Previous model version not found
    """
    try:
        previous_model = admin_service.rollback_ai_model(model_id)
        if not previous_model:
            return error_response("No previous model version found", 404)
        
        return success_response(previous_model.to_dict() if hasattr(previous_model, 'to_dict') else previous_model,
                              "Rollback to previous model successful")
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-models/<int:model_id>/threshold', methods=['PUT'])
@require_role('Admin')
def update_ai_threshold(model_id):
    """
    Update AI model threshold configuration
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: path
        name: model_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            confidence_threshold:
              type: number
              example: 0.80
            risk_level_mapping:
              type: object
              properties:
                low:
                  type: object
                  properties:
                    min:
                      type: number
                    max:
                      type: number
                medium:
                  type: object
                high:
                  type: object
                critical:
                  type: object
    responses:
      200:
        description: Threshold configuration updated successfully
      400:
        description: Invalid input
      404:
        description: Model not found
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return validation_error_response({'body': ['Request body is required']})
        
        # If risk_level_mapping provided, validate it
        if 'risk_level_mapping' in data:
            if not admin_service.ai_config_repository.validate_risk_mapping(data['risk_level_mapping']):
                return validation_error_response({
                    'risk_level_mapping': ['Invalid risk level mapping structure or ranges']
                })
        
        # Validate confidence_threshold if provided
        if 'confidence_threshold' in data:
            if not isinstance(data['confidence_threshold'], (int, float)) or \
               not (0.0 <= data['confidence_threshold'] <= 1.0):
                return validation_error_response({
                    'confidence_threshold': ['Must be a number between 0.0 and 1.0']
                })
        
        config = admin_service.update_ai_threshold(model_id, data)
        if not config:
            return error_response("AI model not found", 404)
        
        return success_response(config, "Threshold configuration updated successfully")
    except ValueError as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@admin_bp.route('/ai-models/<int:model_id>/retrain-policy', methods=['PUT'])
@require_role('Admin')
def update_ai_retrain_policy(model_id):
    """
    Update AI model auto-retrain policy
    ---
    tags:
      - AI Model Configuration (FR-33)
    parameters:
      - in: path
        name: model_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            auto_retrain_enabled:
              type: boolean
              example: true
            retrain_threshold:
              type: number
              example: 0.05
            retrain_schedule:
              type: string
              enum: ["weekly", "monthly", "quarterly"]
              example: "weekly"
            max_error_rate:
              type: number
              example: 0.15
            performance_metric:
              type: string
              enum: ["accuracy", "f1_score", "auc"]
              example: "f1_score"
    responses:
      200:
        description: Retrain policy updated successfully
      400:
        description: Invalid input
      404:
        description: Model not found
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return validation_error_response({'body': ['Request body is required']})
        
        # Validate enums if provided
        valid_schedules = ['weekly', 'monthly', 'quarterly']
        valid_metrics = ['accuracy', 'f1_score', 'auc']
        
        if 'retrain_schedule' in data and data['retrain_schedule'] not in valid_schedules:
            return validation_error_response({
                'retrain_schedule': [f'Must be one of {valid_schedules}']
            })
        
        if 'performance_metric' in data and data['performance_metric'] not in valid_metrics:
            return validation_error_response({
                'performance_metric': [f'Must be one of {valid_metrics}']
            })
        
        # Validate numeric ranges
        if 'retrain_threshold' in data:
            if not isinstance(data['retrain_threshold'], (int, float)) or \
               not (0.0 <= data['retrain_threshold'] <= 1.0):
                return validation_error_response({
                    'retrain_threshold': ['Must be a number between 0.0 and 1.0']
                })
        
        if 'max_error_rate' in data:
            if not isinstance(data['max_error_rate'], (int, float)) or \
               not (0.0 <= data['max_error_rate'] <= 1.0):
                return validation_error_response({
                    'max_error_rate': ['Must be a number between 0.0 and 1.0']
                })
        
        policy = admin_service.update_ai_retrain_policy(model_id, data)
        if not policy:
            return error_response("AI model not found", 404)
        
        return success_response(policy, "Retrain policy updated successfully")
    except ValueError as e:
        return error_response(str(e), 409)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)
