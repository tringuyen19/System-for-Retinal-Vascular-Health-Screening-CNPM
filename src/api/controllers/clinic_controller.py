from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.clinic_repository import ClinicRepository
from infrastructure.databases.mssql import session
from services.clinic_service import ClinicService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import ClinicCreateRequestSchema, ClinicUpdateRequestSchema, ClinicResponseSchema

clinic_bp = Blueprint('clinic', __name__, url_prefix='/api/clinics')

# Initialize repository (only for service initialization)
clinic_repo = ClinicRepository(session)

# Initialize SERVICE (Business Logic Layer) ✅
clinic_service = ClinicService(clinic_repo)


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
            'clinics': [{
                'clinic_id': c.clinic_id,
                'clinic_name': c.clinic_name,
                'address': c.address,
                'phone_number': c.phone_number,
                'logo_url': c.logo_url,
                'description': c.description
            } for c in clinics]
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
            'clinics': [{
                'clinic_id': c.clinic_id,
                'clinic_name': c.clinic_name,
                'address': c.address,
                'phone_number': c.phone_number,
                'description': c.description
            } for c in clinics]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/verify', methods=['PUT'])
def verify_clinic(clinic_id):
    """
    Verify clinic (Admin only)
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
        description: Clinic verified successfully
      404:
        description: Clinic not found
    """
    try:
        # Call SERVICE ✅
        clinic = clinic_service.verify_clinic(clinic_id)
        if not clinic:
            return not_found_response('Clinic not found')
        
        return success_response({
            'clinic_id': clinic.clinic_id,
            'clinic_name': clinic.clinic_name,
            'verification_status': clinic.verification_status
        }, 'Clinic verified successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@clinic_bp.route('/<int:clinic_id>/reject', methods=['PUT'])
def reject_clinic(clinic_id):
    """
    Reject clinic verification (Admin only)
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
        description: Clinic rejected successfully
      404:
        description: Clinic not found
    """
    try:
        # Call SERVICE ✅
        clinic = clinic_service.reject_clinic(clinic_id)
        if not clinic:
            return not_found_response('Clinic not found')
        
        return success_response({
            'clinic_id': clinic.clinic_id,
            'clinic_name': clinic.clinic_name,
            'verification_status': clinic.verification_status
        }, 'Clinic verification rejected')
        
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
        
        return success_response({
            'clinic_id': clinic.clinic_id,
            'clinic_name': clinic.clinic_name,
            'address': clinic.address,
            'phone_number': clinic.phone_number,
            'logo_url': clinic.logo_url,
            'description': clinic.description,
            'verification_status': clinic.verification_status
        }, 'Clinic updated successfully')
        
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

