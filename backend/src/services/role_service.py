"""
Role Service - Business Logic Layer
Handles role management operations
"""

from typing import List, Optional
from domain.models.role import Role
from domain.models.irole_repository import IRoleRepository


class RoleService:
    def __init__(self, repository: IRoleRepository):
        self.repository = repository
    
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

