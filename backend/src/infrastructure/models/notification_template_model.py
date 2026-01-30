from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Text
from infrastructure.databases.base import Base

class NotificationTemplateModel(Base):
    """SQLAlchemy model for notification_templates table - Infrastructure layer"""
    __tablename__ = 'notification_templates'
    __table_args__ = {'extend_existing': True}
    
    template_id = Column(BigInteger, primary_key=True, autoincrement=True)
    template_name = Column(String(100), nullable=False, unique=True)
    template_type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=True)
    content_template = Column(Text, nullable=False)  # NVARCHAR(MAX) in SQL
    variables_schema = Column(Text, nullable=True)    # JSON string
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<NotificationTemplateModel(template_id={self.template_id}, template_name='{self.template_name}')>"