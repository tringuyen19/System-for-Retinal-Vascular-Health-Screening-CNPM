"""
Payment Service - Business Logic Layer
Handles payment processing and management
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from domain.models.payment import Payment
from domain.models.ipayment_repository import IPaymentRepository
from domain.exceptions import NotFoundException, ValidationException
from domain.validators import PaymentValidator


class PaymentService:
    def __init__(self, repository: IPaymentRepository):
        self.repository = repository
    
    def create_payment(self, subscription_id: int, amount: Decimal, 
                      payment_method: str, status: str = 'pending') -> Payment:
        """
        Create payment with validation
        
        Args:
            subscription_id: Subscription ID
            amount: Payment amount
            payment_method: Payment method
            status: Payment status (default: 'pending')
            
        Returns:
            Payment: Created payment domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate using domain validators
        PaymentValidator.validate_amount(float(amount))
        PaymentValidator.validate_payment_method(payment_method)
        
        payment = self.repository.add(
            subscription_id=subscription_id,
            amount=amount,
            payment_method=payment_method,
            payment_time=datetime.now(),
            status=status
        )
        
        if not payment:
            raise ValueError("Failed to create payment")
        
        return payment
    
    def get_payment_by_id(self, payment_id: int) -> Payment:
        """
        Get payment by ID
        
        Raises:
            NotFoundException: If payment not found
        """
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise NotFoundException(f"Payment {payment_id} not found")
        return payment
    
    def get_payments_by_subscription(self, subscription_id: int) -> List[Payment]:
        """Get all payments for a subscription"""
        return self.repository.get_by_subscription(subscription_id)
    
    def get_payment_history(self, account_id: int, limit: int = 50, offset: int = 0) -> List[Payment]:
        """
        Get payment history for an account with pagination (FR-12)
        
        Args:
            account_id: Account ID
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)
            
        Returns:
            List[Payment]: List of payments sorted by date (newest first)
        """
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            raise ValidationException("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValidationException("Offset must be non-negative")
        
        # Get subscriptions for account, then get payments
        # This should be optimized in repository with JOIN
        from infrastructure.repositories.subscription_repository import SubscriptionRepository
        from infrastructure.databases.mssql import session
        
        subscription_repo = SubscriptionRepository(session)
        subscriptions = subscription_repo.get_by_account(account_id)
        
        all_payments = []
        for sub in subscriptions:
            payments = self.repository.get_by_subscription(sub.subscription_id)
            all_payments.extend(payments)
        
        # Sort by date (newest first)
        all_payments.sort(key=lambda p: p.payment_time, reverse=True)
        
        # Apply pagination
        return all_payments[offset:offset+limit]
    
    def get_payments_by_status(self, status: str) -> List[Payment]:
        """Get payments by status"""
        return self.repository.get_by_status(status)
    
    def get_pending_payments(self) -> List[Payment]:
        """Get pending payments"""
        return self.repository.get_pending()
    
    def mark_as_completed(self, payment_id: int) -> Optional[Payment]:
        """Mark payment as completed"""
        return self.repository.mark_as_completed(payment_id)
    
    def mark_as_failed(self, payment_id: int) -> Optional[Payment]:
        """Mark payment as failed"""
        return self.repository.mark_as_failed(payment_id)
    
    def process_payment(self, payment_id: int) -> Optional[Payment]:
        """Process payment (simulate payment gateway)"""
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != 'pending':
            raise ValueError("Payment already processed")
        
        # Simulate payment processing
        # In real app, integrate with payment gateway here
        
        return self.repository.mark_as_completed(payment_id)
    
    def refund_payment(self, payment_id: int) -> Optional[Payment]:
        """Refund payment"""
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        
        if payment.status != 'completed':
            raise ValueError("Can only refund completed payments")
        
        return self.repository.update(payment_id, status='refunded')
    
    def update_payment(self, payment_id: int, **kwargs) -> Optional[Payment]:
        """Update payment"""
        return self.repository.update(payment_id, **kwargs)
    
    def delete_payment(self, payment_id: int) -> bool:
        """Delete payment"""
        return self.repository.delete(payment_id)
    
    def get_total_revenue(self, status: str = 'completed') -> Decimal:
        """Get total revenue"""
        return self.repository.get_total_revenue(status)
    
    def get_revenue_by_date_range(self, start_date: date, end_date: date) -> Decimal:
        """Get revenue by date range"""
        return self.repository.get_revenue_by_date_range(start_date, end_date)
    
    def count_by_status(self, status: str) -> int:
        """Count payments by status"""
        return self.repository.count_by_status(status)
    
    def get_payment_statistics(self) -> dict:
        """Get payment statistics"""
        all_payments = self.repository.get_all()
        return {
            'total_payments': len(all_payments),
            'pending': self.repository.count_by_status('pending'),
            'completed': self.repository.count_by_status('completed'),
            'failed': self.repository.count_by_status('failed'),
            'refunded': self.repository.count_by_status('refunded'),
            'total_revenue': float(self.repository.get_total_revenue('completed')),
            'today_revenue': float(self.repository.get_revenue_by_date_range(date.today(), date.today()))
        }
