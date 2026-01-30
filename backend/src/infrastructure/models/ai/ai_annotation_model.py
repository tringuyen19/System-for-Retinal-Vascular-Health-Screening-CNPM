from sqlalchemy import Column, BigInteger, String, ForeignKey
from infrastructure.databases.base import Base

class AiAnnotationModel(Base):
    __tablename__ = 'ai_annotations'
    __table_args__ = {'extend_existing': True}
    
    annotation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    analysis_id = Column(BigInteger, ForeignKey('ai_analysis.analysis_id'), nullable=False)
    heatmap_url = Column(String(500), nullable=False)
    description = Column(String(1000), nullable=True)
    
    def __repr__(self):
        return f"<AiAnnotationModel(annotation_id={self.annotation_id}, analysis_id={self.analysis_id})>"

