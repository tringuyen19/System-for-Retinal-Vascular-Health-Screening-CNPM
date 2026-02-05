from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import random
from api.middleware.auth_middleware import require_roles, require_role
from infrastructure.repositories.retinal_image_repository import RetinalImageRepository
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.clinic_repository import ClinicRepository
from infrastructure.repositories.subscription_repository import SubscriptionRepository
from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
from infrastructure.repositories.ai_model_version_repository import AiModelVersionRepository
from infrastructure.databases.mssql import session
from services.retinal_image_service import RetinalImageService
from services.patient_profile_service import PatientProfileService
from services.clinic_service import ClinicService
from services.subscription_service import SubscriptionService
from services.ai_analysis_service import AiAnalysisService
from services.ai_model_version_service import AiModelVersionService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import RetinalImageCreateRequestSchema, RetinalImageUpdateRequestSchema, RetinalImageResponseSchema, RetinalImageBulkCreateRequestSchema
from domain.exceptions import BusinessRuleException
from config import Config

retinal_image_bp = Blueprint('retinal_image', __name__, url_prefix='/api/retinal-images')

# Initialize repositories (only for service initialization)
image_repo = RetinalImageRepository(session)
patient_repo = PatientProfileRepository(session)
clinic_repo = ClinicRepository(session)
subscription_repo = SubscriptionRepository(session)
analysis_repo = AiAnalysisRepository(session)
model_version_repo = AiModelVersionRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
image_service = RetinalImageService(image_repo)
patient_service = PatientProfileService(patient_repo)
clinic_service = ClinicService(clinic_repo)
subscription_service = SubscriptionService(subscription_repo)
analysis_service = AiAnalysisService(analysis_repo)
model_version_service = AiModelVersionService(model_version_repo)


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
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def upload_image():
    """
    Upload a new retinal image
    ---
    tags:
      - Retinal Image
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
        
        # FR-11/12: Trừ 1 credit khi upload. remaining = tổng image_limit các gói đã mua - số lần đã up ảnh.
        account_id = data['uploaded_by']
        if subscription_service.get_remaining_credits(account_id) < 1:
            return error_response('Hết lượt phân tích. Vui lòng mua thêm gói.', 402)
        try:
            updated = subscription_service.deduct_credit_for_account(account_id, 1)
            if not updated:
                return error_response('Hết lượt phân tích. Vui lòng mua thêm gói.', 402)
        except BusinessRuleException as e:
            return error_response(str(e) or 'Hết lượt phân tích. Vui lòng mua thêm gói.', 402)
        
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
        
        # Auto-trigger AI analysis: Cách 2 (Kaggle) = pending chờ submit-kaggle-result; mặc định = completed + mock
        analysis_id = None
        try:
            active_model = model_version_service.get_active_model()
            if active_model:
                use_kaggle = getattr(Config, 'AI_RESULT_SOURCE', '') == 'kaggle'
                if use_kaggle:
                    analysis = analysis_service.create_analysis(
                        image_id=image.image_id,
                        ai_model_version_id=active_model.ai_model_version_id,
                        status='pending',
                        processing_time=None
                    )
                else:
                    processing_time = random.randint(1, 20)
                    analysis = analysis_service.create_analysis(
                        image_id=image.image_id,
                        ai_model_version_id=active_model.ai_model_version_id,
                        status='completed',
                        processing_time=processing_time
                    )
                if analysis:
                    analysis_id = analysis.analysis_id
        except Exception as e:
            pass
        
        # Serialize response with schema
        response_schema = RetinalImageResponseSchema()
        response_data = response_schema.dump(image)
        if analysis_id:
            response_data['analysis_id'] = analysis_id
        
        return success_response(response_data, 'Image uploaded successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/upload-for-ai', methods=['POST'])
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def upload_for_ai():
    """
    Upload ảnh võng mạc (file) lên Cloudinary và tạo bản ghi + AI analysis pending (Cách 2: Kaggle).
    Multipart: file, patient_id, clinic_id, uploaded_by, image_type, eye_side.
    Trả về image_url (Cloudinary) để dùng trong Kaggle notebook.
    """
    try:
        if 'file' not in request.files:
            return error_response('Thiếu file. Gửi multipart/form-data với field "file".', 400)
        f = request.files['file']
        if not f or not f.filename:
            return error_response('File trống.', 400)
        patient_id = request.form.get('patient_id', type=int)
        clinic_id = request.form.get('clinic_id', type=int)
        uploaded_by = request.form.get('uploaded_by', type=int)
        image_type = (request.form.get('image_type') or 'fundus').strip().lower()
        eye_side = (request.form.get('eye_side') or 'left').strip().lower()
        if not all([patient_id, clinic_id, uploaded_by]):
            return error_response('Thiếu patient_id, clinic_id hoặc uploaded_by.', 400)
        if image_type not in ('fundus', 'oct', 'fluorescein'):
            return error_response('image_type phải là fundus, oct hoặc fluorescein.', 400)
        if eye_side not in ('left', 'right', 'both'):
            return error_response('eye_side phải là left, right hoặc both.', 400)

        patient = patient_service.get_patient_by_id(patient_id)
        if not patient:
            return not_found_response('Patient not found')
        clinic = clinic_service.get_clinic_by_id(clinic_id)
        if not clinic:
            return not_found_response('Clinic not found')
        if subscription_service.get_remaining_credits(uploaded_by) < 1:
            return error_response('Hết lượt phân tích. Vui lòng mua thêm gói.', 402)
        try:
            subscription_service.deduct_credit_for_account(uploaded_by, 1)
        except BusinessRuleException as e:
            return error_response(str(e) or 'Hết lượt phân tích.', 402)

        from infrastructure.services.cloudinary_service import upload_image as cloudinary_upload, is_cloudinary_configured
        if not is_cloudinary_configured():
            return error_response('Cloudinary chưa cấu hình. Đặt CLOUDINARY_* trong .env.', 503)
        cloudinary_url = cloudinary_upload(f, folder='retina_input')

        image = image_service.upload_image(
            patient_id=patient_id,
            clinic_id=clinic_id,
            uploaded_by=uploaded_by,
            image_type=image_type,
            eye_side=eye_side,
            image_url=cloudinary_url,
            status='uploaded'
        )

        analysis_id = None
        try:
            active_model = model_version_service.get_active_model()
            if active_model:
                use_kaggle = getattr(Config, 'AI_RESULT_SOURCE', '') == 'kaggle'
                status = 'pending' if use_kaggle else 'completed'
                processing_time = None if use_kaggle else random.randint(1, 20)
                analysis = analysis_service.create_analysis(
                    image_id=image.image_id,
                    ai_model_version_id=active_model.ai_model_version_id,
                    status=status,
                    processing_time=processing_time
                )
                if analysis:
                    analysis_id = analysis.analysis_id
        except Exception:
            pass

        return success_response({
            'image_id': image.image_id,
            'analysis_id': analysis_id,
            'image_url': cloudinary_url,
            'message': 'Upload lên Cloudinary thành công. Dùng image_url trong Kaggle notebook, sau đó gọi submit-kaggle-result.'
        }, 'Upload for AI (Kaggle) thành công', 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Lỗi: {str(e)}', 500)


@retinal_image_bp.route('/bulk', methods=['POST'])
@require_roles(['Doctor', 'Admin', 'ClinicManager'])
def upload_bulk_images():
    """
    Upload multiple retinal images in bulk with batch tracking (FR-24)
    ---
    tags:
      - Retinal Images
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
        
        # FR-24: Check credits for all valid images before processing
        # Group images by uploaded_by to check credits per account
        account_credits_needed = {}
        for img_data in images_data:
            account_id = img_data['uploaded_by']
            account_credits_needed[account_id] = account_credits_needed.get(account_id, 0) + 1
        
        # Check if all accounts have sufficient credits
        credit_check_errors = []
        accounts_with_insufficient_credits = set()
        for account_id, credits_needed in account_credits_needed.items():
            remaining = subscription_service.get_remaining_credits(account_id)
            if remaining < credits_needed:
                accounts_with_insufficient_credits.add(account_id)
                credit_check_errors.append({
                    'account_id': account_id,
                    'error': f'Insufficient credits. Required: {credits_needed}, Available: {remaining}'
                })
        
        # Filter out images from accounts with insufficient credits
        if accounts_with_insufficient_credits:
            filtered_images_data = []
            for img_data in images_data:
                if img_data['uploaded_by'] in accounts_with_insufficient_credits:
                    credit_check_errors.append({
                        'image_url': img_data.get('image_url', 'unknown'),
                        'error': f'Account {img_data["uploaded_by"]} has insufficient credits'
                    })
                else:
                    filtered_images_data.append(img_data)
            images_data = filtered_images_data
        
        # If no valid images remain after credit check, return errors
        if not images_data:
            all_errors = validation_errors + credit_check_errors
            return jsonify({
                'message': 'All images failed validation or have insufficient credits',
                'errors': all_errors,
                'total_images': len(data['images']),
                'failed_count': len(all_errors)
            }), 400
        
        # Get optional batch_id from request
        batch_id = data.get('batch_id')
        
        # FR-24: Upload bulk images with credit deduction and auto-trigger AI analysis
        uploaded_images = []
        upload_errors = []
        analysis_created = []
        analysis_errors = []
        
        # Get active AI model for auto-analysis
        active_model = model_version_service.get_active_model()
        auto_analyze = active_model is not None
        
        for img_data in images_data:
            account_id = img_data['uploaded_by']
            image_url = img_data.get('image_url', 'unknown')
            
            try:
                # FR-11/12: Deduct credit before uploading
                try:
                    updated = subscription_service.deduct_credit_for_account(account_id, 1)
                    if not updated:
                        upload_errors.append({
                            'image_url': image_url,
                            'error': 'Hết lượt phân tích. Vui lòng mua thêm gói.'
                        })
                        continue
                except BusinessRuleException as e:
                    upload_errors.append({
                        'image_url': image_url,
                        'error': str(e) or 'Hết lượt phân tích. Vui lòng mua thêm gói.'
                    })
                    continue
                
                # Upload image using service
                image = image_service.upload_image(
                    patient_id=img_data['patient_id'],
                    clinic_id=img_data['clinic_id'],
                    uploaded_by=img_data['uploaded_by'],
                    image_type=img_data['image_type'],
                    eye_side=img_data['eye_side'],
                    image_url=img_data['image_url'],
                    status=img_data.get('status', 'uploaded')
                )
                
                if image:
                    uploaded_images.append(image)
                    
                    # FR-24: Auto-trigger AI analysis if active model exists
                    if auto_analyze:
                        try:
                            # Generate random processing time (1-20 seconds)
                            processing_time = random.randint(1, 20)
                            analysis = analysis_service.create_analysis(
                                image_id=image.image_id,
                                ai_model_version_id=active_model.ai_model_version_id,
                                status='completed',
                                processing_time=processing_time
                            )
                            if analysis:
                                analysis_created.append({
                                    'image_id': image.image_id,
                                    'analysis_id': analysis.analysis_id
                                })
                        except Exception as e:
                            # Log analysis error but don't fail the upload
                            analysis_errors.append({
                                'image_id': image.image_id,
                                'error': f'Failed to create analysis: {str(e)}'
                            })
                else:
                    upload_errors.append({
                        'image_url': image_url,
                        'error': 'Failed to upload image'
                    })
            except Exception as e:
                upload_errors.append({
                    'image_url': image_url,
                    'error': str(e)
                })
        
        # Merge all errors
        all_errors = validation_errors + credit_check_errors + upload_errors
        
        # Serialize successful uploads
        response_schema = RetinalImageResponseSchema()
        serialized_uploaded = [response_schema.dump(img) for img in uploaded_images]
        
        # Calculate total counts including validation errors
        total_error_count = len(all_errors)
        total_success_count = len(uploaded_images)
        total_images = len(data['images'])
        
        # Generate batch_id if not provided
        import uuid
        from datetime import datetime
        if not batch_id:
            batch_id = f"batch_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        response_data = {
            'batch_id': batch_id,
            'batch_status': 'completed' if total_error_count == 0 else 'partial' if total_success_count > 0 else 'failed',
            'uploaded': serialized_uploaded,
            'errors': all_errors,
            'total': total_images,
            'success_count': total_success_count,
            'error_count': total_error_count,
            'created_at': datetime.now().isoformat(),
            'analysis_created': len(analysis_created),
            'analysis_errors': analysis_errors if analysis_errors else None
        }
        
        message = f"Bulk upload completed: {total_success_count} successful, {total_error_count} failed"
        if auto_analyze and analysis_created:
            message += f". {len(analysis_created)} analysis requests created automatically."
        message += f" Batch ID: {batch_id}"
        
        return success_response(response_data, message, 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/<int:image_id>', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def get_image(image_id):
    """
    Get retinal image by ID
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_images_by_patient(patient_id):
    """
    Get all images for a patient
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_roles(['ClinicManager', 'Admin', 'Doctor'])
def get_images_by_clinic(clinic_id):
    """
    Get all images uploaded by a clinic
    ---
    tags:
      - Retinal Image
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
        description: List of images
    """
    try:
        images = image_service.get_images_by_clinic(clinic_id)
        patient_ids = list({img.patient_id for img in images if getattr(img, 'patient_id', None) is not None})
        patient_names = {}
        for pid in patient_ids:
            try:
                p = patient_repo.get_by_id(pid)
                patient_names[pid] = p.patient_name if p else None
            except Exception:
                patient_names[pid] = None
        return success_response({
            'count': len(images),
            'images': [{
                'image_id': img.image_id,
                'patient_id': img.patient_id,
                'patient_name': patient_names.get(img.patient_id) if getattr(img, 'patient_id', None) is not None else None,
                'image_type': img.image_type,
                'eye_side': img.eye_side,
                'status': img.status,
                'image_url': img.image_url,
                'upload_time': img.upload_time.isoformat() if img.upload_time else None
            } for img in images]
        })
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@retinal_image_bp.route('/status/<status>', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_images_by_status(status):
    """
    Get images by status
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_roles(['Doctor', 'Admin'])
def get_pending_analysis():
    """
    Get images pending AI analysis
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_role('Admin')
def mark_as_processing(image_id):
    """
    Mark image as processing
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_role('Admin')
def mark_as_error(image_id):
    """
    Mark image as error
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_roles(['Doctor', 'Admin', 'ClinicManager'])
def update_image(image_id):
    """
    Update image information
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_roles(['Doctor', 'Admin'])
def delete_image(image_id):
    """
    Delete retinal image
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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
@require_roles(['Doctor', 'Admin', 'ClinicManager'])
def get_stats():
    """
    Get image statistics
    ---
    tags:
      - Retinal Image
    security:
      - Bearer: []
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

