from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from infrastructure.repositories.payment_repository import PaymentRepository
from infrastructure.repositories.subscription_repository import SubscriptionRepository
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.databases.mssql import session
from services.payment_service import PaymentService
from services.subscription_service import SubscriptionService
from services.account_service import AccountService
from api.responses import success_response, error_response, not_found_response, validation_error_response
from api.schemas import PaymentCreateRequestSchema, PaymentUpdateRequestSchema, PaymentResponseSchema
from domain.exceptions import ValidationException
from datetime import datetime

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payments')

# Initialize repositories (only for service initialization)
payment_repo = PaymentRepository(session)
subscription_repo = SubscriptionRepository(session)
account_repo = AccountRepository(session)

# Initialize SERVICES (Business Logic Layer) ✅
payment_service = PaymentService(payment_repo)
subscription_service = SubscriptionService(subscription_repo)
account_service = AccountService(account_repo)


@payment_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - Payment
    responses:
      200:
        description: Service is healthy
    """
    return success_response({"status": "healthy"}, "Payment service is running")


@payment_bp.route('', methods=['POST'])
def create_payment():
    """
    Create a new payment
    ---
    tags:
      - Payment
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
            - subscription_id
            - amount
            - payment_method
          properties:
            subscription_id:
              type: integer
              example: 1
            amount:
              type: number
              format: float
              example: 99000.00
            payment_method:
              type: string
              enum: [credit_card, debit_card, bank_transfer, e_wallet, cash]
              example: credit_card
            status:
              type: string
              enum: [pending, completed, failed, refunded]
              example: pending
    responses:
      201:
        description: Payment created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Payment created successfully
            data:
              type: object
      400:
        description: Invalid input
      404:
        description: Subscription not found
    """
    try:
        schema = PaymentCreateRequestSchema()
        data = schema.load(request.get_json())
        
        subscription = subscription_service.get_subscription_by_id(data['subscription_id'])
        if not subscription:
            return not_found_response('Subscription not found')
        
        payment = payment_service.create_payment(
            subscription_id=data['subscription_id'],
            amount=float(data['amount']),
            payment_method=data['payment_method'],
            status=data.get('status', 'pending')
        )
        
        response_schema = PaymentResponseSchema()
        return success_response(response_schema.dump(payment), 'Payment created successfully', 201)
        
    except ValidationError as e:
        return validation_error_response(e.messages)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """
    Get payment by ID
    ---
    tags:
      - Payment
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Payment found
      404:
        description: Payment not found
    """
    try:
        payment = payment_service.get_payment_by_id(payment_id)
        if not payment:
            return not_found_response('Payment not found')
        
        schema = PaymentResponseSchema()
        return success_response(schema.dump(payment))
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/subscription/<int:subscription_id>', methods=['GET'])
def get_payments_by_subscription(subscription_id):
    """
    Get all payments for a subscription
    ---
    tags:
      - Payment
    parameters:
      - name: subscription_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of payments
    """
    try:
        payments = payment_service.get_payments_by_subscription(subscription_id)
        
        return success_response({
            'subscription_id': subscription_id,
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'payment_time': p.payment_time.isoformat() if p.payment_time else None,
                'status': p.status
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/account/<int:account_id>/history', methods=['GET'])
def get_payment_history(account_id):
    """
    Get payment history for an account with pagination (FR-12)
    ---
    tags:
      - Payment
    parameters:
      - name: account_id
        in: path
        required: true
        schema:
          type: integer
          example: 1
      - name: limit
        in: query
        required: false
        schema:
          type: integer
          default: 50
        description: Maximum number of results (1-1000)
      - name: offset
        in: query
        required: false
        schema:
          type: integer
          default: 0
        description: Number of results to skip
    responses:
      200:
        description: Payment history retrieved successfully
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
                count:
                  type: integer
                  example: 5
                total_count:
                  type: integer
                  example: 10
                payments:
                  type: array
                  items:
                    type: object
                    properties:
                      payment_id:
                        type: integer
                      subscription_id:
                        type: integer
                      amount:
                        type: number
                        format: float
                      payment_method:
                        type: string
                      payment_time:
                        type: string
                        format: date-time
                      status:
                        type: string
                        enum: [pending, completed, failed, refunded]
      400:
        description: Invalid pagination parameters
      404:
        description: Account not found
    """
    try:
        # Validate account exists
        account = account_service.get_account_by_id(account_id)
        if not account:
            return not_found_response('Account not found')
        
        # Get pagination parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get payment history via SERVICE ✅
        payments = payment_service.get_payment_history(account_id, limit=limit, offset=offset)
        
        # Serialize response with schema
        schema = PaymentResponseSchema(many=True)
        
        return success_response({
            'account_id': account_id,
            'count': len(payments),
            'total_count': len(payments),  # Note: This is the count for current page, not total
            'limit': limit,
            'offset': offset,
            'payments': schema.dump(payments)
        })
        
    except ValidationException as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/status/<status>', methods=['GET'])
def get_payments_by_status(status):
    """
    Get payments by status
    ---
    tags:
      - Payment
    parameters:
      - name: status
        in: path
        required: true
        schema:
          type: string
          enum: [pending, completed, failed, refunded]
    responses:
      200:
        description: List of payments
    """
    try:
        payments = payment_service.get_payments_by_status(status)
        
        return success_response({
            'status': status,
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'subscription_id': p.subscription_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'payment_time': p.payment_time.isoformat() if p.payment_time else None
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/pending', methods=['GET'])
def get_pending_payments():
    """
    Get all pending payments
    ---
    tags:
      - Payment
    responses:
      200:
        description: List of pending payments
    """
    try:
        payments = payment_service.get_pending_payments()
        
        return success_response({
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'subscription_id': p.subscription_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'payment_time': p.payment_time.isoformat() if p.payment_time else None
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/completed', methods=['GET'])
def get_completed_payments():
    """
    Get all completed payments
    ---
    tags:
      - Payment
    responses:
      200:
        description: List of completed payments
    """
    try:
        payments = payment_service.get_completed_payments()
        
        return success_response({
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'subscription_id': p.subscription_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'payment_time': p.payment_time.isoformat() if p.payment_time else None
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/failed', methods=['GET'])
def get_failed_payments():
    """
    Get all failed payments
    ---
    tags:
      - Payment
    responses:
      200:
        description: List of failed payments
    """
    try:
        payments = payment_service.get_failed_payments()
        
        return success_response({
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'subscription_id': p.subscription_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'payment_time': p.payment_time.isoformat() if p.payment_time else None
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/method/<payment_method>', methods=['GET'])
def get_payments_by_method(payment_method):
    """
    Get payments by payment method
    ---
    tags:
      - Payment
    parameters:
      - name: payment_method
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of payments
    """
    try:
        payments = payment_service.get_payments_by_method(payment_method)
        
        return success_response({
            'payment_method': payment_method,
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'subscription_id': p.subscription_id,
                'amount': float(p.amount),
                'payment_time': p.payment_time.isoformat() if p.payment_time else None,
                'status': p.status
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('', methods=['GET'])
def get_all_payments():
    """
    Get all payments
    ---
    tags:
      - Payment
    parameters:
      - name: start_date
        in: query
        required: false
        schema:
          type: string
          format: date
      - name: end_date
        in: query
        required: false
        schema:
          type: string
          format: date
    responses:
      200:
        description: List of payments
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                payments = payment_service.get_payments_by_date_range(start, end)
            except ValueError:
                return validation_error_response({'date': 'Invalid date format. Use YYYY-MM-DD'})
        else:
            payments = payment_service.get_all_payments()
        
        return success_response({
            'count': len(payments),
            'payments': [{
                'payment_id': p.payment_id,
                'subscription_id': p.subscription_id,
                'amount': float(p.amount),
                'payment_method': p.payment_method,
                'status': p.status
            } for p in payments]
        })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/<int:payment_id>/complete', methods=['PUT'])
