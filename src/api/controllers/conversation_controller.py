from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.conversation_repository import ConversationRepository
from infrastructure.repositories.message_repository import MessageRepository
from infrastructure.repositories.patient_profile_repository import PatientProfileRepository
from infrastructure.repositories.doctor_profile_repository import DoctorProfileRepository
from infrastructure.databases.mssql import session
from services.conversation_service import ConversationService
from services.message_service import MessageService
from services.patient_profile_service import PatientProfileService
from services.doctor_profile_service import DoctorProfileService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import ConversationCreateRequestSchema, ConversationUpdateRequestSchema, ConversationResponseSchema, MessageResponseSchema

conversation_bp = Blueprint('conversation', __name__, url_prefix='/api/conversations')

# Initialize repositories (only for service initialization)
conversation_repo = ConversationRepository(session)
message_repo = MessageRepository(session)
patient_repo = PatientProfileRepository(session)
doctor_repo = DoctorProfileRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
conversation_service = ConversationService(conversation_repo)
message_service = MessageService(message_repo)
patient_service = PatientProfileService(patient_repo)
doctor_service = DoctorProfileService(doctor_repo)


@conversation_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Conversation
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Conversation service is running")


@conversation_bp.route('', methods=['POST'])
def create_conversation():
    """
    Create or get existing conversation between patient and doctor
    ---
    tags:
      - Conversation
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
            - doctor_id
          properties:
            patient_id:
              type: integer
              example: 1
            doctor_id:
              type: integer
              example: 2
            status:
              type: string
              example: "active"
    responses:
      201:
        description: Conversation created/found successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Conversation started successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate request data with schema
        schema = ConversationCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Validate patient and doctor exist via SERVICES ✅
        patient = patient_service.get_patient_by_id(data['patient_id'])
        if not patient:
            return not_found_response('Patient not found')
        
        doctor = doctor_service.get_doctor_by_id(data['doctor_id'])
        if not doctor:
            return not_found_response('Doctor not found')
        
        # STEP 3: Start conversation via SERVICE ✅ (get or create)
        conversation = conversation_service.start_conversation(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id']
        )
        
        # STEP 4: Serialize response with schema
        response_schema = ConversationResponseSchema()
        return success_response(response_schema.dump(conversation), 'Conversation started successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Get conversation by ID
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Conversation found
      404:
        description: Conversation not found
    """
    try:
        # Call SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        # Serialize response with schema
        schema = ConversationResponseSchema()
        return success_response(schema.dump(conversation))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/patient/<int:patient_id>', methods=['GET'])
