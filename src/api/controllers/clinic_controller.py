from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.clinic_repository import ClinicRepository
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.doctor_profile_repository import DoctorProfileRepository
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.repositories.ai_result_repository import AiResultRepository
from infrastructure.repositories.subscription_repository import SubscriptionRepository
from infrastructure.repositories.medical_report_repository import MedicalReportRepository
from infrastructure.databases.mssql import session
from services.clinic_service import ClinicService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import ClinicCreateRequestSchema, ClinicUpdateRequestSchema, ClinicResponseSchema

clinic_bp = Blueprint('clinic', __name__, url_prefix='/api/clinics')

# Initialize repositories
clinic_repo = ClinicRepository(session)
account_repo = AccountRepository(session)
patient_repo = PatientProfileRepository(session)
doctor_repo = DoctorProfileRepository(session)
image_repo = RetinalImageRepository(session)
result_repo = AiResultRepository(session)
subscription_repo = SubscriptionRepository(session)
report_repo = MedicalReportRepository(session)

# Initialize SERVICE with dependency injection ✅
clinic_service = ClinicService(
    repository=clinic_repo,
    account_repository=account_repo,
    patient_repository=patient_repo,
    doctor_repository=doctor_repo,
    image_repository=image_repo,
    result_repository=result_repo,
    subscription_repository=subscription_repo,
    report_repository=report_repo
)


@clinic_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Clinic
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Clinic service is running")


