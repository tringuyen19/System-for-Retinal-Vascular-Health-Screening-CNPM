from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.clinic_repository import ClinicRepository
from infrastructure.databases.mssql import session
from services.retinal_image_service import RetinalImageService
from services.patient_profile_service import PatientProfileService
from services.clinic_service import ClinicService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import RetinalImageCreateRequestSchema, RetinalImageUpdateRequestSchema, RetinalImageResponseSchema, RetinalImageBulkCreateRequestSchema

retinal_image_bp = Blueprint('retinal_image', __name__, url_prefix='/api/retinal-images')

# Initialize repositories (only for service initialization)
image_repo = RetinalImageRepository(session)
patient_repo = PatientProfileRepository(session)
clinic_repo = ClinicRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
image_service = RetinalImageService(image_repo)
patient_service = PatientProfileService(patient_repo)
clinic_service = ClinicService(clinic_repo)


@retinal_image_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Retinal Image
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Retinal image service is running")


@retinal_image_bp.route('', methods=['POST'])
def upload_image():
    """
    Upload a new retinal image
    ---
    tags:
      - Retinal Image
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
            - patient_id
            - clinic_id
            - uploaded_by
            - image_type
            - eye_side
            - image_url
          properties:
            patient_id:
              type: integer
              example: 1
            clinic_id:
              type: integer
              example: 1
            uploaded_by:
              type: integer
              example: 1
              description: Account ID (account_id) của người upload ảnh (lấy từ bảng accounts)
            image_type:
              type: string
              enum: [fundus, oct, fluorescein]
              example: fundus
            eye_side:
              type: string
              enum: [left, right, both]
              example: left
            image_url:
              type: string
              example: https://example.com/image.jpg
            status:
              type: string
              example: uploaded
    responses:
      201:
        description: Image uploaded successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Image uploaded successfully
            data:
              type: object
      400:
        description: Invalid input
      404:
        description: Patient or clinic not found
    """
    try:
        # Validate request data with schema
        schema = RetinalImageCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # Validate patient exists (via SERVICE) ✅
        patient = patient_service.get_patient_by_id(data['patient_id'])
        if not patient:
            return not_found_response('Patient not found')
        
        # Validate clinic exists (via SERVICE) ✅
        clinic = clinic_service.get_clinic_by_id(data['clinic_id'])
        if not clinic:
            return not_found_response('Clinic not found')
        
        # Upload image
        image = image_service.upload_image(
            patient_id=data['patient_id'],
            clinic_id=data['clinic_id'],
            uploaded_by=data['uploaded_by'],
            image_type=data['image_type'],
            eye_side=data['eye_side'],
            image_url=data['image_url'],
            status=data.get('status', 'uploaded')
        )
        
        # Serialize response with schema
        response_schema = RetinalImageResponseSchema()
        return success_response(response_schema.dump(image), 'Image uploaded successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/bulk', methods=['POST'])
