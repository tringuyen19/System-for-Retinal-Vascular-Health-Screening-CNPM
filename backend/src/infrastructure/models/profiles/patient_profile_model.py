from sqlalchemy import Column, BigInteger, String, Date, ForeignKey
from infrastructure.databases.base import Base

class PatientProfileModel(Base):
    __tablename__ = 'patient_profiles'
    __table_args__ = {'extend_existing': True}
    
    patient_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'), nullable=False, unique=True)
    patient_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    medical_history = Column(String(1000), nullable=True)
    
    def __repr__(self):
        return f"<PatientProfileModel(patient_id={self.patient_id}, patient_name='{self.patient_name}')>"

