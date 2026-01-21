from sqlalchemy import Column, BigInteger, String, DateTime, DECIMAL, ForeignKey
from infrastructure.databases.base import Base

class PaymentModel(Base):
    __tablename__ = 'payments'
    __table_args__ = {'extend_existing': True}
    
    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    subscription_id = Column(BigInteger, ForeignKey('subscriptions.subscription_id'), nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False)
    
    def __repr__(self):
        return f"<PaymentModel(payment_id={self.payment_id}, amount={self.amount}, status='{self.status}')>"

