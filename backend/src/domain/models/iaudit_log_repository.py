from abc import ABC, abstractmethod
from .audit_log import AuditLog
from typing import List, Optional
from datetime import datetime, date

class IAuditLogRepository(ABC):
    """Repository interface for Audit Log - Domain layer"""
    
    @abstractmethod
    def create_log(self, account_id: Optional[int], action_type: str, entity_type: str,
                   entity_id: Optional[int], old_values: Optional[str],
                   new_values: Optional[str], description: Optional[str],
                   ip_address: Optional[str], user_agent: Optional[str],
                   created_at: datetime) -> AuditLog:
        """Create a new audit log entry"""
        pass
    
    @abstractmethod
    def get_by_id(self, audit_log_id: int) -> Optional[AuditLog]:
        """Get audit log by ID"""
        pass
    
    @abstractmethod
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get all audit logs with optional pagination"""
        pass
    
    @abstractmethod
    def get_by_account(self, account_id: int, limit: Optional[int] = None, 
                   offset: int = 0) -> List[AuditLog]:
        """Get audit logs by account ID"""
        pass
    
    @abstractmethod
    def get_by_action_type(self, action_type: str, limit: Optional[int] = None,
                          offset: int = 0) -> List[AuditLog]:
        """Get audit logs by action type"""
        pass
    
    @abstractmethod
    def get_by_entity_type(self, entity_type: str, limit: Optional[int] = None,
                          offset: int = 0) -> List[AuditLog]:
        """Get audit logs by entity type"""
        pass
    
    @abstractmethod
    def get_by_entity(self, entity_type: str, entity_id: int,
                     limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get audit logs for a specific entity"""
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date,
                         limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get audit logs within date range"""
        pass
    
    @abstractmethod
    def search(self, account_id: Optional[int] = None, action_type: Optional[str] = None,
              entity_type: Optional[str] = None, entity_id: Optional[int] = None,
              start_date: Optional[date] = None, end_date: Optional[date] = None,
              limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Search audit logs with multiple filters"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total count of audit logs"""
        pass
    
    @abstractmethod
    def count_by_action_type(self, action_type: str) -> int:
        """Count audit logs by action type"""
        pass
    
    @abstractmethod
    def count_by_entity_type(self, entity_type: str) -> int:
        """Count audit logs by entity type"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> dict:
        """Get audit log statistics"""
        pass