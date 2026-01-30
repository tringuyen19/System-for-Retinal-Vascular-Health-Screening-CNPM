"""
Account Service - Business Logic Layer
Handles account management and authentication
"""

from typing import List, Optional
from datetime import datetime
import bcrypt
from domain.models.account import Account
from domain.models.iaccount_repository import IAccountRepository
from domain.exceptions import NotFoundException, ValidationException, ConflictException
from domain.validators import AccountValidator


class AccountService:
    def __init__(self, repository: IAccountRepository):
        self.repository = repository
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt (business logic)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def register_account(self, email: str, password: str, role_id: int, 
                        clinic_id: Optional[int] = None, status: str = 'active') -> Account:
        """
        Register new account with validation and password hashing
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            role_id: Role ID (1=Admin, 2=Doctor, 3=Patient, 4=ClinicManager)
            clinic_id: Optional clinic ID
            status: Account status (default: 'active')
            
        Returns:
            Account: Created account domain model
            
        Raises:
            ValidationException: If email or password is invalid
            ConflictException: If email already exists
        """
        # 1. Validate input using domain validators
        AccountValidator.validate_email(email)
        AccountValidator.validate_password(password)
        
        # 2. Check email duplicate (business rule)
        if self.repository.check_email_exists(email):
            raise ConflictException(f"Email '{email}' already exists")
        
        # 3. Hash password (business logic - moved from controller)
        password_hash = self._hash_password(password)
        
        # 4. Create account
        account = self.repository.add(
            email=email,
            password_hash=password_hash,
            role_id=role_id,
            clinic_id=clinic_id,
            status=status,
            created_at=datetime.now()
        )
        
        if not account:
            raise ValueError("Failed to create account")
        
        return account
    
    def authenticate(self, email: str, password: str) -> Account:
        """
        Authenticate user with email and password
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            Account: Authenticated account domain model
            
        Raises:
            ValidationException: If credentials are invalid
            NotFoundException: If account not found
        """
        # 1. Get account by email
        account = self.repository.get_by_email(email)
        if not account:
            raise NotFoundException("Invalid email or password")
        
        # 2. Check account status
        if account.status != 'active':
            raise ValidationException("Account is not active. Please contact administrator.")
        
        # 3. Verify password (business logic - moved from controller)
        if not self._verify_password(password, account.password_hash):
            raise ValidationException("Invalid email or password")
        
        return account
    
    def get_account_by_id(self, account_id: int) -> Account:
        """
        Get account by ID
        
        Raises:
            NotFoundException: If account not found
        """
        account = self.repository.get_by_id(account_id)
        if not account:
            raise NotFoundException(f"Account {account_id} not found")
        return account
    
    def get_account_by_email(self, email: str) -> Account:
        """
        Get account by email
        
        Raises:
            NotFoundException: If account not found
        """
        account = self.repository.get_by_email(email)
        if not account:
            raise NotFoundException(f"Account with email '{email}' not found")
        return account
    
    def list_all_accounts(self) -> List[Account]:
        """Get all accounts"""
        return self.repository.get_all()
    
    def get_accounts_by_role(self, role_id: int) -> List[Account]:
        """Get accounts by role"""
        return self.repository.get_by_role(role_id)
    
    def update_account(self, account_id: int, **kwargs) -> Optional[Account]:
        """Update account"""
        return self.repository.update(account_id, **kwargs)
    
    def change_password(self, account_id: int, new_password_hash: str) -> Optional[Account]:
        """Change account password"""
        return self.repository.update_password(account_id, new_password_hash)
    
    def update_status(self, account_id: int, status: str) -> Optional[Account]:
        """Update account status"""
        return self.repository.update_status(account_id, status)
    
    def delete_account(self, account_id: int) -> bool:
        """Delete account"""
        return self.repository.delete(account_id)
    
    def count_accounts(self) -> int:
        """Count total accounts"""
        return self.repository.count()
    
    def count_by_role(self, role_id: int) -> int:
        """Count accounts by role"""
        return self.repository.count_by_role(role_id)
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.repository.check_email_exists(email)
    
    def create_account(self, email: str, password: str, role_id: int,
                      clinic_id: Optional[int] = None, status: str = 'active') -> Account:
        """
        Create account (alias for register_account)
        Note: Now accepts plain password instead of password_hash
        """
        return self.register_account(email, password, role_id, clinic_id, status)
    
    def update_password(self, account_id: int, new_password_hash: str) -> Optional[Account]:
        """Update password (alias for change_password)"""
        return self.change_password(account_id, new_password_hash)

    def get_accounts_by_clinic(self, clinic_id: int) -> List[Account]:
        """Get all accounts in a clinic"""
        return self.repository.get_by_clinic(clinic_id)