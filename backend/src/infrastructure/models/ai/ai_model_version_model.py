from sqlalchemy import Column, Integer, String, DateTime, Boolean
from infrastructure.databases.base import Base

class AiModelVersionModel(Base):
    __tablename__ = 'ai_model_versions'
    __table_args__ = {'extend_existing': True}
    
    ai_model_version_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    threshold_config = Column(String(1000), nullable=False)
    trained_at = Column(DateTime, nullable=False)
    active_flag = Column(Boolean, nullable=False)
    
    def __repr__(self):
        return f"<AiModelVersionModel(ai_model_version_id={self.ai_model_version_id}, model_name='{self.model_name}', version='{self.version}')>"