@clinic_bp.route('', methods=['POST'])
def create_clinic():
    """
    Register a new clinic
    ---
    tags:
      - Clinic
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
            - clinic_name
            - address
            - phone_number
          properties:
            clinic_name:
              type: string
              example: "City Eye Clinic"
            address:
              type: string
              example: "123 Main Street, City"
            phone_number:
              type: string
              example: "+1234567890"
            logo_url:
              type: string
              example: "https://example.com/logo.png"
            description:
              type: string
              example: "Leading eye care clinic"
    responses:
      201:
        description: Clinic created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Clinic created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate request data with schema
        schema = ClinicCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Call SERVICE to register clinic ✅
        clinic = clinic_service.register_clinic(
            name=data['name'],
            address=data['address'],
            phone=data['phone'],
            logo_url=data['logo_url'],
            verification_status='pending'
        )
        
        # STEP 3: Serialize response with schema
        response_schema = ClinicResponseSchema()
        return success_response(response_schema.dump(clinic), 'Clinic registered successfully. Pending verification.', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>', methods=['GET'])
def get_clinic(clinic_id):
    """
    Get clinic by ID
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Clinic found
      404:
        description: Clinic not found
    """
    try:
        # Call SERVICE ✅
        clinic = clinic_service.get_clinic_by_id(clinic_id)
        if not clinic:
            return not_found_response('Clinic not found')
        
        # Serialize response with schema
        schema = ClinicResponseSchema()
        return success_response(schema.dump(clinic))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/search', methods=['GET'])
def search_clinics():
    """
    Search clinics by name
    ---
    tags:
      - Clinic
    parameters:
      - name: name
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of clinics
    """
    try:
        name = request.args.get('name', '')
        if not name:
            return validation_error_response({'name': 'Name parameter is required'})
        
        # Call SERVICE ✅
        clinics = clinic_service.search_clinics_by_name(name)
        
        return success_response({
            'count': len(clinics),
            'clinics': ClinicResponseSchema(many=True).dump(clinics)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('', methods=['GET'])
def get_all_clinics():
    """
    Get all clinics
    ---
    tags:
      - Clinic
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
          enum: [pending, verified, rejected]
    responses:
      200:
        description: List of clinics
    """
    try:
        status = request.args.get('status')
        
        # Call SERVICE ✅
        clinics = clinic_service.list_all_clinics(status)
        
        return success_response({
            'count': len(clinics),
            'clinics': ClinicResponseSchema(many=True).dump(clinics)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/verified', methods=['GET'])
def get_verified_clinics():
    """
    Get all verified clinics
    ---
    tags:
      - Clinic
    responses:
      200:
        description: List of verified clinics
    """
    try:
        # Call SERVICE ✅
        clinics = clinic_service.get_verified_clinics()
        
        return success_response({
            'count': len(clinics),
            'clinics': ClinicResponseSchema(many=True).dump(clinics)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/pending', methods=['GET'])
def get_pending_clinics():
    """
    Get clinics pending verification (Admin only)
    ---
    tags:
      - Clinic
    responses:
      200:
        description: List of pending clinics
    """
    try:
        # Call SERVICE ✅
        clinics = clinic_service.get_pending_clinics()
        
        return success_response({
            'count': len(clinics),
            'clinics': ClinicResponseSchema(many=True).dump(clinics)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/verify', methods=['PUT'])
def verify_clinic(clinic_id):
    """
    Verify clinic (Admin only) - FR-22 Verification Workflow
    
    Workflow: pending → verified
    Only clinics with 'pending' status can be verified.
    ---
    tags:
      - Clinic
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: clinic_id
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
            admin_notes:
              type: string
              example: "All documents verified. License valid."
              description: Optional notes from admin
    responses:
      200:
        description: Clinic verified successfully
              schema:
          type: object
          properties:
            message:
              type: string
              example: Clinic verified successfully
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                clinic_name:
                  type: string
                verification_status:
                  type: string
                  enum: [verified]
      400:
        description: Invalid request (clinic not in pending status)
      404:
        description: Clinic not found
    """
    try:
        from domain.exceptions import NotFoundException, ValidationException
        
        data = request.get_json() or {}
        admin_notes = data.get('admin_notes')

        # Call SERVICE ✅
        clinic = clinic_service.verify_clinic(clinic_id, admin_notes=admin_notes)
        if not clinic:
            return not_found_response('Clinic not found')
        
        schema = ClinicResponseSchema()
        return success_response(schema.dump(clinic), 'Clinic verified successfully')
    
    except NotFoundException as e:
        return not_found_response(str(e))
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/reject', methods=['PUT'])
def reject_clinic(clinic_id):
    """
    Reject clinic verification (Admin only) - FR-22 Verification Workflow
    
    Workflow: pending → rejected
    Only clinics with 'pending' status can be rejected.
    Rejection reason is recommended for audit trail.
    ---
    tags:
      - Clinic
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: clinic_id
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
            admin_notes:
              type: string
              example: "Invalid license number or missing required documents"
              description: Reason for rejection (recommended)
    responses:
      200:
        description: Clinic rejected successfully
                schema:
          type: object
          properties:
            message:
              type: string
              example: Clinic verification rejected
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                clinic_name:
                  type: string
                verification_status:
                  type: string
                  enum: [rejected]
      400:
        description: Invalid request (clinic not in pending status)
      404:
        description: Clinic not found
    """
    try:
        from domain.exceptions import NotFoundException
        
        data = request.get_json() or {}
        rejection_reason = data.get('rejection_reason')

        # Call SERVICE ✅
        clinic = clinic_service.reject_clinic(clinic_id, rejection_reason=rejection_reason)
        if not clinic:
            return not_found_response('Clinic not found')
        
        return success_response({
            'clinic_id': clinic.clinic_id,
            'clinic_name': clinic.clinic_name,
            'verification_status': clinic.verification_status
        }, 'Clinic verification rejected')

    except NotFoundException as e:
        return not_found_response(str(e))
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>', methods=['PUT'])
def update_clinic(clinic_id):
    """
    Update clinic information
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: clinic_id
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
            clinic_name:
              type: string
              example: "Updated Clinic Name"
            address:
              type: string
              example: "456 New Street"
            phone_number:
              type: string
              example: "+1234567890"
            logo_url:
              type: string
              example: "https://example.com/new-logo.png"
            description:
              type: string
              example: "Updated description"
    responses:
      200:
        description: Clinic updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Clinic updated successfully
            data:
              type: object
      404:
        description: Clinic not found
    """
    try:
        data = request.get_json()
        
        # Call SERVICE ✅
        clinic = clinic_service.update_clinic(clinic_id, **data)
        if not clinic:
            return not_found_response('Clinic not found')
        
        schema = ClinicResponseSchema()
        return success_response(schema.dump(clinic), 'Clinic updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>', methods=['DELETE'])
def delete_clinic(clinic_id):
    """
    Delete clinic
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Clinic deleted successfully
      404:
        description: Clinic not found
    """
    try:
        # Call SERVICE ✅
        result = clinic_service.delete_clinic(clinic_id)
        if not result:
            return not_found_response('Clinic not found')
        
        return success_response(None, 'Clinic deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get clinic statistics
    ---
    tags:
      - Clinic
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
          enum: [pending, verified, rejected]
    responses:
      200:
        description: Clinic statistics
    """
    try:
        status = request.args.get('status')
        
        if status:
            # Call SERVICE ✅
            count = clinic_service.count_clinics(status)
            return success_response({
                'status': status,
                'count': count
            })
        else:
            # Call SERVICE to get statistics ✅
            stats = clinic_service.get_clinic_statistics()
            return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


