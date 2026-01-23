from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.databases.base import Base

class ClinicModel(Base):
    __tablename__ = 'clinics'
    __table_args__ = {'extend_existing': True}
    
    clinic_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=False)
    phone = Column(String(50), nullable=False)
    logo_url = Column(String(255), nullable=False)
    verification_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ClinicModel(clinic_id={self.clinic_id}, name='{self.name}')>"

