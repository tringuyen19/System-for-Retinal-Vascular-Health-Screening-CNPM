from sqlalchemy import Column, Integer, BigInteger, String, Date, ForeignKey
from infrastructure.databases.base import Base

class SubscriptionModel(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = {'extend_existing': True}
    
    subscription_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'), nullable=False)
    package_id = Column(Integer, ForeignKey('service_packages.package_id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    remaining_credits = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f"<SubscriptionModel(subscription_id={self.subscription_id}, account_id={self.account_id}, status='{self.status}')>"

