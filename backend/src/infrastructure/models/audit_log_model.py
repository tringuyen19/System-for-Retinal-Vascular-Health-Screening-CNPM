from sqlalchemy import Column, BigInteger, String, DateTime, Text, ForeignKey
from infrastructure.databases.base import Base

class AuditLogModel(Base):
    """SQLAlchemy model for audit_logs table - Infrastructure layer"""
    __tablename__ = 'audit_logs'
    __table_args__ = {'extend_existing': True}
    
    audit_log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'), nullable=True)
    action_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    description = Column(String(1000), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<AuditLogModel(audit_log_id={self.audit_log_id}, action_type='{self.action_type}', entity_type='{self.entity_type}')>"