# ========== PHASE 3: CLINIC FUNCTIONAL REQUIREMENTS ==========

@clinic_bp.route('/<int:clinic_id>/verification-status', methods=['GET'])
def get_verification_status(clinic_id):
    """
    Get clinic verification status (FR-22)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Verification status retrieved
        schema:
          type: object
          properties:
            clinic_id:
              type: integer
            verification_status:
              type: string
              enum: [pending, verified, rejected]
      404:
        description: Clinic not found
    """
    try:
        from domain.exceptions import NotFoundException
        status = clinic_service.get_verification_status(clinic_id)
        return success_response({
            'clinic_id': clinic_id,
            'verification_status': status
        })
    except NotFoundException as e:
        return not_found_response(str(e))
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/members', methods=['GET'])
def get_clinic_members(clinic_id):
    """
    Get all members (doctors and patients) in clinic (FR-23)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 2
    responses:
      200:
        description: Clinic members retrieved
        schema:
          type: object
          properties:
            clinic_id:
              type: integer
              example: 2
            doctors:
              type: array
              items:
                type: object
                properties:
                  account_id:
                    type: integer
                    example: 3
                  doctor_id:
                    type: integer
                    example: 2
                  doctor_name:
                    type: string
                    example: "Dr. Tran Thi B"
                  specialization:
                    type: string
                    example: "Ophthalmologist"
                  license_number:
                    type: string
                    example: "DOC-LICENSE-002"
            patients:
              type: array
              items:
                type: object
                properties:
                  account_id:
                    type: integer
                    example: 4
                  patient_id:
                    type: integer
                    example: 1
                  patient_name:
                    type: string
                    example: "Nguyen Van Patient 1"
                  date_of_birth:
                    type: string
                    format: date
                    example: "1980-01-15"
                  gender:
                    type: string
                    example: "Male"
            total_doctors:
              type: integer
              example: 1
            total_patients:
              type: integer
              example: 2
      400:
        description: Invalid request
      404:
        description: Clinic not found
      500:
        description: Internal server error
    """
    try:
        members = clinic_service.get_clinic_members(clinic_id)
        return success_response(members)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/risk-aggregation', methods=['GET'])
def get_clinic_risk_aggregation(clinic_id):
    """
    Get aggregated risk data for all patients in clinic (FR-25)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
    responses:
      200:
        description: Risk aggregation retrieved
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                  example: 1
                total_patients:
                  type: integer
                  example: 10
                total_analyses:
                  type: integer
                  example: 25
                risk_distribution:
                  type: object
                  properties:
                    low:
                      type: integer
                      example: 10
                    medium:
                      type: integer
                      example: 8
                    high:
                      type: integer
                      example: 5
                    critical:
                      type: integer
                      example: 2
                high_risk_patients_count:
                  type: integer
                  example: 7
                high_risk_patients:
                  type: array
                  items:
                    type: object
                    properties:
                      patient_id:
                        type: integer
                        example: 1
                      patient_name:
                        type: string
                        example: "Nguyen Van A"
                      risk_level:
                        type: string
                        example: "high"
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        aggregation = clinic_service.get_clinic_risk_aggregation(clinic_id)
        return success_response(aggregation)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/usage', methods=['GET'])
def get_clinic_usage(clinic_id):
    """
    Get clinic usage summary including images and package usage (FR-27)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Usage summary retrieved
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                  example: 1
                total_images_uploaded:
                  type: integer
                  example: 50
                total_analyses:
                  type: integer
                  example: 45
                active_subscriptions:
                  type: integer
                  example: 2
                total_credits_allocated:
                  type: integer
                  example: 1000
                remaining_credits:
                  type: integer
                  example: 750
                credits_used:
                  type: integer
                  example: 250
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        usage = clinic_service.get_clinic_usage_summary(clinic_id)
        return success_response(usage)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/high-risk-alerts', methods=['GET'])
