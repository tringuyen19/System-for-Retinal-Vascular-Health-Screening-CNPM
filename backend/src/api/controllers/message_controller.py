from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_roles
from infrastructure.repositories.message_repository import MessageRepository
from infrastructure.repositories.conversation_repository import ConversationRepository
from infrastructure.databases.mssql import session
from services.message_service import MessageService
from services.conversation_service import ConversationService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import MessageCreateRequestSchema, MessageResponseSchema

message_bp = Blueprint('message', __name__, url_prefix='/api/messages')

# Initialize repositories (only for service initialization)
message_repo = MessageRepository(session)
conversation_repo = ConversationRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
message_service = MessageService(message_repo)
conversation_service = ConversationService(conversation_repo)


@message_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Message
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Message service is running")


@message_bp.route('', methods=['POST'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def create_message():
    """
    Send a new message
    ---
    tags:
      - Message
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
            - conversation_id
            - sender_type
            - sender_name
            - content
          properties:
            conversation_id:
              type: integer
              example: 1
            sender_type:
              type: string
              enum: [patient, doctor]
              example: "patient"
            sender_name:
              type: string
              example: "Nguyen Van A"
            content:
              type: string
              example: "Hello doctor, I have a question about my test results"
            message_type:
              type: string
              enum: [text, image, file]
              example: "text"
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
        # STEP 1: Validate request data
        schema = MessageCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Verify conversation exists via SERVICE ✅
        conversation = conversation_service.get_conversation_by_id(data['conversation_id'])
        if not conversation:
            return not_found_response('Conversation not found')
        
        # STEP 3: Send message via SERVICE ✅
        message = message_service.send_message(
            conversation_id=data['conversation_id'],
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


@message_bp.route('/<int:message_id>', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_message(message_id):
    """
    Get message by ID
    ---
    tags:
      - Message
    security:
      - Bearer: []
    parameters:
      - name: message_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Message found
      404:
        description: Message not found
    """
    try:
        # Call SERVICE ✅
        message = message_service.get_message_by_id(message_id)
        if not message:
            return not_found_response('Message not found')
        
        schema = MessageResponseSchema()
        return success_response(schema.dump(message))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/conversation/<int:conversation_id>', methods=['GET'])
def get_messages_by_conversation(conversation_id):
    """
    Get all messages in a conversation
    ---
    tags:
      - Message
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
        
        # Call SERVICE ✅
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


@message_bp.route('/conversation/<int:conversation_id>/recent', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_recent_messages(conversation_id):
    """
    Get recent messages in a conversation
    ---
    tags:
      - Message
    security:
      - Bearer: []
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
          default: 20
    responses:
      200:
        description: List of recent messages
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Call SERVICE ✅
        messages = message_service.get_messages_by_conversation(conversation_id)
        messages = messages[-limit:] if len(messages) > limit else messages  # Get most recent
        
        return success_response({
            'conversation_id': conversation_id,
            'count': len(messages),
            'messages': MessageResponseSchema(many=True).dump(messages)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/conversation/<int:conversation_id>/last', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_last_message(conversation_id):
    """
    Get last message in a conversation
    ---
    tags:
      - Message
    security:
      - Bearer: []
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
        # Call SERVICE ✅
        message = message_service.get_last_message(conversation_id)
        if not message:
            return not_found_response('No messages found in this conversation')
        
        schema = MessageResponseSchema()
        return success_response(schema.dump(message))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/conversation/<int:conversation_id>/sender/<sender_type>', methods=['GET'])
def get_messages_by_sender(conversation_id, sender_type):
    """
    Get messages by sender type in a conversation
    ---
    tags:
      - Message
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
      - name: sender_type
        in: path
        required: true
        schema:
          type: string
          enum: [patient, doctor]
    responses:
      200:
        description: List of messages
    """
    try:
        # Call SERVICE ✅
        messages = message_service.get_messages_by_sender(conversation_id, sender_type)
        
        return success_response({
            'conversation_id': conversation_id,
            'sender_type': sender_type,
            'count': len(messages),
            'messages': [{
                'message_id': m.message_id,
                'sender_name': m.sender_name,
                'content': m.content,
                'sent_at': m.sent_at.isoformat() if m.sent_at else None
            } for m in messages]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/conversation/<int:conversation_id>/search', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def search_messages(conversation_id):
    """
    Search messages in a conversation
    ---
    tags:
      - Message
    security:
      - Bearer: []
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
        
        # Call SERVICE ✅
        messages = message_service.search_messages(conversation_id, query)
        
        return success_response({
            'conversation_id': conversation_id,
            'query': query,
            'count': len(messages),
            'messages': MessageResponseSchema(many=True).dump(messages)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/<int:message_id>', methods=['PUT'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def update_message(message_id):
    """
    Update message content
    ---
    tags:
      - Message
    security:
      - Bearer: []
    parameters:
      - name: message_id
        in: path
        required: true
        schema:
          type: integer
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: message_id
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
            - content
          properties:
            content:
              type: string
              example: "Updated message content"
    responses:
      200:
        description: Message updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Message updated successfully
            data:
              type: object
      400:
        description: Content is required
      404:
        description: Message not found
    """
    try:
        data = request.get_json()
        if not data.get('content'):
            return validation_error_response({'content': 'Content is required'})
        
        # Call SERVICE ✅
        message = message_service.update_message(message_id, content=data['content'])
        if not message:
            return not_found_response('Message not found')
        
        return success_response({
            'message_id': message.message_id,
            'content': message.content
        }, 'Message updated successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/<int:message_id>', methods=['DELETE'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def delete_message(message_id):
    """
    Delete message
    ---
    tags:
      - Message
    security:
      - Bearer: []
    parameters:
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
        # Call SERVICE ✅
        result = message_service.delete_message(message_id)
        if not result:
            return not_found_response('Message not found')
        
        return success_response(None, 'Message deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/conversation/<int:conversation_id>/delete-all', methods=['DELETE'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def delete_all_messages(conversation_id):
    """
    Delete all messages in a conversation
    ---
    tags:
      - Message
    security:
      - Bearer: []
    parameters:
      - name: conversation_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Messages deleted successfully
    """
    try:
        # Call SERVICE ✅
        result = message_service.delete_all_by_conversation(conversation_id)
        count = result if isinstance(result, int) else (1 if result else 0)
        
        return success_response({
            'conversation_id': conversation_id,
            'deleted_count': count
        }, f'Messages deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@message_bp.route('/stats', methods=['GET'])
@require_roles(['Doctor', 'Admin'])
def get_stats():
    """
    Get message statistics
    ---
    tags:
      - Message
    security:
      - Bearer: []
    parameters:
      - name: conversation_id
        in: query
        required: false
        schema:
          type: integer
    responses:
      200:
        description: Message statistics
    """
    try:
        conversation_id = request.args.get('conversation_id', type=int)
        
        if conversation_id:
            # Call SERVICE ✅
            count = message_service.count_messages(conversation_id)
            return success_response({
                'conversation_id': conversation_id,
                'total_messages': count
            })
        else:
            # Total messages across all conversations
            return success_response({
                'total_messages': 0  # Need to add method to service if needed
            })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

