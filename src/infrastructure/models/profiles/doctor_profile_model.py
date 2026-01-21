from sqlalchemy import Column, BigInteger, String, ForeignKey
from infrastructure.databases.base import Base

class DoctorProfileModel(Base):
    __tablename__ = 'doctor_profiles'
    __table_args__ = {'extend_existing': True}
    
    doctor_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'), nullable=False, unique=True)
    doctor_name = Column(String(255), nullable=False)
    specialization = Column(String(255), nullable=False)
    license_number = Column(String(100), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<DoctorProfileModel(doctor_id={self.doctor_id}, doctor_name='{self.doctor_name}')>"

