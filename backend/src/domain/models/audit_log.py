from datetime import datetime
from typing import Optional

class AuditLog:
    """Domain model for Audit Log - Pure Python, no framework dependencies"""
    def __init__(self, audit_log_id: int, account_id: Optional[int], action_type: str,
                 entity_type: str, entity_id: Optional[int], old_values: Optional[str],
                 new_values: Optional[str], description: Optional[str],
                 ip_address: Optional[str], user_agent: Optional[str], created_at: datetime):
        self.audit_log_id = audit_log_id
        self.account_id = account_id
        self.action_type = action_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.old_values = old_values
        self.new_values = new_values
        self.description = description
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at