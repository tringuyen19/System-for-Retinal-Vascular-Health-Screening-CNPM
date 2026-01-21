from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class DoctorReviewModel(Base):
    __tablename__ = 'doctor_reviews'
    __table_args__ = {'extend_existing': True}
    
    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id = Column(BigInteger, ForeignKey('ai_analysis.analysis_id'), nullable=False, unique=True)
    doctor_id = Column(BigInteger, ForeignKey('doctor_profiles.doctor_id'), nullable=False)
    validation_status = Column(String(20), nullable=False)
    comment = Column(String(1000), nullable=True)
    reviewed_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<DoctorReviewModel(review_id={self.review_id}, doctor_id={self.doctor_id}, validation_status='{self.validation_status}')>"

