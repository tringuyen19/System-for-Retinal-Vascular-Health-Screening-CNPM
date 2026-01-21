from sqlalchemy import Column, BigInteger, String, DECIMAL, ForeignKey
from infrastructure.databases.base import Base

class AiResultModel(Base):
    __tablename__ = 'ai_results'
    __table_args__ = {'extend_existing': True}
    
    result_id = Column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id = Column(BigInteger, ForeignKey('ai_analysis.analysis_id'), nullable=False)
    disease_type = Column(String(100), nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence_score = Column(DECIMAL(5, 2), nullable=False)
    
    def __repr__(self):
        return f"<AiResultModel(result_id={self.result_id}, disease_type='{self.disease_type}', risk_level='{self.risk_level}')>"

