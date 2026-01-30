from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from infrastructure.databases.base import Base

class NotificationModel(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'extend_existing': True}
    
    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'), nullable=False)
    type = Column(String(50), nullable=False)
    content = Column(String(1000), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<NotificationModel(notification_id={self.notification_id}, account_id={self.account_id}, type='{self.type}')>"

