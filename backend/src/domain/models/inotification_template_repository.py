from abc import ABC, abstractmethod
from .notification_template import NotificationTemplate
from typing import List, Optional
from datetime import datetime

class INotificationTemplateRepository(ABC):
    """Repository interface for Notification Template - Domain layer"""
    
    @abstractmethod
    def create_template(self, template_name: str, template_type: str,
                       subject: Optional[str], content_template: str,
                       variables_schema: Optional[str], is_active: bool,
                       created_at: datetime, updated_at: datetime) -> NotificationTemplate:
        """Create a new notification template"""
        pass
    
    @abstractmethod
    def get_by_id(self, template_id: int) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        pass
    
    @abstractmethod
    def get_by_type(self, template_type: str) -> List[NotificationTemplate]:
        """Get templates by type"""
        pass
    
    @abstractmethod
    def get_active_by_type(self, template_type: str) -> Optional[NotificationTemplate]:
        """Get active template by type (only one active per type)"""
        pass
    
    @abstractmethod
    def get_all(self, include_inactive: bool = False) -> List[NotificationTemplate]:
        """Get all templates"""
        pass
    
    @abstractmethod
    def update_template(self, template_id: int, template_name: Optional[str] = None,
                       subject: Optional[str] = None, content_template: Optional[str] = None,
                       variables_schema: Optional[str] = None,
                       updated_at: datetime = None) -> Optional[NotificationTemplate]:
        """Update template"""
        pass
    
    @abstractmethod
    def activate_template(self, template_id: int, updated_at: datetime) -> Optional[NotificationTemplate]:
        """Activate template (deactivate others of same type)"""
        pass
    
    @abstractmethod
    def deactivate_template(self, template_id: int, updated_at: datetime) -> Optional[NotificationTemplate]:
        """Deactivate template"""
        pass
    
    @abstractmethod
    def delete_template(self, template_id: int) -> bool:
        """Delete template"""
        pass