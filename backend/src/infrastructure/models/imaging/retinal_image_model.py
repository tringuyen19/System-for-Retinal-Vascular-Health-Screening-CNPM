from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class RetinalImageModel(Base):
    __tablename__ = 'retinal_images'
    __table_args__ = {'extend_existing': True}
    
    image_id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey('patient_profiles.patient_id'), nullable=False)
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'), nullable=False)
    uploaded_by = Column(BigInteger, ForeignKey('accounts.account_id'), nullable=False)
    image_type = Column(String(20), nullable=False)
    eye_side = Column(String(20), nullable=False)
    image_url = Column(String(500), nullable=False)
    upload_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f"<RetinalImageModel(image_id={self.image_id}, patient_id={self.patient_id}, eye_side='{self.eye_side}')>"