def get_high_risk_alerts(clinic_id):
    """
    Get high-risk patient alerts for clinic (FR-29)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - name: risk_level
        in: query
        required: false
        schema:
          type: string
          enum: [high, critical]
          default: high
        description: Risk level to filter
    responses:
      200:
        description: High-risk alerts retrieved
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                  example: 1
                risk_level:
                  type: string
                  example: "high"
                alerts:
                  type: array
                  items:
                    type: object
                    properties:
                      patient_id:
                        type: integer
                        example: 1
                      patient_name:
                        type: string
                        example: "Nguyen Van A"
                      risk_level:
                        type: string
                        example: "high"
                      latest_analysis:
                        type: object
                        properties:
                          risk_level:
                            type: string
                            example: "high"
                          confidence_score:
                            type: number
                            format: float
                            example: 95.5
                          disease_type:
                            type: string
                            example: "diabetic_retinopathy"
                      alert_timestamp:
                        type: string
                        format: date-time
                        example: "2024-01-15T10:30:00"
                count:
                  type: integer
                  example: 5
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        risk_level = request.args.get('risk_level', 'high')
        alerts = clinic_service.get_high_risk_alerts(clinic_id, risk_level)
        return success_response({
            'clinic_id': clinic_id,
            'risk_level': risk_level,
            'alerts': alerts,
            'count': len(alerts)
        })
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/abnormal-trends', methods=['GET'])
def detect_abnormal_trends(clinic_id):
    """
    Detect abnormal trends in clinic patient data (FR-29)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - name: days
        in: query
        required: false
        schema:
          type: integer
          default: 30
        description: Number of days to analyze
    responses:
      200:
        description: Abnormal trends detected
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                  example: 1
                period_days:
                  type: integer
                  example: 30
                total_patients_analyzed:
                  type: integer
                  example: 10
                abnormal_trends_detected:
                  type: boolean
                  example: true
                abnormal_trends:
                  type: object
                  properties:
                    risk_increases:
                      type: array
                      items:
                        type: object
                    sudden_spikes:
                      type: array
                      items:
                        type: object
                    total_abnormal_cases:
                      type: integer
                summary:
                  type: object
                  properties:
                    risk_increases_count:
                      type: integer
                    sudden_spikes_count:
                      type: integer
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        days = request.args.get('days', type=int, default=30)
        trends = clinic_service.detect_abnormal_trends(clinic_id, days)
        return success_response(trends)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

@clinic_bp.route('/<int:clinic_id>/reports-summary', methods=['GET'])
def get_clinic_reports_summary(clinic_id):
    """
    Get summary of all reports for clinic patients (FR-25)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
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
        description: Reports summary retrieved
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                total_reports:
                  type: integer
                unique_patients:
                  type: integer
                unique_doctors:
                  type: integer
                reports_by_month:
                  type: object
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        from datetime import date as date_type
        
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
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
        
        summary = clinic_service.get_clinic_reports_summary(clinic_id, start_date, end_date)
        return success_response(summary)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/screening-report', methods=['GET'])
def generate_clinic_screening_report(clinic_id):
    """
    Generate clinic-wide report for screening campaigns (FR-26)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - name: campaign_name
        in: query
        required: false
        schema:
          type: string
        description: Optional campaign name
      - name: start_date
        in: query
        required: false
        schema:
          type: string
          format: date
        description: Campaign start date (YYYY-MM-DD)
      - name: end_date
        in: query
        required: false
        schema:
          type: string
          format: date
        description: Campaign end date (YYYY-MM-DD)
    responses:
      200:
        description: Screening report generated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                campaign_name:
                  type: string
                  example: "Screening Campaign - Clinic 1"
                clinic_id:
                  type: integer
                  example: 1
                period:
                  type: object
                  properties:
                    start_date:
                      type: string
                      format: date
                      example: "2024-01-01"
                    end_date:
                      type: string
                      format: date
                      example: "2024-01-31"
                    generated_at:
                      type: string
                      format: date-time
                      example: "2024-01-15T10:30:00"
                summary:
                  type: object
                  properties:
                    total_patients_screened:
                      type: integer
                      example: 50
                    total_images_analyzed:
                      type: integer
                      example: 120
                    total_reports_generated:
                      type: integer
                      example: 45
                    high_risk_cases:
                      type: integer
                      example: 8
                risk_distribution:
                  type: object
                  properties:
                    low:
                      type: integer
                      example: 30
                    medium:
                      type: integer
                      example: 12
                    high:
                      type: integer
                      example: 6
                    critical:
                      type: integer
                      example: 2
                usage_statistics:
                  type: object
                  properties:
                    images_uploaded:
                      type: integer
                      example: 120
                    credits_used:
                      type: integer
                      example: 100
                    remaining_credits:
                      type: integer
                      example: 200
                reports_statistics:
                  type: object
                  properties:
                    total_reports:
                      type: integer
                      example: 45
                    unique_patients:
                      type: integer
                      example: 40
                    unique_doctors:
                      type: integer
                      example: 5
                high_risk_patients:
                  type: array
                  items:
                    type: object
                    properties:
                      patient_id:
                        type: integer
                        example: 1
                      patient_name:
                        type: string
                        example: "John Doe"
                      risk_level:
                        type: string
                        example: "high"
                      confidence:
                        type: number
                        format: float
                        example: 0.95
                recommendations:
                  type: array
                  items:
                    type: string
                  example:
                    - "⚠️ High-risk rate is 16.0%. Consider increasing screening frequency and follow-up care."
                    - "✅ Screening campaign is running smoothly. Continue regular monitoring."
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        from datetime import date as date_type
        
        campaign_name = request.args.get('campaign_name')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
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
        
        report = clinic_service.generate_clinic_screening_report(
            clinic_id, campaign_name, start_date, end_date
        )
        return success_response(report)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/export-statistics', methods=['GET'])
