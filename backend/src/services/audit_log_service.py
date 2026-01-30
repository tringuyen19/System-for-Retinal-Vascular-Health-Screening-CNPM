"""
Audit Log Service - Business Logic Layer
Handles audit logging operations (FR-37)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from domain.models.audit_log import AuditLog
from domain.models.iaudit_log_repository import IAuditLogRepository
from domain.exceptions import NotFoundException, ValidationException


class AuditLogService:
    """Service for audit log operations - FR-37"""
    
    def __init__(self, repository: IAuditLogRepository):
        self.repository = repository
    
    def create_log(self, account_id: Optional[int], action_type: str, entity_type: str,
                   entity_id: Optional[int] = None, old_values: Optional[Dict[str, Any]] = None,
                   new_values: Optional[Dict[str, Any]] = None, description: Optional[str] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> AuditLog:
        """
        Create audit log entry (FR-37)
        
        Args:
            account_id: Account ID of user performing action (None for system actions)
            action_type: Type of action (create, update, delete, approve, suspend, etc.)
            entity_type: Type of entity (account, clinic, patient, ai_config, etc.)
            entity_id: ID of entity being modified
            old_values: Dictionary of old values (will be converted to JSON string)
            new_values: Dictionary of new values (will be converted to JSON string)
            description: Human-readable description of the action
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            AuditLog: Created audit log entry
        """
        import json
        
        # Validate required fields
        if not action_type:
            raise ValidationException("action_type is required")
        if not entity_type:
            raise ValidationException("entity_type is required")
        
        # Convert dict to JSON string if provided
        old_values_str = json.dumps(old_values) if old_values else None
        new_values_str = json.dumps(new_values) if new_values else None
        
        return self.repository.create_log(
            account_id=account_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values_str,
            new_values=new_values_str,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now()
        )
    
    def get_by_id(self, audit_log_id: int) -> Optional[AuditLog]:
        """Get audit log by ID"""
        log = self.repository.get_by_id(audit_log_id)
        if not log:
            raise NotFoundException(f"Audit log {audit_log_id} not found")
        return log
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get all audit logs with pagination"""
        return self.repository.get_all(limit=limit, offset=offset)
    
    def get_by_account(self, account_id: int, limit: Optional[int] = None,
                   offset: int = 0) -> List[AuditLog]:
        """Get audit logs by account ID"""
        return self.repository.get_by_account(account_id, limit=limit, offset=offset)
    
    def get_by_action_type(self, action_type: str, limit: Optional[int] = None,
                          offset: int = 0) -> List[AuditLog]:
        """Get audit logs by action type"""
        return self.repository.get_by_action_type(action_type, limit=limit, offset=offset)
    
    def get_by_entity_type(self, entity_type: str, limit: Optional[int] = None,
                          offset: int = 0) -> List[AuditLog]:
        """Get audit logs by entity type"""
        return self.repository.get_by_entity_type(entity_type, limit=limit, offset=offset)
    
    def get_by_entity(self, entity_type: str, entity_id: int,
                     limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get audit logs for a specific entity"""
        return self.repository.get_by_entity(entity_type, entity_id, limit=limit, offset=offset)
    
    def get_by_date_range(self, start_date: date, end_date: date,
                         limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get audit logs within date range"""
        if start_date > end_date:
            raise ValidationException("start_date must be before end_date")
        return self.repository.get_by_date_range(start_date, end_date, limit=limit, offset=offset)
    
    def search_logs(self, account_id: Optional[int] = None, action_type: Optional[str] = None,
                   entity_type: Optional[str] = None, entity_id: Optional[int] = None,
                   start_date: Optional[date] = None, end_date: Optional[date] = None,
                   limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Search audit logs with multiple filters"""
        if start_date and end_date and start_date > end_date:
            raise ValidationException("start_date must be before end_date")
        return self.repository.search(
            account_id=account_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit log statistics (FR-37)"""
        return self.repository.get_statistics()
    
    def count(self) -> int:
        """Get total count of audit logs"""
        return self.repository.count()