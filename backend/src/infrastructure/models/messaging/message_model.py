from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from infrastructure.databases.base import Base

class MessageModel(Base):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}
    
    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.conversation_id'), nullable=False)
    sender_type = Column(String(20), nullable=False)
    sender_name = Column(String(255), nullable=False)
    content = Column(String(2000), nullable=False)
    message_type = Column(String(20), nullable=False)
    sent_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<MessageModel(message_id={self.message_id}, sender_name='{self.sender_name}', sender_type='{self.sender_type}')>"

