from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.role_model import RoleModel
from domain.models.role import Role
from domain.models.irole_repository import IRoleRepository


class RoleRepository(IRoleRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: RoleModel) -> Role:
        """Convert RoleModel (Infrastructure) to Role (Domain)"""
        return Role(
            role_id=model.role_id,
            role_name=model.role_name
        )
    
    def add(self, role_name: str) -> Role:
        """Create a new role"""
        try:
            role_model = RoleModel(role_name=role_name)
            self.session.add(role_model)
            self.session.commit()
            self.session.refresh(role_model)
            return self._to_domain(role_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating role: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        try:
            role_model = self.session.query(RoleModel).filter_by(role_id=role_id).first()
            return self._to_domain(role_model) if role_model else None
        except Exception as e:
            raise ValueError(f'Error getting role: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_name(self, role_name: str) -> Optional[Role]:
        """Get role by name"""
        try:
            role_model = self.session.query(RoleModel).filter_by(role_name=role_name).first()
            return self._to_domain(role_model) if role_model else None
        except Exception as e:
            raise ValueError(f'Error getting role by name: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[Role]:
        """Get all roles"""
        try:
            role_models = self.session.query(RoleModel).all()
            return [self._to_domain(model) for model in role_models]
        except Exception as e:
            raise ValueError(f'Error getting all roles: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, role_id: int, role_name: str) -> Optional[Role]:
        """Update role"""
        try:
            role_model = self.session.query(RoleModel).filter_by(role_id=role_id).first()
            if not role_model:
                return None
            
            role_model.role_name = role_name
            self.session.commit()
            self.session.refresh(role_model)
            return self._to_domain(role_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating role: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, role_id: int) -> bool:
        """Delete role"""
        try:
            role_model = self.session.query(RoleModel).filter_by(role_id=role_id).first()
            if not role_model:
                return False
            
            self.session.delete(role_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting role: {str(e)}')
        finally:
            self.session.close()
    
    def count(self) -> int:
        """Count total roles"""
        try:
            return self.session.query(RoleModel).count()
        except Exception as e:
            raise ValueError(f'Error counting roles: {str(e)}')
        finally:
            self.session.close()
    
    def check_exists(self, role_name: str) -> bool:
        """Check if role exists by name"""
        try:
            role_model = self.session.query(RoleModel).filter_by(role_name=role_name).first()
            return role_model is not None
        except Exception as e:
            raise ValueError(f'Error checking role existence: {str(e)}')
        finally:
            self.session.close()