def mark_as_completed(payment_id):
    """
    Mark payment as completed
    ---
    tags:
      - Payment
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Payment marked as completed
      404:
        description: Payment not found
    """
    try:
        payment = payment_service.mark_as_completed(payment_id)
        if not payment:
            return not_found_response('Payment not found')
        
        return success_response({
            'payment_id': payment.payment_id,
            'status': payment.status
        }, 'Payment completed successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/<int:payment_id>/fail', methods=['PUT'])
def mark_as_failed(payment_id):
    """
    Mark payment as failed
    ---
    tags:
      - Payment
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Payment marked as failed
      404:
        description: Payment not found
    """
    try:
        payment = payment_service.mark_as_failed(payment_id)
        if not payment:
            return not_found_response('Payment not found')
        
        return success_response({
            'payment_id': payment.payment_id,
            'status': payment.status
        }, 'Payment marked as failed')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/<int:payment_id>/refund', methods=['PUT'])
def mark_as_refunded(payment_id):
    """
    Mark payment as refunded
    ---
    tags:
      - Payment
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Payment refunded
      404:
        description: Payment not found
    """
    try:
        payment = payment_service.mark_as_refunded(payment_id)
        if not payment:
            return not_found_response('Payment not found')
        
        return success_response({
            'payment_id': payment.payment_id,
            'status': payment.status
        }, 'Payment refunded successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    """
    Delete payment
    ---
    tags:
      - Payment
    parameters:
      - name: payment_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Payment deleted successfully
      404:
        description: Payment not found
    """
    try:
        result = payment_service.delete_payment(payment_id)
        if not result:
            return not_found_response('Payment not found')
        
        return success_response(None, 'Payment deleted successfully')
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get payment statistics
    ---
    tags:
      - Payment
    parameters:
      - name: status
        in: query
        required: false
        schema:
          type: string
      - name: payment_method
        in: query
        required: false
        schema:
          type: string
    responses:
      200:
        description: Payment statistics
    """
    try:
        status = request.args.get('status')
        payment_method = request.args.get('payment_method')
        
        if status:
            count = payment_service.count_by_status(status)
            return success_response({
                'status': status,
                'count': count
            })
        elif payment_method:
            count = payment_service.count_by_method(payment_method)
            return success_response({
                'payment_method': payment_method,
                'count': count
            })
        else:
            stats = payment_service.get_payment_statistics()
            total_revenue = stats.get('total_revenue', 0)
            pending_count = stats.get('pending_count', 0)
            completed_count = stats.get('completed_count', 0)
            failed_count = stats.get('failed_count', 0)
            
            return success_response({
                'total_revenue': total_revenue,
                'pending_payments': pending_count,
                'completed_payments': completed_count,
                'failed_payments': failed_count
            })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)


@payment_bp.route('/revenue', methods=['GET'])
def get_revenue():
    """
    Get revenue statistics
    ---
    tags:
      - Payment
    parameters:
      - name: start_date
        in: query
        required: false
        schema:
          type: string
          format: date
      - name: end_date
        in: query
        required: false
        schema:
          type: string
          format: date
      - name: status
        in: query
        required: false
        schema:
          type: string
          default: completed
    responses:
      200:
        description: Revenue information
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status', 'completed')
        
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)
                revenue = payment_service.get_revenue_by_date_range(start, end, status)
                
                return success_response({
                    'start_date': start_date,
                    'end_date': end_date,
                    'status': status,
                    'revenue': revenue
                })
            except ValueError:
                return validation_error_response({'date': 'Invalid date format. Use YYYY-MM-DD'})
        else:
            total_revenue = payment_service.get_total_revenue(status)
            return success_response({
                'status': status,
                'total_revenue': total_revenue
            })
        
    except Exception as e:
        return error_response(f'Internal server error: {str(e)}', 500)

