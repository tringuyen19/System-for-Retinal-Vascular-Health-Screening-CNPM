from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.databases.mssql import session
from services.patient_profile_service import PatientProfileService
from services.account_service import AccountService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import PatientProfileCreateRequestSchema, PatientProfileUpdateRequestSchema, PatientProfileResponseSchema
from domain.exceptions import NotFoundException, ValidationException
from datetime import date

patient_bp = Blueprint('patient', __name__, url_prefix='/api/patients')

# Initialize repositories (only for service initialization)
patient_repo = PatientProfileRepository(session)
account_repo = AccountRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
patient_service = PatientProfileService(patient_repo)
account_service = AccountService(account_repo)


@patient_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Patient
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Patient service is running")


@patient_bp.route('', methods=['POST'])
def create_patient():
    """
    Create a new patient profile
    ---
    tags:
      - Patient
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
            - patient_name
          properties:
            account_id:
              type: integer
              example: 1
            patient_name:
              type: string
              example: "Nguyen Van A"
            date_of_birth:
              type: string
              format: date
              example: "1990-01-15"
            gender:
              type: string
              enum: [male, female, other, prefer_not_to_say]
              example: "male"
            medical_history:
              type: string
              example: "No known allergies"
    responses:
      201:
        description: Patient created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Patient created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate request data with schema
        schema = PatientProfileCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Check if account exists via SERVICE ✅
        account = account_service.get_account_by_id(data['account_id'])
        if not account:
            return not_found_response('Account not found')
        
        # STEP 3: Call SERVICE ✅
        patient = patient_service.create_patient(
            account_id=data['account_id'],
            patient_name=data['patient_name'],
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            medical_history=data.get('medical_history')
        )
        
        # STEP 4: Serialize response with schema
        response_schema = PatientProfileResponseSchema()
        return success_response(response_schema.dump(patient), 'Patient created successfully', 201)
        
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


@patient_bp.route('/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """
    Get patient by ID
    ---
    tags:
      - Patient
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Patient found
      404:
        description: Patient not found
    """
    try:
        # Call SERVICE ✅
        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            return not_found_response('Patient not found')
        
        # Serialize response with schema
        schema = PatientProfileResponseSchema()
        return success_response(schema.dump(patient))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('/account/<int:account_id>', methods=['GET'])
def get_patient_by_account(account_id):
    """
    Get patient by account ID
    ---
    tags:
      - Patient
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Patient found
      404:
        description: Patient not found
    """
    try:
        # Call SERVICE ✅
        patient = patient_service.get_patient_by_account(account_id)
        if not patient:
            return not_found_response('Patient not found')
        
        # Serialize response with schema
        schema = PatientProfileResponseSchema()
        return success_response(schema.dump(patient))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('/search', methods=['GET'])
def search_patients():
    """
    Search and filter patients (FR-18)
    ---
    tags:
      - Patient
    parameters:
      - name: name
        in: query
        required: false
        schema:
          type: string
        description: Patient name (partial match)
      - name: clinic_id
        in: query
        required: false
        schema:
          type: integer
        description: Filter by clinic ID
      - name: risk_level
        in: query
        required: false
        schema:
          type: string
          enum: [low, medium, high, critical]
        description: Filter by risk level
    responses:
      200:
        description: List of filtered patients
        schema:
          type: object
          properties:
            count:
              type: integer
            patients:
              type: array
    """
    try:
        name = request.args.get('name', None)
        clinic_id = request.args.get('clinic_id', type=int)
        risk_level = request.args.get('risk_level', None)
        
        # Call SERVICE ✅
        patients = patient_service.search_patients(
            name=name,
            clinic_id=clinic_id,
            risk_level=risk_level
        )
        
        # Serialize response with schema
        schema = PatientProfileResponseSchema(many=True)
        return success_response({
            'count': len(patients),
            'patients': schema.dump(patients)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('/assigned/clinic/<int:clinic_id>', methods=['GET'])
def get_assigned_patients(clinic_id):
    """
    Get patients assigned to a clinic (FR-13)
    ---
    tags:
      - Patient
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of assigned patients
    """
    try:
        # Call SERVICE ✅
        patients = patient_service.get_assigned_patients_by_clinic(clinic_id)
        
        # Serialize response with schema
        schema = PatientProfileResponseSchema(many=True)
        return success_response({
            'clinic_id': clinic_id,
            'count': len(patients),
            'patients': schema.dump(patients)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('', methods=['GET'])
def get_all_patients():
    """
    Get all patients
    ---
    tags:
      - Patient
    responses:
      200:
        description: List of all patients
    """
    try:
        # Call SERVICE ✅
        patients = patient_service.list_all_patients()
        
        # Serialize response with schema
        schema = PatientProfileResponseSchema(many=True)
        return success_response({
            'count': len(patients),
            'patients': schema.dump(patients)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """
    Update patient profile
    ---
    tags:
      - Patient
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: patient_id
        in: path
        required: true
        type: integer
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            patient_name:
              type: string
              example: "Nguyen Van B"
            date_of_birth:
              type: string
              format: date
              example: "1990-01-15"
            gender:
              type: string
              enum: [male, female, other, prefer_not_to_say]
              example: "male"
            medical_history:
              type: string
              example: "Updated medical history"
    responses:
      200:
        description: Patient updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Patient updated successfully
            data:
              type: object
      400:
        description: Invalid input
      404:
        description: Patient not found
    """
    try:
        # Validate request data with schema
        schema = PatientProfileUpdateRequestSchema()
        data = schema.load(request.get_json())
        
        # Call SERVICE ✅
        patient = patient_service.update_patient(patient_id, **data)
        if not patient:
            return not_found_response('Patient not found')
        
        # Serialize response with schema
        response_schema = PatientProfileResponseSchema()
        return success_response(response_schema.dump(patient), 'Patient updated successfully')
        
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


@patient_bp.route('/<int:patient_id>/medical-history', methods=['PUT'])
def update_medical_history(patient_id):
    """
    Update patient medical history
    ---
    tags:
      - Patient
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: patient_id
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
            - medical_history
          properties:
            medical_history:
              type: string
              example: "Updated medical history: Diabetes type 2, hypertension"
    responses:
      200:
        description: Medical history updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Medical history updated successfully
            data:
              type: object
      400:
        description: Medical history is required
      404:
        description: Patient not found
    """
    try:
        data = request.get_json()
        if not data.get('medical_history'):
            return validation_error_response({'medical_history': 'Medical history is required'})
        
        # Call SERVICE ✅
        patient = patient_service.update_medical_history(patient_id, data['medical_history'])
        if not patient:
            return not_found_response('Patient not found')
        
        return success_response({
            'patient_id': patient.patient_id,
            'medical_history': patient.medical_history
        }, 'Medical history updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """
    Delete patient
    ---
    tags:
      - Patient
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Patient deleted successfully
      404:
        description: Patient not found
    """
    try:
        # Call SERVICE ✅
        result = patient_service.delete_patient(patient_id)
        if not result:
            return not_found_response('Patient not found')
        
        return success_response(None, 'Patient deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@patient_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get patient statistics
    ---
    tags:
      - Patient
    responses:
      200:
        description: Patient statistics
    """
    try:
        # Call SERVICE ✅
        stats = patient_service.get_patient_statistics()
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)





