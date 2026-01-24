"""
Notification Service - Business Logic Layer
Handles notification management
"""

from typing import List, Optional
from datetime import datetime
from domain.models.notification import Notification
from domain.models.inotification_repository import INotificationRepository
from domain.exceptions import NotFoundException, ValidationException


class NotificationService:
    def __init__(self, repository: INotificationRepository):
        self.repository = repository
    
    def send_notification(self, account_id: int, notification_type: str, 
                         content: str) -> Notification:
        """
        Send notification to user (FR-9)
        
        Args:
            account_id: Account ID
            notification_type: Type of notification
            content: Notification content
            
        Returns:
            Notification: Created notification domain model
        """
        if not content:
            raise ValidationException("Notification content is required")
        
        notification = self.repository.send_notification(
            account_id=account_id,
            notification_type=notification_type,
            content=content,
            created_at=datetime.now()
        )
        
        if not notification:
            raise ValueError("Failed to send notification")
        
        return notification
    
    def send_ai_result_notification(self, account_id: int, analysis_id: int) -> Notification:
        """
        Auto-trigger notification when AI result is ready (FR-9)
        
        Args:
            account_id: Account ID
            analysis_id: Analysis ID
            
        Returns:
            Notification: Created notification domain model
        """
        content = f"AI analysis completed for analysis ID {analysis_id}. Please check your results."
        
        return self.send_notification(
            account_id=account_id,
            notification_type='ai_result_ready',
            content=content
        )
    
    def broadcast_notification(self, account_ids: List[int], notification_type: str, 
                              content: str) -> List[Notification]:
        """Broadcast notification to multiple users"""
        notifications = []
        for account_id in account_ids:
            notification = self.send_notification(account_id, notification_type, content)
            if notification:
                notifications.append(notification)
        return notifications
    
    def get_notification_by_id(self, notification_id: int) -> Notification:
        """
        Get notification by ID
        
        Raises:
            NotFoundException: If notification not found
        """
        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise NotFoundException(f"Notification {notification_id} not found")
        return notification
    
    def get_notifications_by_account(self, account_id: int) -> List[Notification]:
        """Get all notifications for an account"""
        return self.repository.get_by_account(account_id)
    
    def get_unread_notifications(self, account_id: int) -> List[Notification]:
        """Get unread notifications for an account"""
        return self.repository.get_unread_by_account(account_id)
    
    def get_recent_notifications(self, account_id: int, limit: int = 10) -> List[Notification]:
        """Get recent notifications for an account"""
        return self.repository.get_recent_by_account(account_id, limit)
    
    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        """Mark notification as read"""
        return self.repository.mark_as_read(notification_id)
    
    def mark_all_as_read(self, account_id: int) -> bool:
        """Mark all notifications as read for an account"""
        return self.repository.mark_all_as_read(account_id)
    
    def delete_notification(self, notification_id: int) -> bool:
        """Delete notification"""
        return self.repository.delete(notification_id)
    
    def delete_all_by_account(self, account_id: int) -> bool:
        """Delete all notifications for an account"""
        return self.repository.delete_all_by_account(account_id)
    
    def count_unread(self, account_id: int) -> int:
        """Count unread notifications"""
        return self.repository.count_unread(account_id)
    
    def count_by_type(self, account_id: int, notification_type: str) -> int:
        """Count notifications by type"""
        return self.repository.count_by_type(account_id, notification_type)
    
    def get_notification_statistics(self, account_id: int) -> dict:
        """Get notification statistics for an account"""
        return {
            'total': len(self.repository.get_by_account(account_id)),
            'unread': self.repository.count_unread(account_id),
            'read': len(self.repository.get_by_account(account_id)) - self.repository.count_unread(account_id)
        }
    
    def delete_read_notifications(self, account_id: int) -> int:
        """Delete all read notifications for an account"""
        return self.repository.delete_read_notifications(account_id)
    
    def count_total_notifications(self) -> int:
        """Count total notifications in system"""
        return self.repository.count_total()