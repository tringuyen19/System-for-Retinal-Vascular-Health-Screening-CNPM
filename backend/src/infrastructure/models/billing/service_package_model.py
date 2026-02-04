from sqlalchemy import Column, Integer, String, DECIMAL, Boolean
from infrastructure.databases.base import Base

class ServicePackageModel(Base):
    __tablename__ = 'service_packages'
    __table_args__ = {'extend_existing': True}
    
    package_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(DECIMAL(12, 2), nullable=False)
    image_limit = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    # FR-34: package_type (patient/clinic) and active flag for admin management
    package_type = Column(String(20), nullable=True)  # 'patient' | 'clinic'
    is_active = Column(Boolean, nullable=True)  # default True via migration
    
    def __repr__(self):
        return f"<ServicePackageModel(package_id={self.package_id}, name='{self.name}', price={self.price})>"