def export_clinic_statistics(clinic_id):
    """
    Export clinic statistics for clinical research or management (FR-30)
    ---
    tags:
      - Clinic
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - name: format
        in: query
        required: false
        schema:
          type: string
          enum: [json, csv_data]
          default: json
        description: Export format (json or csv_data)
    responses:
      200:
        description: Statistics exported
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                clinic_id:
                  type: integer
                  example: 1
                export_date:
                  type: string
                  format: date-time
                  example: "2024-01-15T10:30:00"
                export_format:
                  type: string
                  enum: [json, csv_data]
                  example: "json"
                clinic_info:
                  type: object
                  properties:
                    total_doctors:
                      type: integer
                      example: 5
                    total_patients:
                      type: integer
                      example: 50
                risk_statistics:
                  type: object
                  properties:
                    total_analyses:
                      type: integer
                      example: 120
                    risk_distribution:
                      type: object
                      properties:
                        low:
                          type: integer
                          example: 80
                        medium:
                          type: integer
                          example: 25
                        high:
                          type: integer
                          example: 12
                        critical:
                          type: integer
                          example: 3
                    high_risk_patients_count:
                      type: integer
                      example: 15
                usage_statistics:
                  type: object
                  properties:
                    total_images_uploaded:
                      type: integer
                      example: 150
                    total_analyses:
                      type: integer
                      example: 120
                    active_subscriptions:
                      type: integer
                      example: 2
                    credits_used:
                      type: integer
                      example: 100
                    remaining_credits:
                      type: integer
                      example: 200
                reports_statistics:
                  type: object
                  properties:
                    total_reports:
                      type: integer
                      example: 45
                    unique_patients:
                      type: integer
                      example: 40
                    unique_doctors:
                      type: integer
                      example: 5
                    reports_by_month:
                      type: object
                      additionalProperties:
                        type: integer
                      example:
                        "2024-01": 20
                        "2024-02": 25
                trend_analysis:
                  type: object
                  properties:
                    abnormal_trends_detected:
                      type: boolean
                      example: true
                    risk_increases_count:
                      type: integer
                      example: 5
                    sudden_spikes_count:
                      type: integer
                      example: 2
                csv_format:
                  type: array
                  description: CSV format data (only if format=csv_data)
                  items:
                    type: array
                    items:
                      type: string
                  example:
                    - ["Metric", "Value"]
                    - ["Clinic ID", "1"]
                    - ["Total Doctors", "5"]
                    - ["Total Patients", "50"]
      400:
        description: Invalid request
      500:
        description: Internal server error
    """
    try:
        export_format = request.args.get('format', 'json')
        
        if export_format not in ['json', 'csv_data']:
            return error_response('Invalid format. Must be "json" or "csv_data"', 400)
        
        statistics = clinic_service.export_clinic_statistics(clinic_id, format=export_format)
        return success_response(statistics)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