def get_conversations_by_patient(patient_id):
    """
    Get all conversations for a patient
    ---
    tags:
      - Conversation
    parameters:
      - name: patient_id
        in: path
        required: true
        schema:
          type: integer
      - name: active_only
        in: query
        required: false
        schema:
          type: boolean
          default: false
    responses:
      200:
        description: List of conversations
    """
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Call SERVICE ✅
        if active_only:
            conversations = conversation_service.get_active_conversations_by_patient(patient_id)
        else:
            conversations = conversation_service.get_conversations_by_patient(patient_id)
        
        # Serialize response with schema
        schema = ConversationResponseSchema(many=True)
        return success_response({
            'patient_id': patient_id,
            'count': len(conversations),
            'conversations': schema.dump(conversations)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/doctor/<int:doctor_id>', methods=['GET'])
def get_conversations_by_doctor(doctor_id):
    """
    Get all conversations for a doctor
    ---
    tags:
      - Conversation
    parameters:
      - name: doctor_id
        in: path
        required: true
        schema:
          type: integer
      - name: active_only
        in: query
        required: false
        schema:
          type: boolean
          default: false
    responses:
      200:
        description: List of conversations
    """
    try:
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # Call SERVICE ✅
        if active_only:
            conversations = conversation_service.get_active_conversations_by_doctor(doctor_id)
        else:
            conversations = conversation_service.get_conversations_by_doctor(doctor_id)
        
        # Serialize response with schema
        schema = ConversationResponseSchema(many=True)
        return success_response({
            'doctor_id': doctor_id,
            'count': len(conversations),
            'conversations': schema.dump(conversations)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/close', methods=['PUT'])
def close_conversation(conversation_id):
    """
    Close a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Conversation closed successfully
      404:
        description: Conversation not found
    """
    try:
        # Call SERVICE ✅
        conversation = conversation_service.close_conversation(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        schema = ConversationResponseSchema()
        return success_response(schema.dump(conversation), 'Conversation closed successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/reopen', methods=['PUT'])
def reopen_conversation(conversation_id):
    """
    Reopen a closed conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Conversation reopened successfully
      404:
        description: Conversation not found
    """
    try:
        # Call SERVICE ✅
        conversation = conversation_service.reopen_conversation(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        schema = ConversationResponseSchema()
        return success_response(schema.dump(conversation), 'Conversation reopened successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """
    Get all messages in a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
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
    responses:
      200:
        description: List of messages
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # Verify conversation exists via SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        # Get messages via SERVICE ✅
        messages = message_service.get_messages_by_conversation(conversation_id)
        
        # Apply limit if needed
        if limit and len(messages) > limit:
            messages = messages[-limit:]  # Get most recent
        
        return success_response({
            'conversation_id': conversation_id,
            'count': len(messages),
            'messages': MessageResponseSchema(many=True).dump(messages)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """
    Send a message in a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: conversation_id
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
            - sender_type
            - sender_name
            - content
          properties:
            sender_type:
              type: string
              enum: [patient, doctor]
              example: "patient"
            sender_name:
              type: string
              example: "John Doe"
            content:
              type: string
              example: "Hello, I have a question about my diagnosis"
    responses:
      201:
        description: Message sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Message sent successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['sender_type', 'sender_name', 'content']):
            return validation_error_response({
                'sender_type': 'Required',
                'sender_name': 'Required',
                'content': 'Required'
            })
        
        # Verify conversation exists via SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        # Send message via SERVICE ✅
        message = message_service.send_message(
            conversation_id=conversation_id,
            sender_type=data['sender_type'],
            sender_name=data['sender_name'],
            content=data['content']
        )
        
        response_schema = MessageResponseSchema()
        return success_response(response_schema.dump(message), 'Message sent successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/messages/search', methods=['GET'])
def search_messages(conversation_id):
    """
    Search messages in a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
      - name: query
        in: query
        required: true
        schema:
          type: string
    responses:
      200:
        description: Search results
    """
    try:
        query = request.args.get('query', '')
        if not query:
            return validation_error_response({'query': 'Search query is required'})
        
        # Verify conversation exists via SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        # Search messages via SERVICE ✅
        messages = message_service.search_messages(conversation_id, query)
        
        return success_response({
            'conversation_id': conversation_id,
            'query': query,
            'count': len(messages),
            'messages': MessageResponseSchema(many=True).dump(messages)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/messages/last', methods=['GET'])
def get_last_message(conversation_id):
    """
    Get last message in a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Last message
      404:
        description: No messages found
    """
    try:
        # Verify conversation exists via SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        # Get last message via SERVICE ✅
        message = message_service.get_last_message(conversation_id)
        if not message:
            return not_found_response('No messages found in this conversation')
        
        schema = MessageResponseSchema()
        return success_response(schema.dump(message))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>/messages/<int:message_id>', methods=['DELETE'])
def delete_message(conversation_id, message_id):
    """
    Delete a message from a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
      - name: message_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Message deleted successfully
      404:
        description: Message not found
    """
    try:
        # Verify conversation exists via SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(conversation_id)
        if not conversation:
            return not_found_response('Conversation not found')
        
        # Delete message via SERVICE ✅
        result = message_service.delete_message(message_id)
        if not result:
            return not_found_response('Message not found')
        
        return success_response(None, 'Message deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    Delete a conversation
    ---
    tags:
      - Conversation
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Conversation deleted successfully
      404:
        description: Conversation not found
    """
    try:
        # Call SERVICE ✅
        result = conversation_service.delete_conversation(conversation_id)
        if not result:
            return not_found_response('Conversation not found')
        
        return success_response(None, 'Conversation deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@conversation_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get conversation statistics
    ---
    tags:
      - Conversation
    responses:
      200:
        description: Conversation statistics
    """
    try:
        # Call SERVICE ✅
        stats = conversation_service.get_conversation_statistics()
        
        return success_response(stats)
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

