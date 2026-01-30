"""
Notification Template Service - Business Logic Layer
Handles notification template management (FR-39)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import re
from domain.models.notification_template import NotificationTemplate
from domain.models.inotification_template_repository import INotificationTemplateRepository
from domain.exceptions import NotFoundException, ValidationException


class NotificationTemplateService:
    """Service for notification template operations - FR-39"""
    
    def __init__(self, repository: INotificationTemplateRepository):
        self.repository = repository
    
    def create_template(self, template_name: str, template_type: str,
                       subject: Optional[str] = None, content_template: str = None,
                       variables_schema: Optional[Dict[str, str]] = None,
                       is_active: bool = False) -> NotificationTemplate:
        """
        Create notification template (FR-39)
        
        Args:
            template_name: Unique template name
            template_type: Type (ai_result_ready, clinic_approved, etc.)
            subject: Email subject (optional)
            content_template: Template content with {{variables}}
            variables_schema: Dict describing available variables
            is_active: Whether template is active
            
        Returns:
            NotificationTemplate: Created template
        """
        # Validate required fields
        if not template_name:
            raise ValidationException("template_name is required")
        if not template_type:
            raise ValidationException("template_type is required")
        if not content_template:
            raise ValidationException("content_template is required")
        
        # Validate template has valid placeholders
        placeholders = re.findall(r'\{\{(\w+)\}\}', content_template)
        if variables_schema:
            schema_vars = set(variables_schema.keys())
            template_vars = set(placeholders)
            if not template_vars.issubset(schema_vars):
                missing = template_vars - schema_vars
                raise ValidationException(f"Template uses variables not in schema: {missing}")
        
        # Convert variables_schema dict to JSON string
        variables_schema_str = json.dumps(variables_schema) if variables_schema else None
        
        return self.repository.create_template(
            template_name=template_name,
            template_type=template_type,
            subject=subject,
            content_template=content_template,
            variables_schema=variables_schema_str,
            is_active=is_active,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def get_by_id(self, template_id: int) -> NotificationTemplate:
        """Get template by ID"""
        template = self.repository.get_by_id(template_id)
        if not template:
            raise NotFoundException(f"Notification template {template_id} not found")
        return template
    
    def get_by_type(self, template_type: str) -> List[NotificationTemplate]:
        """Get templates by type"""
        return self.repository.get_by_type(template_type)
    
    def get_active_template_by_type(self, template_type: str) -> Optional[NotificationTemplate]:
        """Get active template by type"""
        return self.repository.get_active_by_type(template_type)
    
    def get_all(self, include_inactive: bool = False) -> List[NotificationTemplate]:
        """Get all templates"""
        return self.repository.get_all(include_inactive=include_inactive)
    
    def update_template(self, template_id: int, template_name: Optional[str] = None,
                       subject: Optional[str] = None, content_template: Optional[str] = None,
                       variables_schema: Optional[Dict[str, str]] = None) -> NotificationTemplate:
        """Update template"""
        # Validate template exists
        existing = self.repository.get_by_id(template_id)
        if not existing:
            raise NotFoundException(f"Notification template {template_id} not found")
        
        # Validate content_template if provided
        if content_template:
            placeholders = re.findall(r'\{\{(\w+)\}\}', content_template)
            if variables_schema:
                schema_vars = set(variables_schema.keys())
                template_vars = set(placeholders)
                if not template_vars.issubset(schema_vars):
                    missing = template_vars - schema_vars
                    raise ValidationException(f"Template uses variables not in schema: {missing}")
        
        # Convert variables_schema dict to JSON string if provided
        variables_schema_str = None
        if variables_schema is not None:
            variables_schema_str = json.dumps(variables_schema)
        
        updated = self.repository.update_template(
            template_id=template_id,
            template_name=template_name,
            subject=subject,
            content_template=content_template,
            variables_schema=variables_schema_str,
            updated_at=datetime.now()
        )
        
        if not updated:
            raise NotFoundException(f"Notification template {template_id} not found")
        
        return updated
    
    def activate_template(self, template_id: int) -> NotificationTemplate:
        """Activate template (deactivate others of same type)"""
        activated = self.repository.activate_template(template_id, datetime.now())
        if not activated:
            raise NotFoundException(f"Notification template {template_id} not found")
        return activated
    
    def deactivate_template(self, template_id: int) -> NotificationTemplate:
        """Deactivate template"""
        deactivated = self.repository.deactivate_template(template_id, datetime.now())
        if not deactivated:
            raise NotFoundException(f"Notification template {template_id} not found")
        return deactivated
    
    def delete_template(self, template_id: int) -> bool:
        """Delete template"""
        # Validate template exists
        existing = self.repository.get_by_id(template_id)
        if not existing:
            raise NotFoundException(f"Notification template {template_id} not found")
        
        return self.repository.delete_template(template_id)
    
    def render_template(self, template_id: int, variables: Dict[str, Any]) -> str:
        """
        Render template with variables (FR-39)
        
        Args:
            template_id: Template ID
            variables: Dict of variable values
            
        Returns:
            str: Rendered content
        """
        template = self.repository.get_by_id(template_id)
        if not template:
            raise NotFoundException(f"Notification template {template_id} not found")
        
        if not template.is_active:
            raise ValidationException(f"Template {template_id} is not active")
        
        # Render content
        content = template.content_template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        # Check for unresolved placeholders
        unresolved = re.findall(r'\{\{(\w+)\}\}', content)
        if unresolved:
            raise ValidationException(f"Unresolved variables: {unresolved}")
        
        return content
    
    def render_template_by_type(self, template_type: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Render active template by type with variables (FR-39)
        
        Args:
            template_type: Template type
            variables: Dict of variable values
            
        Returns:
            str: Rendered content, or None if no active template
        """
        template = self.repository.get_active_by_type(template_type)
        if not template:
            return None
        
        # Render content
        content = template.content_template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        # Check for unresolved placeholders
        unresolved = re.findall(r'\{\{(\w+)\}\}', content)
        if unresolved:
            raise ValidationException(f"Unresolved variables: {unresolved}")
        
        return content