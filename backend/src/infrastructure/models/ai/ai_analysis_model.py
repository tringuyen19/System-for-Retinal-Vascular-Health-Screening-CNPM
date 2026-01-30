from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class AiAnalysisModel(Base):
    __tablename__ = 'ai_analysis'
    __table_args__ = {'extend_existing': True}
    
    analysis_id = Column(BigInteger, primary_key=True, autoincrement=True)
    image_id = Column(BigInteger, ForeignKey('retinal_images.image_id'), nullable=False, unique=True)
    ai_model_version_id = Column(Integer, ForeignKey('ai_model_versions.ai_model_version_id'), nullable=False)
    analysis_time = Column(DateTime, nullable=False)
    processing_time = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f"<AiAnalysisModel(analysis_id={self.analysis_id}, image_id={self.image_id}, status='{self.status}')>"

