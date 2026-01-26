from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.notification_repository import NotificationRepository
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.databases.mssql import session
from services.notification_service import NotificationService
from services.account_service import AccountService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import NotificationCreateRequestSchema, NotificationUpdateRequestSchema, NotificationResponseSchema

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

# Initialize repositories (only for service initialization)
notification_repo = NotificationRepository(session)
account_repo = AccountRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
notification_service = NotificationService(notification_repo)
account_service = AccountService(account_repo)


@notification_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Notification
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Notification service is running")


@notification_bp.route('', methods=['POST'])
def send_notification():
    """
    Send a new notification
    ---
    tags:
      - Notification
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
            - notification_type
            - content
          properties:
            account_id:
              type: integer
              example: 1
            notification_type:
              type: string
              example: "ai_result_ready"
            content:
              type: string
              example: "AI analysis completed for analysis ID 123"
    responses:
      201:
        description: Notification sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Notification sent successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        # STEP 1: Validate request data
        schema = NotificationCreateRequestSchema()
        data = schema.load(request.get_json())
        
        # STEP 2: Verify account exists via SERVICE ✅
        account = account_service.get_account_by_id(data['account_id'])
        if not account:
            return not_found_response('Account not found')
        
        # STEP 3: Send notification via SERVICE ✅
        notification = notification_service.send_notification(
            account_id=data['account_id'],
            notification_type=data['notification_type'],
            content=data['content']
        )
        
        response_schema = NotificationResponseSchema()
        return success_response(response_schema.dump(notification), 'Notification sent successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/<int:notification_id>', methods=['GET'])
def get_notification(notification_id):
    """
    Get notification by ID
    ---
    tags:
      - Notification
    parameters:
      - name: notification_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Notification found
      404:
        description: Notification not found
    """
    try:
        # Call SERVICE ✅
        notification = notification_service.get_notification_by_id(notification_id)
        if not notification:
            return not_found_response('Notification not found')
        
        schema = NotificationResponseSchema()
        return success_response(schema.dump(notification))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/account/<int:account_id>', methods=['GET'])
def get_notifications_by_account(account_id):
    """
    Get all notifications for an account
    ---
    tags:
      - Notification
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
      - name: unread_only
        in: query
        required: false
        schema:
          type: boolean
          default: false
      - name: type
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: List of notifications
    """
    try:
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        notification_type = request.args.get('type')
        
        # Call SERVICE ✅
        if unread_only:
            notifications = notification_service.get_unread_notifications(account_id)
        elif notification_type:
            notifications = notification_service.get_notifications_by_account(account_id)
            # Filter by type in controller (or add method to service)
            notifications = [n for n in notifications if n.notification_type == notification_type]
        else:
            notifications = notification_service.get_notifications_by_account(account_id)
        
        return success_response({
            'account_id': account_id,
            'count': len(notifications),
            'notifications': [{
                'notification_id': n.notification_id,
                'notification_type': n.notification_type,
                'content': n.content,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat() if n.created_at else None
            } for n in notifications]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/account/<int:account_id>/unread', methods=['GET'])
def get_unread_notifications(account_id):
    """
    Get unread notifications for an account
    ---
    tags:
      - Notification
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of unread notifications
    """
    try:
        # Call SERVICE ✅
        notifications = notification_service.get_unread_notifications(account_id)
        
        return success_response({
            'account_id': account_id,
            'count': len(notifications),
            'notifications': [{
                'notification_id': n.notification_id,
                'notification_type': n.notification_type,
                'content': n.content,
                'created_at': n.created_at.isoformat() if n.created_at else None
            } for n in notifications]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/account/<int:account_id>/recent', methods=['GET'])
def get_recent_notifications(account_id):
    """
    Get recent notifications for an account
    ---
    tags:
      - Notification
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 10
    responses:
      200:
        description: List of recent notifications
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Call SERVICE ✅
        notifications = notification_service.get_recent_notifications(account_id, limit)
        
        return success_response({
            'account_id': account_id,
            'count': len(notifications),
            'notifications': [{
                'notification_id': n.notification_id,
                'notification_type': n.notification_type,
                'content': n.content,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat() if n.created_at else None
            } for n in notifications]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """
    Mark notification as read
    ---
    tags:
      - Notification
    parameters:
      - name: notification_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Notification marked as read
      404:
        description: Notification not found
    """
    try:
        # Call SERVICE ✅
        notification = notification_service.mark_as_read(notification_id)
        if not notification:
            return not_found_response('Notification not found')
        
        return success_response({
            'notification_id': notification.notification_id,
            'is_read': notification.is_read,
            'read_at': notification.read_at.isoformat() if notification.read_at else None
        }, 'Notification marked as read')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/account/<int:account_id>/read-all', methods=['PUT'])
def mark_all_as_read(account_id):
    """
    Mark all notifications as read for an account
    ---
    tags:
      - Notification
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: All notifications marked as read
    """
    try:
        # Call SERVICE ✅
        result = notification_service.mark_all_as_read(account_id)
        
        return success_response({
            'account_id': account_id,
            'marked_count': result
        }, f'All notifications marked as read')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """
    Delete notification
    ---
    tags:
      - Notification
    parameters:
      - name: notification_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Notification deleted successfully
      404:
        description: Notification not found
    """
    try:
        # Call SERVICE ✅
        result = notification_service.delete_notification(notification_id)
        if not result:
            return not_found_response('Notification not found')
        
        return success_response(None, 'Notification deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/account/<int:account_id>/delete-all', methods=['DELETE'])
def delete_all_notifications(account_id):
    """
    Delete all notifications for an account
    ---
    tags:
      - Notification
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
      - name: read_only
        in: query
        required: false
        schema:
          type: boolean
          default: false
    responses:
      200:
        description: Notifications deleted successfully
    """
    try:
        read_only = request.args.get('read_only', 'false').lower() == 'true'
        
        # Call SERVICE ✅
        if read_only:
            count = notification_service.delete_read_notifications(account_id)
            message = f'{count} read notifications deleted'
        else:
            count = notification_service.delete_all_by_account(account_id)
            message = f'{count} notifications deleted'
        
        return success_response({
            'account_id': account_id,
            'deleted_count': count
        }, message)
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get notification statistics
    ---
    tags:
      - Notification
    parameters:
      - name: account_id
        in: query
        required: false
        schema:
          type: integer
      - name: type
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: Notification statistics
    """
    try:
        account_id = request.args.get('account_id', type=int)
        notification_type = request.args.get('type')
        
        if account_id:
            # Call SERVICE to get statistics ✅
            stats = notification_service.get_notification_statistics(account_id)
            return success_response({
                'account_id': account_id,
                'total_notifications': stats['total'],
                'unread_notifications': stats['unread'],
                'read_notifications': stats['read']
            })
        elif notification_type:
            # Call SERVICE ✅
            count = notification_service.count_by_type(account_id if account_id else 0, notification_type)
            return success_response({
                'notification_type': notification_type,
                'count': count
            })
        else:
            # Call SERVICE to get total notifications ✅
            total = notification_service.count_total_notifications()
            return success_response({
                'total_notifications': total
            })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@notification_bp.route('/broadcast', methods=['POST'])
def broadcast_notification():
    """
    Broadcast notification to multiple accounts
    ---
    tags:
      - Notification
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
            - account_ids
            - notification_type
            - content
          properties:
            account_ids:
              type: array
              items:
                type: integer
              example: [1, 2, 3]
            notification_type:
              type: string
              example: "system_announcement"
            content:
              type: string
              example: "System maintenance scheduled for tomorrow"
    responses:
      201:
        description: Notifications broadcast successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Notifications broadcast successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('account_ids') or not data.get('notification_type') or not data.get('content'):
            return validation_error_response({'message': 'account_ids, notification_type, and content are required'})
        
        if not isinstance(data['account_ids'], list):
            return validation_error_response({'account_ids': 'Must be an array of account IDs'})
        
        # Send notifications to all accounts via SERVICE ✅
        notifications = notification_service.broadcast_notification(
            account_ids=data['account_ids'],
            notification_type=data['notification_type'],
            content=data['content']
        )
        count = len(notifications)
        
        return success_response({
            'total_sent': count,
            'total_accounts': len(data['account_ids'])
        }, f'Notification broadcast to {count} accounts'), 201
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

