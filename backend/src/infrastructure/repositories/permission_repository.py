"""
Permission Repository - Data access layer for permissions
FR-32: Define roles and manage access permissions
"""

from typing import List, Optional
from infrastructure.models.permission_model import Permission


class PermissionRepository:
    """Repository for managing permission data access"""
    
    def __init__(self, session):
        self.session = session
    
    def add(self, role_id: int, resource: str, action: str) -> Optional[Permission]:
        """
        Add a new permission
        
        Args:
            role_id: Role ID
            resource: Resource name (Account, Doctor, Clinic, etc.)
            action: Action name (create, read, update, delete)
            
        Returns:
            Permission: Created permission object
            
        Raises:
            ValueError: If permission already exists
        """
        # Check if permission already exists
        if self.check_exists(role_id, resource, action):
            raise ValueError(f"Permission already exists: role={role_id}, {resource}.{action}")
        
        permission = Permission(role_id=role_id, resource=resource, action=action)
        self.session.add(permission)
        self.session.commit()
        return permission
    
    def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return self.session.query(Permission).filter(Permission.permission_id == permission_id).first()
    
    def get_by_role_id(self, role_id: int) -> List[Permission]:
        """Get all permissions for a role"""
        return self.session.query(Permission).filter(Permission.role_id == role_id).all()
    
    def get_by_role_resource(self, role_id: int, resource: str) -> List[Permission]:
        """Get all permissions for a role and resource"""
        return self.session.query(Permission).filter(
            Permission.role_id == role_id,
            Permission.resource == resource
        ).all()
    
    def get_all(self) -> List[Permission]:
        """Get all permissions"""
        return self.session.query(Permission).all()
    
    def check_exists(self, role_id: int, resource: str, action: str) -> bool:
        """Check if permission exists"""
        permission = self.session.query(Permission).filter(
            Permission.role_id == role_id,
            Permission.resource == resource,
            Permission.action == action
        ).first()
        return permission is not None
    
    def delete(self, permission_id: int) -> bool:
        """Delete permission by ID"""
        permission = self.get_by_id(permission_id)
        if not permission:
            return False
        
        self.session.delete(permission)
        self.session.commit()
        return True
    
    def delete_by_role(self, role_id: int) -> bool:
        """Delete all permissions for a role"""
        permissions = self.get_by_role_id(role_id)
        for perm in permissions:
            self.session.delete(perm)
        self.session.commit()
        return True
    
    def delete_by_role_resource(self, role_id: int, resource: str) -> bool:
        """Delete all permissions for a role and resource"""
        permissions = self.get_by_role_resource(role_id, resource)
        for perm in permissions:
            self.session.delete(perm)
        self.session.commit()
        return True
    
    def count_permissions(self) -> int:
        """Count total permissions"""
        return self.session.query(Permission).count()
    
    def count_by_role(self, role_id: int) -> int:
        """Count permissions for a role"""
        return self.session.query(Permission).filter(Permission.role_id == role_id).count()
