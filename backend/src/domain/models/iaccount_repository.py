from abc import ABC, abstractmethod
from .account import Account
from typing import List, Optional
from datetime import datetime

class IAccountRepository(ABC):
    @abstractmethod
    def add(self, email: str, password_hash: str, role_id: int, 
            clinic_id: Optional[int], status: str, created_at: datetime) -> Account:
        pass

    @abstractmethod
    def get_by_id(self, account_id: int) -> Optional[Account]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Account]:
        pass

    @abstractmethod
    def get_all(self) -> List[Account]:
        pass

    @abstractmethod
    def get_by_role(self, role_id: int) -> List[Account]:
        pass

    @abstractmethod
    def authenticate(self, email: str, password_hash: str) -> Optional[Account]:
        pass

    @abstractmethod
    def update(self, account_id: int, **kwargs) -> Optional[Account]:
        pass

    @abstractmethod
    def update_password(self, account_id: int, new_password_hash: str) -> Optional[Account]:
        pass

    @abstractmethod
    def update_status(self, account_id: int, status: str) -> Optional[Account]:
        pass

    @abstractmethod
    def delete(self, account_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def count_by_role(self, role_id: int) -> int:
        pass

    @abstractmethod
    def check_email_exists(self, email: str) -> bool:
        pass

    @abstractmethod
    def get_by_clinic(self, clinic_id: int) -> List[Account]:
        """Get all accounts in a clinic"""
        pass
