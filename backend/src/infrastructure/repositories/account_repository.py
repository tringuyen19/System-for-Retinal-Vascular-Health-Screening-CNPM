from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from infrastructure.databases.mssql import session
from infrastructure.models.account_model import AccountModel
from domain.models.account import Account
from domain.models.iaccount_repository import IAccountRepository


class AccountRepository(IAccountRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: AccountModel) -> Account:
        """Convert AccountModel (Infrastructure) to Account (Domain)"""
        return Account(
            account_id=model.account_id,
            email=model.email,
            password_hash=model.password_hash,
            role_id=model.role_id,
            clinic_id=model.clinic_id,
            status=model.status,
            created_at=model.created_at
        )
    
    def add(self, email: str, password_hash: str, role_id: int, 
            clinic_id: Optional[int] = None, status: str = 'active', 
            created_at: datetime = None) -> Account:
        """Create a new account"""
        try:
            account_model = AccountModel(
                email=email,
                password_hash=password_hash,
                role_id=role_id,
                clinic_id=clinic_id,
                status=status,
                created_at=created_at or datetime.now()
            )
            self.session.add(account_model)
            self.session.commit()
            self.session.refresh(account_model)
            return self._to_domain(account_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating account: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        try:
            account_model = self.session.query(AccountModel).filter_by(account_id=account_id).first()
            return self._to_domain(account_model) if account_model else None
        except Exception as e:
            raise ValueError(f'Error getting account: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_email(self, email: str) -> Optional[Account]:
        """Get account by email"""
        try:
            account_model = self.session.query(AccountModel).filter_by(email=email).first()
            return self._to_domain(account_model) if account_model else None
        except Exception as e:
            raise ValueError(f'Error getting account by email: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[Account]:
        """Get all accounts"""
        try:
            account_models = self.session.query(AccountModel).all()
            return [self._to_domain(model) for model in account_models]
        except Exception as e:
            raise ValueError(f'Error getting all accounts: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_role(self, role_id: int) -> List[Account]:
        """Get accounts by role"""
        try:
            account_models = self.session.query(AccountModel).filter_by(role_id=role_id).all()
            return [self._to_domain(model) for model in account_models]
        except Exception as e:
            raise ValueError(f'Error getting accounts by role: {str(e)}')
        finally:
            self.session.close()
    
    def authenticate(self, email: str, password_hash: str) -> Optional[Account]:
        """Authenticate account"""
        try:
            account_model = self.session.query(AccountModel).filter_by(
                email=email,
                password_hash=password_hash
            ).first()
            return self._to_domain(account_model) if account_model else None
        except Exception as e:
            raise ValueError(f'Error authenticating account: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, account_id: int, **kwargs) -> Optional[Account]:
        """Update account fields"""
        try:
            account_model = self.session.query(AccountModel).filter_by(account_id=account_id).first()
            if not account_model:
                return None
            
            for key, value in kwargs.items():
                if hasattr(account_model, key) and key != 'account_id' and key != 'created_at':
                    setattr(account_model, key, value)
            
            self.session.commit()
            self.session.refresh(account_model)
            return self._to_domain(account_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating account: {str(e)}')
        finally:
            self.session.close()
    
    def update_password(self, account_id: int, new_password_hash: str) -> Optional[Account]:
        """Update account password"""
        try:
            account_model = self.session.query(AccountModel).filter_by(account_id=account_id).first()
            if not account_model:
                return None
            
            account_model.password_hash = new_password_hash
            self.session.commit()
            self.session.refresh(account_model)
            return self._to_domain(account_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating password: {str(e)}')
        finally:
            self.session.close()
    
    def update_status(self, account_id: int, status: str) -> Optional[Account]:
        """Update account status"""
        try:
            account_model = self.session.query(AccountModel).filter_by(account_id=account_id).first()
            if not account_model:
                return None
            
            account_model.status = status
            self.session.commit()
            self.session.refresh(account_model)
            return self._to_domain(account_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating status: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, account_id: int) -> bool:
        """Delete account"""
        try:
            account_model = self.session.query(AccountModel).filter_by(account_id=account_id).first()
            if not account_model:
                return False
            
            self.session.delete(account_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting account: {str(e)}')
        finally:
            self.session.close()
    
    def count(self) -> int:
        """Count total accounts"""
        try:
            return self.session.query(AccountModel).count()
        except Exception as e:
            raise ValueError(f'Error counting accounts: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_role(self, role_id: int) -> int:
        """Count accounts by role"""
        try:
            return self.session.query(AccountModel).filter_by(role_id=role_id).count()
        except Exception as e:
            raise ValueError(f'Error counting accounts by role: {str(e)}')
        finally:
            self.session.close()
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email exists"""
        try:
            account_model = self.session.query(AccountModel).filter_by(email=email).first()
            return account_model is not None
        except Exception as e:
            raise ValueError(f'Error checking email existence: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_clinic(self, clinic_id: int) -> List[Account]:
        """Get all accounts in a clinic"""
        try:
            account_models = self.session.query(AccountModel).filter_by(clinic_id=clinic_id).all()
            return [self._to_domain(model) for model in account_models]
        except Exception as e:
            raise ValueError(f'Error getting accounts by clinic: {str(e)}')
        finally:
            self.session.close()