from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class MedicalReportModel(Base):
    __tablename__ = 'medical_reports'
    __table_args__ = {'extend_existing': True}
    
    report_id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey('patient_profiles.patient_id'), nullable=False)
    analysis_id = Column(BigInteger, ForeignKey('ai_analysis.analysis_id'), nullable=False, unique=True)
    doctor_id = Column(BigInteger, ForeignKey('doctor_profiles.doctor_id'), nullable=False)
    report_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<MedicalReportModel(report_id={self.report_id}, patient_id={self.patient_id}, doctor_id={self.doctor_id})>"

