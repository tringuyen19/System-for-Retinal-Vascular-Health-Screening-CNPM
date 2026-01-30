from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from api.middleware.auth_middleware import require_roles, require_role
from infrastructure.repositories.subscription_repository import SubscriptionRepository
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.service_package_repository import ServicePackageRepository
from infrastructure.databases.mssql import session
from services.subscription_service import SubscriptionService
from services.account_service import AccountService
from services.service_package_service import ServicePackageService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import SubscriptionCreateRequestSchema, SubscriptionUpdateRequestSchema, SubscriptionResponseSchema
from datetime import datetime, timedelta, date

subscription_bp = Blueprint('subscription', __name__, url_prefix='/api/subscriptions')

# Initialize repositories (only for service initialization)
subscription_repo = SubscriptionRepository(session)
account_repo = AccountRepository(session)
package_repo = ServicePackageRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
subscription_service = SubscriptionService(subscription_repo)
account_service = AccountService(account_repo)
package_service = ServicePackageService(package_repo)


@subscription_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Subscription
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Subscription service is running")


@subscription_bp.route('', methods=['POST'])
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def create_subscription():
    """
    Create a new subscription
    ---
    tags:
      - Subscription
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
            - account_id
            - package_id
            - remaining_credits
          properties:
            account_id:
              type: integer
              example: 1
            package_id:
              type: integer
              example: 1
            start_date:
              type: string
              format: date
              example: "2024-01-01"
              description: Optional. Defaults to today if not provided
            end_date:
              type: string
              format: date
              example: "2024-12-31"
              description: Optional. Auto-calculated from start_date + package duration_days
            remaining_credits:
              type: integer
              example: 100
            status:
              type: string
              example: "active"
    responses:
      201:
        description: Subscription created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Subscription created successfully
            data:
              type: object
      400:
        description: Invalid input
    """
    try:
        schema = SubscriptionCreateRequestSchema()
        data = schema.load(request.get_json())
        
        account = account_service.get_account_by_id(data['account_id'])
        if not account:
            return not_found_response('Account not found')
        
        # Validate package exists and get package details
        package = package_service.get_package_by_id(data['package_id'])
        if not package:
            return not_found_response('Service package not found')
        
        # Validate package has duration_days
        if not hasattr(package, 'duration_days') or package.duration_days is None:
            return error_response('Service package missing duration_days information', 400)
        
        # Auto-calculate start_date and end_date from package duration
        start_date = data.get('start_date')
        if not start_date:
            start_date = date.today()
        
        end_date = data.get('end_date')
        if not end_date:
            # Calculate end_date from start_date + package duration_days
            # IMPORTANT: Use duration_days from the package (e.g., 30, 90, 180 days)
            duration_days = package.duration_days
            if duration_days <= 0:
                return error_response('Invalid package duration_days', 400)
            end_date = start_date + timedelta(days=duration_days)
        
        subscription = subscription_service.create_subscription(
            account_id=data['account_id'],
            package_id=data['package_id'],
            start_date=start_date,
            end_date=end_date,
            remaining_credits=data['remaining_credits'],
            status=data.get('status', 'active')
        )
        
        response_schema = SubscriptionResponseSchema()
        return success_response(response_schema.dump(subscription), 'Subscription created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/<int:subscription_id>', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def get_subscription(subscription_id):
    """
    Get subscription by ID
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    parameters:
      - name: subscription_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Subscription found
      404:
        description: Subscription not found
    """
    try:
        subscription = subscription_service.get_subscription_by_id(subscription_id)
        if not subscription:
            return not_found_response('Subscription not found')
        
        schema = SubscriptionResponseSchema()
        return success_response(schema.dump(subscription))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/account/<int:account_id>', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_subscriptions_by_account(account_id):
    """
    Get all subscriptions for an account
    ---
    tags:
      - Subscription
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
        description: List of subscriptions
    """
    try:
        subscriptions = subscription_service.get_subscriptions_by_account(account_id)
        
        return success_response({
            'account_id': account_id,
            'count': len(subscriptions),
            'subscriptions': SubscriptionResponseSchema(many=True).dump(subscriptions)
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/account/<int:account_id>/active', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin'])
def get_active_subscription(account_id):
    """
    Get active subscription for an account
    ---
    tags:
      - Subscription
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
        description: Active subscription found
      404:
        description: No active subscription
    """
    try:
        subscription = subscription_service.get_active_subscription(account_id)
        if not subscription:
            return not_found_response('No active subscription found')
        
        schema = SubscriptionResponseSchema()
        return success_response(schema.dump(subscription))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/account/<int:account_id>/credits', methods=['GET'])
@require_roles(['Patient', 'Doctor', 'Admin', 'ClinicManager'])
def get_account_credits(account_id):
    """
    Get remaining credits for an account (FR-12)
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
    responses:
      200:
        description: Remaining credits retrieved successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Success
            data:
              type: object
              properties:
                account_id:
                  type: integer
                  example: 1
                remaining_credits:
                  type: integer
                  example: 100
                has_active_subscription:
                  type: boolean
                  example: true
      404:
        description: Account not found
    """
    try:
        # Validate account exists
        account = account_service.get_account_by_id(account_id)
        if not account:
            return not_found_response('Account not found')
        
        # Get remaining credits via SERVICE ✅
        remaining_credits = subscription_service.get_remaining_credits(account_id)
        
        # Check if has active subscription
        active_subscription = subscription_service.get_active_subscription(account_id)
        has_active_subscription = active_subscription is not None
        
        return success_response({
            'account_id': account_id,
            'remaining_credits': remaining_credits,
            'has_active_subscription': has_active_subscription
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/status/<status>', methods=['GET'])
@require_roles(['Admin', 'ClinicManager'])
def get_subscriptions_by_status(status):
    """
    Get subscriptions by status
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    parameters:
      - name: status
        in: path
        required: true
        schema:
          type: string
          enum: [active, expired, cancelled]
    responses:
      200:
        description: List of subscriptions
    """
    try:
        subscriptions = subscription_service.get_subscriptions_by_status(status)
        
        return success_response({
            'status': status,
            'count': len(subscriptions),
            'subscriptions': [{
                'subscription_id': s.subscription_id,
                'account_id': s.account_id,
                'package_id': s.package_id,
                'remaining_credits': s.remaining_credits,
                'end_date': s.end_date.isoformat() if s.end_date else None
            } for s in subscriptions]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/expiring-soon', methods=['GET'])
def get_expiring_soon():
    """
    Get subscriptions expiring soon
    ---
    tags:
      - Subscription
    parameters:
      - name: days
        in: query
        required: false
        schema:
          type: integer
          default: 7
    responses:
      200:
        description: List of subscriptions expiring soon
    """
    try:
        days = request.args.get('days', 7, type=int)
        subscriptions = subscription_service.get_expiring_soon(days)
        
        return success_response({
            'days': days,
            'count': len(subscriptions),
            'subscriptions': [{
                'subscription_id': s.subscription_id,
                'account_id': s.account_id,
                'end_date': s.end_date.isoformat() if s.end_date else None,
                'remaining_credits': s.remaining_credits
            } for s in subscriptions]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/<int:subscription_id>/deduct-credit', methods=['PUT'])
@require_role('Admin')
def deduct_credit(subscription_id):
    """
    Deduct credits from subscription
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: subscription_id
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
            - amount
          properties:
            amount:
              type: integer
              example: 10
    responses:
      200:
        description: Credits deducted successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Credits deducted successfully
            data:
              type: object
      400:
        description: Amount is required
      404:
        description: Subscription not found
    """
    try:
        data = request.get_json()
        if not data.get('amount'):
            return validation_error_response({'amount': 'Amount is required'})
        
        subscription = subscription_service.deduct_credits(subscription_id, data['amount'])
        if not subscription:
            return not_found_response('Subscription not found or insufficient credits')
        
        return success_response({
            'subscription_id': subscription.subscription_id,
            'remaining_credits': subscription.remaining_credits
        }, 'Credits deducted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/<int:subscription_id>/add-credit', methods=['PUT'])
@require_roles(['Admin', 'ClinicManager'])
def add_credit(subscription_id):
    """
    Add credits to subscription
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: subscription_id
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
            - amount
          properties:
            amount:
              type: integer
              example: 50
    responses:
      200:
        description: Credits added successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Credits added successfully
            data:
              type: object
      400:
        description: Amount is required
      404:
        description: Subscription not found
    """
    try:
        data = request.get_json()
        if not data.get('amount'):
            return validation_error_response({'amount': 'Amount is required'})
        
        subscription = subscription_service.add_credits(subscription_id, data['amount'])
        if not subscription:
            return not_found_response('Subscription not found')
        
        return success_response({
            'subscription_id': subscription.subscription_id,
            'remaining_credits': subscription.remaining_credits
        }, 'Credits added successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/<int:subscription_id>/cancel', methods=['PUT'])
def cancel_subscription(subscription_id):
    """
    Cancel subscription
    ---
    tags:
      - Subscription
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: subscription_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
    responses:
      200:
        description: Subscription cancelled
        schema:
          type: object
          properties:
            message:
              type: string
              example: Subscription cancelled successfully
            data:
              type: object
              properties:
                subscription_id:
                  type: integer
                status:
                  type: string
      404:
        description: Subscription not found
    """
    try:
        subscription = subscription_service.cancel_subscription(subscription_id)
        if not subscription:
            return not_found_response('Subscription not found')
        
        return success_response({
            'subscription_id': subscription.subscription_id,
            'status': subscription.status
        }, 'Subscription cancelled successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/<int:subscription_id>/renew', methods=['PUT'])
@require_roles(['Patient', 'Admin', 'ClinicManager'])
def renew_subscription(subscription_id):
    """
    Renew subscription
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: subscription_id
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
            - duration_days
            - additional_credits
          properties:
            duration_days:
              type: integer
              example: 30
            additional_credits:
              type: integer
              example: 100
    responses:
      200:
        description: Subscription renewed
        schema:
          type: object
          properties:
            message:
              type: string
              example: Subscription renewed successfully
            data:
              type: object
      400:
        description: Missing required fields
      404:
        description: Subscription not found
    """
    try:
        data = request.get_json()
        
        required_fields = ['duration_days', 'additional_credits']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return validation_error_response({'message': f'Missing required fields: {", ".join(missing_fields)}'})
        
        subscription = subscription_service.renew_subscription(
            subscription_id,
            data['duration_days'],
            data['additional_credits']
        )
        if not subscription:
            return not_found_response('Subscription not found')
        
        return success_response({
            'subscription_id': subscription.subscription_id,
            'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
            'remaining_credits': subscription.remaining_credits,
            'status': subscription.status
        }, 'Subscription renewed successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    """
    Delete subscription
    ---
    tags:
      - Subscription
    parameters:
      - name: subscription_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Subscription deleted successfully
      404:
        description: Subscription not found
    """
    try:
        result = subscription_service.delete_subscription(subscription_id)
        if not result:
            return not_found_response('Subscription not found')
        
        return success_response(None, 'Subscription deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@subscription_bp.route('/stats', methods=['GET'])
@require_roles(['Admin', 'ClinicManager'])
def get_stats():
    """
    Get subscription statistics
    ---
    tags:
      - Subscription
    security:
      - Bearer: []
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: Subscription statistics
    """
    try:
        status = request.args.get('status')
        
        if status:
            count = subscription_service.count_by_status(status)
            return success_response({
                'status': status,
                'count': count
            })
        else:
            stats = subscription_service.get_subscription_statistics()
            
            return success_response({
                'total_subscriptions': stats.get('total_subscriptions', 0),
                'active': stats.get('active', 0),
                'expired': stats.get('expired', 0),
                'cancelled': stats.get('cancelled', 0),
                'expiring_soon': stats.get('expiring_soon', 0)
            })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

