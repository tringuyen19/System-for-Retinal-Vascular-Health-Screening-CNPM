from sqlalchemy import Column, Integer, String
from infrastructure.databases.base import Base

class RoleModel(Base):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(255), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<RoleModel(role_id={self.role_id}, role_name='{self.role_name}')>"

