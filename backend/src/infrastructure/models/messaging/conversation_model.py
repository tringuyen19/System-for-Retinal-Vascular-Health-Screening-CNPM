from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class ConversationModel(Base):
    __tablename__ = 'conversations'
    __table_args__ = {'extend_existing': True}
    
    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey('patient_profiles.patient_id'), nullable=False)
    doctor_id = Column(BigInteger, ForeignKey('doctor_profiles.doctor_id'), nullable=False)
    created_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f"<ConversationModel(conversation_id={self.conversation_id}, patient_id={self.patient_id}, doctor_id={self.doctor_id})>"

