"""
Permission Model - SQLAlchemy ORM
Represents role permissions (Resource + Action combinations)
FR-32: Define roles and manage access permissions
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Permission:
    """
    Permission model - Stores which resource+action each role can perform
    
    Attributes:
        permission_id (int): Primary key
        role_id (int): Foreign key to Role
        resource (str): Resource name (Account, Doctor, Clinic, AiModel, Payment, Report, Role, Notification)
        action (str): Action name (create, read, update, delete)
        created_at (datetime): Creation timestamp
    
    Example:
        - permission_id=1, role_id=1 (Admin), resource='Account', action='create'
        - permission_id=2, role_id=1 (Admin), resource='Account', action='delete'
        - permission_id=10, role_id=4 (ClinicManager), resource='Account', action='read'
    """
    
    __tablename__ = 'permissions'
    
    # Columns
    permission_id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    resource = Column(String(50), nullable=False)  # Account, Doctor, Clinic, etc.
    action = Column(String(20), nullable=False)     # create, read, update, delete
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    
    # Unique constraint: each role can only have one permission per resource+action
    __table_args__ = (
        UniqueConstraint('role_id', 'resource', 'action', name='uq_role_resource_action'),
    )
    
    def __init__(self, role_id: int, resource: str, action: str):
        self.role_id = role_id
        self.resource = resource
        self.action = action
        self.created_at = datetime.now()
    
    def __repr__(self):
        return f'<Permission {self.permission_id}: role={self.role_id}, {self.resource}.{self.action}>'
    
    def to_dict(self):
        """Convert permission to dictionary"""
        return {
            'permission_id': self.permission_id,
            'role_id': self.role_id,
            'resource': self.resource,
            'action': self.action,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
