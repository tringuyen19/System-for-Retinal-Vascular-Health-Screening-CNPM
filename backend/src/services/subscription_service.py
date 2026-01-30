"""
Subscription Service - Business Logic Layer
Handles subscription management
"""

from typing import List, Optional
from datetime import date, timedelta
from domain.models.subscription import Subscription
from domain.models.isubscription_repository import ISubscriptionRepository
from domain.exceptions import NotFoundException, ValidationException, BusinessRuleException
from domain.validators import SubscriptionValidator


class SubscriptionService:
    def __init__(self, repository: ISubscriptionRepository):
        self.repository = repository
    
    def create_subscription(self, account_id: int, package_id: int, 
                           start_date: date, end_date: date, 
                           remaining_credits: int, status: str = 'active') -> Subscription:
        """
        Create subscription with validation (FR-11)
        
        Args:
            account_id: Account ID
            package_id: Service package ID
            start_date: Subscription start date
            end_date: Subscription end date
            remaining_credits: Initial credits
            status: Subscription status (default: 'active')
            
        Returns:
            Subscription: Created subscription domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate using domain validators
        SubscriptionValidator.validate_dates(start_date, end_date)
        SubscriptionValidator.validate_credits(remaining_credits)
        
        subscription = self.repository.add(
            account_id=account_id,
            package_id=package_id,
            start_date=start_date,
            end_date=end_date,
            remaining_credits=remaining_credits,
            status=status
        )
        
        if not subscription:
            raise ValueError("Failed to create subscription")
        
        return subscription
    
    def get_subscription_by_id(self, subscription_id: int) -> Subscription:
        """
        Get subscription by ID
        
        Raises:
            NotFoundException: If subscription not found
        """
        subscription = self.repository.get_by_id(subscription_id)
        if not subscription:
            raise NotFoundException(f"Subscription {subscription_id} not found")
        return subscription
    
    def get_subscriptions_by_account(self, account_id: int) -> List[Subscription]:
        """Get all subscriptions for an account"""
        return self.repository.get_by_account(account_id)
    
    def get_active_subscription(self, account_id: int) -> Optional[Subscription]:
        """Get active subscription for an account"""
        return self.repository.get_active_by_account(account_id)
    
    def get_remaining_credits(self, account_id: int) -> int:
        """
        Get remaining analysis credits for an account (FR-12)
        
        Args:
            account_id: Account ID
            
        Returns:
            int: Remaining credits (0 if no active subscription)
        """
        subscription = self.get_active_subscription(account_id)
        if not subscription:
            return 0
        
        return subscription.remaining_credits
    
    def get_subscriptions_by_status(self, status: str) -> List[Subscription]:
        """Get subscriptions by status"""
        return self.repository.get_by_status(status)
    
    def get_expiring_soon(self, days: int = 7) -> List[Subscription]:
        """Get subscriptions expiring soon"""
        return self.repository.get_expiring_soon(days)
    
    def deduct_credit(self, subscription_id: int, amount: int = 1) -> Subscription:
        """
        Deduct credit from subscription with validation
        
        Args:
            subscription_id: Subscription ID
            amount: Amount to deduct (default: 1)
            
        Returns:
            Subscription: Updated subscription domain model
            
        Raises:
            NotFoundException: If subscription not found
            BusinessRuleException: If insufficient credits or subscription not active
        """
        subscription = self.get_subscription_by_id(subscription_id)
        
        if subscription.status != 'active':
            raise BusinessRuleException("Subscription is not active")
        
        if subscription.remaining_credits < amount:
            raise BusinessRuleException(f"Insufficient credits. Available: {subscription.remaining_credits}, Required: {amount}")
        
        updated = self.repository.deduct_credit(subscription_id, amount)
        if not updated:
            raise NotFoundException(f"Subscription {subscription_id} not found")
        
        return updated
    
    def renew_subscription(self, subscription_id: int, new_end_date: date, 
                          additional_credits: int) -> Optional[Subscription]:
        """Renew subscription"""
        subscription = self.repository.get_by_id(subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")
        
        if new_end_date <= subscription.end_date:
            raise ValueError("New end date must be after current end date")
        
        return self.repository.renew_subscription(subscription_id, new_end_date, additional_credits)
    
    def cancel_subscription(self, subscription_id: int) -> Optional[Subscription]:
        """Cancel subscription"""
        return self.repository.cancel_subscription(subscription_id)
    
    def check_credits(self, account_id: int) -> dict:
        """Check credits for an account"""
        subscription = self.get_active_subscription(account_id)
        if not subscription:
            return {'has_credits': False, 'remaining_credits': 0, 'status': 'no_active_subscription'}
        
        return {
            'has_credits': subscription.remaining_credits > 0,
            'remaining_credits': subscription.remaining_credits,
            'status': subscription.status,
            'expires_at': subscription.end_date
        }
    
    def update_subscription(self, subscription_id: int, **kwargs) -> Optional[Subscription]:
        """Update subscription"""
        return self.repository.update(subscription_id, **kwargs)
    
    def delete_subscription(self, subscription_id: int) -> bool:
        """Delete subscription"""
        return self.repository.delete(subscription_id)
    
    def count_by_status(self, status: str) -> int:
        """Count subscriptions by status"""
        return self.repository.count_by_status(status)
    
    def get_subscription_statistics(self) -> dict:
        """Get subscription statistics"""
        all_subs = self.repository.get_all()
        return {
            'total_subscriptions': len(all_subs),
            'active': self.repository.count_by_status('active'),
            'expired': self.repository.count_by_status('expired'),
            'cancelled': self.repository.count_by_status('cancelled'),
            'expiring_soon': len(self.repository.get_expiring_soon(7))
        }
