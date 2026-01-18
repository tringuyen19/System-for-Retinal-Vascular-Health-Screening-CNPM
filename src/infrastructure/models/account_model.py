from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class AccountModel(Base):
    __tablename__ = 'accounts'
    __table_args__ = {'extend_existing': True}
    
    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'), nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<AccountModel(account_id={self.account_id}, email='{self.email}')>"