def upload_bulk_images():
    """
    Upload multiple retinal images in bulk with batch tracking (FR-24)
    ---
    tags:
      - Retinal Images
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
            - images
          properties:
            images:
              type: array
              items:
                type: object
                required:
                  - patient_id
                  - clinic_id
                  - uploaded_by
                  - image_type
                  - eye_side
                  - image_url
                properties:
                  patient_id:
                    type: integer
                    example: 1
                  clinic_id:
                    type: integer
                    example: 1
                  uploaded_by:
                    type: integer
                    example: 1
                    description: Account ID (account_id) của người upload ảnh (lấy từ bảng accounts)
                  image_type:
                    type: string
                    enum: [fundus, oct, fluorescein]
                    example: fundus
                  eye_side:
                    type: string
                    enum: [left, right, both]
                    example: left
                  image_url:
                    type: string
                    example: https://example.com/image1.jpg
                  status:
                    type: string
                    example: uploaded
    responses:
      201:
        description: Bulk upload completed
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Bulk upload completed: 3 successful, 0 failed"
            data:
              type: object
              properties:
                uploaded:
                  type: array
                  items:
                    type: object
                    properties:
                      image_id:
                        type: integer
                      patient_id:
                        type: integer
                      clinic_id:
                        type: integer
                      image_type:
                        type: string
                      eye_side:
                        type: string
                      image_url:
                        type: string
                      status:
                        type: string
                      upload_time:
                        type: string
                errors:
                  type: array
                  items:
                    type: object
                    properties:
                      image_url:
                        type: string
                      error:
                        type: string
               batch_id:
                  type: string
                  example: "batch_abc123_1234567890"
                  description: Batch ID for tracking this upload
                batch_status:
                  type: string
                  enum: [completed, partial, failed]
                  example: "completed"
                  description: Status of the batch upload
                total:
                  type: integer
                  example: 3
                success_count:
                  type: integer
                  example: 3
                error_count:
                  type: integer
                  example: 0
                created_at:
                  type: string
                  format: date-time
                  example: "2024-01-15T10:30:00"
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Validation errors"
            errors:
              type: object
    """
    try:
        # Validate request data
        schema = RetinalImageBulkCreateRequestSchema()
        data = schema.load(request.get_json())
        
        if not data.get('images') or len(data['images']) == 0:
            return error_response('No images provided', 400)
        
        # Validate all patients and clinics exist before processing
        # Collect all validation errors and valid images separately
        validation_errors = []
        images_data = []
        
        for idx, img in enumerate(data['images']):
            image_url = img.get("image_url", f"image_{idx + 1}")
            is_valid = True
            
            # Validate patient exists
            patient = patient_service.get_patient_by_id(img['patient_id'])
            if not patient:
                validation_errors.append({
                    'image_url': image_url,
                    'error': f'Patient with ID {img["patient_id"]} not found'
                })
                is_valid = False
            
            # Validate clinic exists
            if is_valid:
                clinic = clinic_service.get_clinic_by_id(img['clinic_id'])
                if not clinic:
                    validation_errors.append({
                        'image_url': image_url,
                        'error': f'Clinic with ID {img["clinic_id"]} not found'
                    })
                    is_valid = False
            
            # Only add valid images to images_data
            if is_valid:
                images_data.append({
                    'patient_id': img['patient_id'],
                    'clinic_id': img['clinic_id'],
                    'uploaded_by': img['uploaded_by'],
                    'image_type': img['image_type'],
                    'eye_side': img['eye_side'],
                    'image_url': img['image_url'],
                    'status': img.get('status', 'uploaded')
                })
        
        # If all images have validation errors, return errors
        if len(validation_errors) == len(data['images']):
            return jsonify({
                'message': 'All images failed validation',
                'errors': validation_errors,
                'total_images': len(data['images']),
                'failed_count': len(validation_errors)
            }), 400
        
        # If some images have errors but some are valid, proceed with valid ones
        # (Errors will be included in the final response from service)
        
       # Get optional batch_id from request
        batch_id = data.get('batch_id')
        
        # Upload bulk images (only valid ones) with batch tracking
        result = image_service.upload_bulk_images(images_data, batch_id=batch_id)
        
        # Merge validation errors from controller with service errors
        all_errors = validation_errors.copy()
        for service_error in result['errors']:
            # Service errors might have different format, add them as-is
            if isinstance(service_error, dict):
                all_errors.append(service_error)
            else:
                all_errors.append({'error': str(service_error)})
        
        # Serialize successful uploads
        response_schema = RetinalImageResponseSchema()
        serialized_uploaded = [response_schema.dump(img) for img in result['uploaded']]
        
        # Calculate total counts including validation errors
        total_error_count = len(all_errors)
        total_success_count = result['success_count']
        total_images = len(data['images'])
        
        response_data = {
            'batch_id': result['batch_id'],
            'batch_status': result['batch_status'],
            'uploaded': serialized_uploaded,
            'errors': all_errors,
            'total': total_images,
            'success_count': total_success_count,
            'error_count': total_error_count,
            'created_at': result['created_at']
        }
        
        message = f"Bulk upload completed: {total_success_count} successful, {total_error_count} failed. Batch ID: {result['batch_id']}"
        return success_response(response_data, message, 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>', methods=['GET'])
def get_image(image_id):
    """
    Get retinal image by ID
    ---
    tags:
      - Retinal Image
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Image found
      404:
        description: Image not found
    """
    try:
        image = image_service.get_image_by_id(image_id)
        if not image:
            return not_found_response('Image not found')
        
        # Serialize response with schema
        schema = RetinalImageResponseSchema()
        return success_response(schema.dump(image))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_images_by_patient(patient_id):
    """
    Get all images for a patient
    ---
    tags:
      - Retinal Image
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
      - name: eye_side
        in: query
        required: false
        schema:
          type: string
          enum: [left, right, both]
    responses:
      200:
        description: List of images
    """
    try:
        eye_side = request.args.get('eye_side')
        
        # Get all images for patient
        images = image_service.get_images_by_patient(patient_id)
        
        # Filter by eye_side if provided
        if eye_side:
            images = [img for img in images if img.eye_side == eye_side]
        
        return success_response({
            'count': len(images),
            'images': RetinalImageResponseSchema(many=True).dump(images)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/clinic/<int:clinic_id>', methods=['GET'])
def get_images_by_clinic(clinic_id):
    """
    Get all images uploaded by a clinic
    ---
    tags:
      - Retinal Image
    parameters:
      - name: clinic_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of images
    """
    try:
        images = image_service.get_images_by_clinic(clinic_id)
        
        return success_response({
            'count': len(images),
            'images': [{
                'image_id': img.image_id,
                'patient_id': img.patient_id,
                'image_type': img.image_type,
                'eye_side': img.eye_side,
                'status': img.status,
                'upload_time': img.upload_time.isoformat() if img.upload_time else None
            } for img in images]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/status/<status>', methods=['GET'])
def get_images_by_status(status):
    """
    Get images by status
    ---
    tags:
      - Retinal Image
    parameters:
      - name: status
        in: path
        required: true
        schema:
          type: string
          enum: [uploaded, processing, analyzed, error]
    responses:
      200:
        description: List of images
    """
    try:
        images = image_service.get_images_by_status(status)
        
        return success_response({
            'status': status,
            'count': len(images),
            'images': [{
                'image_id': img.image_id,
                'patient_id': img.patient_id,
                'clinic_id': img.clinic_id,
                'image_type': img.image_type,
                'eye_side': img.eye_side,
                'upload_time': img.upload_time.isoformat() if img.upload_time else None
            } for img in images]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/pending-analysis', methods=['GET'])
def get_pending_analysis():
    """
    Get images pending AI analysis
    ---
    tags:
      - Retinal Image
    responses:
      200:
        description: List of images pending analysis
    """
    try:
        images = image_service.get_pending_analysis()
        
        return success_response({
            'count': len(images),
            'images': [{
                'image_id': img.image_id,
                'patient_id': img.patient_id,
                'clinic_id': img.clinic_id,
                'image_type': img.image_type,
                'eye_side': img.eye_side,
                'image_url': img.image_url,
                'upload_time': img.upload_time.isoformat() if img.upload_time else None
            } for img in images]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>/processing', methods=['PUT'])
def mark_as_processing(image_id):
    """
    Mark image as processing
    ---
    tags:
      - Retinal Image
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Image marked as processing
      404:
        description: Image not found
    """
    try:
        image = image_service.mark_as_processing(image_id)
        if not image:
            return not_found_response('Image not found')
        
        return success_response({
            'image_id': image.image_id,
            'status': image.status
        }, 'Image marked as processing')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>/analyzed', methods=['PUT'])
def mark_as_analyzed(image_id):
    """
    Mark image as analyzed
    ---
    tags:
      - Retinal Image
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Image marked as analyzed
      404:
        description: Image not found
    """
    try:
        image = image_service.mark_as_analyzed(image_id)
        if not image:
            return not_found_response('Image not found')
        
        return success_response({
            'image_id': image.image_id,
            'status': image.status
        }, 'Image marked as analyzed')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>/error', methods=['PUT'])
def mark_as_error(image_id):
    """
    Mark image as error
    ---
    tags:
      - Retinal Image
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Image marked as error
      404:
        description: Image not found
    """
    try:
        image = image_service.mark_as_error(image_id)
        if not image:
            return not_found_response('Image not found')
        
        return success_response({
            'image_id': image.image_id,
            'status': image.status
        }, 'Image marked as error')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>', methods=['PUT'])
def update_image(image_id):
    """
    Update image information
    ---
    tags:
      - Retinal Image
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: image_id
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
            status:
              type: string
              enum: [uploaded, processing, analyzed, error]
              example: "processed"
    responses:
      200:
        description: Image updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Image updated successfully
            data:
              type: object
      404:
        description: Image not found
    """
    try:
        data = request.get_json()
        
        image = image_service.update_image(image_id, **data)
        if not image:
            return not_found_response('Image not found')
        
        # Use schema for response serialization
        response_schema = RetinalImageResponseSchema()
        return success_response(response_schema.dump(image), 'Image updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """
    Delete retinal image
    ---
    tags:
      - Retinal Image
    parameters:
      - name: image_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Image deleted successfully
      404:
        description: Image not found
    """
    try:
        result = image_service.delete_image(image_id)
        if not result:
            return not_found_response('Image not found')
        
        return success_response(None, 'Image deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get image statistics
    ---
    tags:
      - Retinal Image
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
      - name: patient_id
        in: query
        required: false
        schema:
          type: integer
    responses:
      200:
        description: Image statistics
    """
    try:
        status = request.args.get('status')
        patient_id = request.args.get('patient_id', type=int)
        
        if patient_id:
            count = image_service.count_by_patient(patient_id)
            return success_response({
                'patient_id': patient_id,
                'total_images': count
            })
        elif status:
            count = image_service.count_by_status(status)
            return success_response({
                'status': status,
                'count': count
            })
        else:
            stats = image_service.get_image_statistics()
            
            return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

