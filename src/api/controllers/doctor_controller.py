from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.doctor_profile_repository import DoctorProfileRepository
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.doctor_review_repository import DoctorReviewRepository
from infrastructure.repositories.medical_report_repository import MedicalReportRepository
from infrastructure.repositories.conversation_repository import ConversationRepository
from infrastructure.databases.mssql import session
from services.doctor_profile_service import DoctorProfileService
from services.account_service import AccountService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import DoctorProfileCreateRequestSchema, DoctorProfileUpdateRequestSchema, DoctorProfileResponseSchema
from domain.exceptions import NotFoundException, ValidationException

doctor_bp = Blueprint('doctor', __name__, url_prefix='/api/doctors')

# Initialize repositories (only for service initialization)
doctor_repo = DoctorProfileRepository(session)
account_repo = AccountRepository(session)
review_repo = DoctorReviewRepository(session)
report_repo = MedicalReportRepository(session)
conversation_repo = ConversationRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
# Inject all required repositories for performance summary
doctor_service = DoctorProfileService(
    repository=doctor_repo,
    review_repository=review_repo,
    report_repository=report_repo,
    conversation_repository=conversation_repo
)
account_service = AccountService(account_repo)


@doctor_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Doctor
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Doctor service is running")


@doctor_bp.route('', methods=['POST'])
def create_doctor():
    """
    Create a new doctor profile
    ---
    tags:
      - Doctor
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
            - account_id
            - doctor_name
            - specialization
            - license_number
          properties:
            account_id:
              type: integer
              example: 1
            doctor_name:
              type: string
              example: "Dr. Nguyen Van B"
            specialization:
              type: string
              example: "Ophthalmology"
            license_number:
              type: string
              example: "DR12345"
    responses:
      201:
        description: Doctor created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Doctor created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate request data with schema
        schema = DoctorProfileCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Check if account exists via SERVICE ✅
        account = account_service.get_account_by_id(data['account_id'])
        if not account:
            return not_found_response('Account not found')
        
        # STEP 3: Call SERVICE ✅ (Service handles license validation)
        doctor = doctor_service.create_doctor(
            account_id=data['account_id'],
            doctor_name=data['doctor_name'],
            specialization=data['specialization'],
            license_number=data['license_number']
        )
        
        # STEP 4: Serialize response with schema
        response_schema = DoctorProfileResponseSchema()
        return success_response(response_schema.dump(doctor), 'Doctor created successfully', 201)
        
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


@doctor_bp.route('/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    """
    Get doctor by ID
    ---
    tags:
      - Doctor
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Doctor found
      404:
        description: Doctor not found
    """
    try:
        # Call SERVICE ✅
        doctor = doctor_service.get_doctor_by_id(doctor_id)
        if not doctor:
            return not_found_response('Doctor not found')
        
        # Serialize response with schema
        schema = DoctorProfileResponseSchema()
        return success_response(schema.dump(doctor))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/account/<int:account_id>', methods=['GET'])
def get_doctor_by_account(account_id):
    """
    Get doctor by account ID
    ---
    tags:
      - Doctor
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Doctor found
      404:
        description: Doctor not found
    """
    try:
        # Call SERVICE ✅
        doctor = doctor_service.get_doctor_by_account(account_id)
        if not doctor:
            return not_found_response('Doctor not found')
        
        # Serialize response with schema
        schema = DoctorProfileResponseSchema()
        return success_response(schema.dump(doctor))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/license/<license_number>', methods=['GET'])
def get_doctor_by_license(license_number):
    """
    Get doctor by license number
    ---
    tags:
      - Doctor
    parameters:
      - name: license_number
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Doctor found
      404:
        description: Doctor not found
    """
    try:
        # Call SERVICE ✅
        doctor = doctor_service.get_doctor_by_license(license_number)
        if not doctor:
            return not_found_response('Doctor not found')
        
        # Serialize response with schema
        schema = DoctorProfileResponseSchema()
        return success_response(schema.dump(doctor))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/specialization/<specialization>', methods=['GET'])
def get_doctors_by_specialization(specialization):
    """
    Get doctors by specialization
    ---
    tags:
      - Doctor
    parameters:
      - name: specialization
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of doctors
    """
    try:
        # Call SERVICE ✅
        doctors = doctor_service.search_by_specialization(specialization)
        
        # Serialize response with schema
        schema = DoctorProfileResponseSchema(many=True)
        return success_response({
            'count': len(doctors),
            'doctors': schema.dump(doctors)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/search', methods=['GET'])
def search_doctors():
    """
    Search doctors by name
    ---
    tags:
      - Doctor
    parameters:
      - name: name
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of doctors
    """
    try:
        name = request.args.get('name', '')
        if not name:
            return validation_error_response({'name': 'Name parameter is required'})
        
        # Call SERVICE ✅
        doctors = doctor_service.search_doctors_by_name(name)
        
        # Serialize response with schema
        schema = DoctorProfileResponseSchema(many=True)
        return success_response({
            'count': len(doctors),
            'doctors': schema.dump(doctors)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('', methods=['GET'])
def get_all_doctors():
    """
    Get all doctors
    ---
    tags:
      - Doctor
    responses:
      200:
        description: List of all doctors
    """
    try:
        # Call SERVICE ✅
        doctors = doctor_service.list_all_doctors()
        
        # Serialize response with schema
        schema = DoctorProfileResponseSchema(many=True)
        return success_response({
            'count': len(doctors),
            'doctors': schema.dump(doctors)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    """
    Update doctor profile
    ---
    tags:
      - Doctor
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: doctor_id
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
            doctor_name:
              type: string
              example: "Dr. John Smith"
            specialization:
              type: string
              example: "Ophthalmology"
            license_number:
              type: string
              example: "MD12345"
    responses:
      200:
        description: Doctor updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Doctor updated successfully
            data:
              type: object
      404:
        description: Doctor not found
    """
    try:
        # Validate request data with schema
        schema = DoctorProfileUpdateRequestSchema()
        data = schema.load(request.get_json())
        
        # Call SERVICE ✅
        doctor = doctor_service.update_doctor(doctor_id, **data)
        if not doctor:
            return not_found_response('Doctor not found')
        
        # Serialize response with schema
        response_schema = DoctorProfileResponseSchema()
        return success_response(response_schema.dump(doctor), 'Doctor updated successfully')
        
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


@doctor_bp.route('/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    """
    Delete doctor
    ---
    tags:
      - Doctor
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Doctor deleted successfully
      404:
        description: Doctor not found
      409:
        description: Cannot delete doctor due to foreign key constraints (has associated records)
    """
    try:
        # Call SERVICE ✅
        result = doctor_service.delete_doctor(doctor_id)
        if not result:
            return not_found_response('Doctor not found')
        
        return success_response(None, 'Doctor deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        error_msg = str(e)
        # Check if it's a Foreign Key constraint error
        if 'REFERENCE constraint' in error_msg or 'Foreign Key' in error_msg:
            # Extract table name from error message
            if 'conversations' in error_msg:
                return error_response(
                    'Cannot delete doctor: This doctor has associated conversations. Please delete or reassign conversations first.',
                    409  # Conflict status code
                )
            elif 'doctor_reviews' in error_msg:
                return error_response(
                    'Cannot delete doctor: This doctor has associated reviews. Please delete or reassign reviews first.',
                    409
                )
            elif 'medical_reports' in error_msg:
                return error_response(
                    'Cannot delete doctor: This doctor has associated medical reports. Please delete or reassign reports first.',
                    409
                )
            else:
                return error_response(
                    'Cannot delete doctor: This doctor has associated records in the system. Please remove all related records first.',
                    409
                )
        return error_response(f'Error deleting doctor: {error_msg}', 500)


@doctor_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get doctor statistics
    ---
    tags:
      - Doctor
    responses:
      200:
        description: Doctor statistics
    """
    try:
        # Call SERVICE ✅
        total = doctor_service.count_doctors()
        all_doctors = doctor_service.list_all_doctors()
        
        # Group by specialization
        specialization_counts = {}
        for doctor in all_doctors:
            spec = doctor.specialization or 'Unknown'
            specialization_counts[spec] = specialization_counts.get(spec, 0) + 1
        
        stats = {
            'total_doctors': total,
            'by_specialization': specialization_counts
        }
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/validate-license', methods=['POST'])
def validate_license():
    """
    Validate license number
    ---
    tags:
      - Doctor
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
            - license_number
          properties:
            license_number:
              type: string
              example: "DR12345"
    responses:
      200:
        description: License validation result
        schema:
          type: object
          properties:
            license_number:
              type: string
            is_valid:
              type: boolean
            message:
              type: string
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        license_number = data.get('license_number')
        
        if not license_number:
            return validation_error_response({'license_number': 'License number is required'})
        
        # Call SERVICE ✅
        is_valid = doctor_service.validate_license(license_number)
        
        return success_response({
            'license_number': license_number,
            'is_valid': is_valid,
            'message': 'License is valid and available' if is_valid else 'License is invalid or already exists'
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@doctor_bp.route('/<int:doctor_id>/performance', methods=['GET'])
def get_doctor_performance(doctor_id):
    """
    Get performance summary for a doctor (FR-21)
    ---
    tags:
      - Doctor
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Doctor performance summary
        schema:
          type: object
          properties:
            doctor_id:
              type: integer
            doctor_name:
              type: string
            specialization:
              type: string
            total_reviews:
              type: integer
            approved_reviews:
              type: integer
            approval_rate:
              type: number
            total_reports:
              type: integer
            unique_patients:
              type: integer
            performance_score:
              type: number
    """
    try:
        # Call SERVICE ✅
        performance = doctor_service.get_performance_summary(doctor_id)
        
        return success_response(performance, 'Performance summary retrieved successfully')
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)
