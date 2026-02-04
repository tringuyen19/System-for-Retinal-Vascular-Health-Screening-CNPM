"""
Role Service - Business Logic Layer
Handles role management operations
"""

from typing import List, Optional
from domain.models.role import Role
from domain.models.irole_repository import IRoleRepository
from infrastructure.repositories.permission_repository import PermissionRepository


class RoleService:
    def __init__(self, repository: IRoleRepository, permission_repository: PermissionRepository = None):
        self.repository = repository
        self.permission_repository = permission_repository
    
    def create_role(self, role_name: str) -> Optional[Role]:
        """Create a new role (with duplicate check)"""
        if self.repository.check_exists(role_name):
            raise ValueError(f"Role '{role_name}' already exists")
        return self.repository.add(role_name)
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return self.repository.get_by_id(role_id)
    
    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get role by name"""
        return self.repository.get_by_name(role_name)
    
    def list_all_roles(self) -> List[Role]:
        """Get all roles"""
        return self.repository.get_all()
    
    def update_role(self, role_id: int, role_name: str) -> Optional[Role]:
        """Update role name"""
        return self.repository.update(role_id, role_name)
    
    def delete_role(self, role_id: int) -> bool:
        """Delete role"""
        return self.repository.delete(role_id)
    
    def count_roles(self) -> int:
        """Count total roles"""
        return self.repository.count()
    
    def check_role_exists(self, role_name: str) -> bool:
        """Check if role exists"""
        return self.repository.check_exists(role_name)
    
    def ensure_default_roles(self) -> None:
        """Ensure default roles exist (Admin, Doctor, Patient, ClinicManager)"""
        default_roles = ['Admin', 'Doctor', 'Patient', 'ClinicManager']
        for role_name in default_roles:
            if not self.repository.check_exists(role_name):
                self.repository.add(role_name)
    
    # ========== Permission Management Methods (FR-32) ==========
    
    def assign_permission(self, role_id: int, resource: str, action: str) -> Optional[dict]:
        """
        Assign a permission to a role
        
        Args:
            role_id: Role ID
            resource: Resource name (Account, Doctor, Clinic, etc.)
            action: Action name (create, read, update, delete)
            
        Returns:
            dict: Permission info {permission_id, role_id, resource, action}
            
        Raises:
            ValueError: If role doesn't exist or permission already exists
        """
        if not self.permission_repository:
            raise RuntimeError("Permission repository not configured")
        
        # Verify role exists
        if not self.get_role_by_id(role_id):
            raise ValueError(f"Role {role_id} does not exist")
        
        # Assign permission
        permission = self.permission_repository.add(role_id, resource, action)
        if not permission:
            raise RuntimeError("Failed to create permission")
        
        return permission.to_dict()
    
    def get_role_permissions(self, role_id: int) -> List[dict]:
        """
        Get all permissions for a role
        
        Args:
            role_id: Role ID
            
        Returns:
            List[dict]: List of permissions [{resource, action, ...}]
        """
        if not self.permission_repository:
            raise RuntimeError("Permission repository not configured")
        
        permissions = self.permission_repository.get_by_role_id(role_id)
        return [p.to_dict() for p in permissions]
    
    def revoke_permission(self, role_id: int, resource: str, action: str) -> bool:
        """
        Revoke a permission from a role
        
        Args:
            role_id: Role ID
            resource: Resource name
            action: Action name
            
        Returns:
            bool: True if revoked successfully
        """
        if not self.permission_repository:
            raise RuntimeError("Permission repository not configured")
        
        # Find the permission
        perms = self.permission_repository.get_by_role_resource(role_id, resource)
        for perm in perms:
            if perm.action == action:
                return self.permission_repository.delete(perm.permission_id)
        
        return False
    
    def has_permission(self, role_id: int, resource: str, action: str) -> bool:
        """
        Check if a role has a specific permission
        
        Args:
            role_id: Role ID
            resource: Resource name
            action: Action name
            
        Returns:
            bool: True if role has permission
        """
        if not self.permission_repository:
            return False
        
        return self.permission_repository.check_exists(role_id, resource, action)
    
    def revoke_all_permissions(self, role_id: int) -> bool:
        """Revoke all permissions for a role"""
        if not self.permission_repository:
            raise RuntimeError("Permission repository not configured")
        
        return self.permission_repository.delete_by_role(role_id)


