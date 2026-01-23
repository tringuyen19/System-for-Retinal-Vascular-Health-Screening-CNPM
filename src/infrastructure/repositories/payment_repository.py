from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from infrastructure.databases.mssql import session
from infrastructure.models.billing.payment_model import PaymentModel
from domain.models.payment import Payment
from domain.models.ipayment_repository import IPaymentRepository


class PaymentRepository(IPaymentRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: PaymentModel) -> Payment:
        return Payment(
            payment_id=model.payment_id, subscription_id=model.subscription_id,
            amount=model.amount, payment_method=model.payment_method,
            payment_time=model.payment_time, status=model.status
        )
    
    def add(self, subscription_id: int, amount: Decimal, payment_method: str,
            payment_time: datetime, status: str) -> Payment:
        try:
            payment_model = PaymentModel(
                subscription_id=subscription_id, amount=amount, payment_method=payment_method,
                payment_time=payment_time, status=status
            )
            self.session.add(payment_model)
            self.session.commit()
            self.session.refresh(payment_model)
            return self._to_domain(payment_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating payment: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        try:
            payment_model = self.session.query(PaymentModel).filter_by(payment_id=payment_id).first()
            return self._to_domain(payment_model) if payment_model else None
        except Exception as e:
            raise ValueError(f'Error getting payment: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_subscription(self, subscription_id: int) -> List[Payment]:
        try:
            payment_models = self.session.query(PaymentModel).filter_by(subscription_id=subscription_id).all()
            return [self._to_domain(model) for model in payment_models]
        except Exception as e:
            raise ValueError(f'Error getting payments by subscription: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_status(self, status: str) -> List[Payment]:
        try:
            payment_models = self.session.query(PaymentModel).filter_by(status=status).all()
            return [self._to_domain(model) for model in payment_models]
        except Exception as e:
            raise ValueError(f'Error getting payments by status: {str(e)}')
        finally:
            self.session.close()
    
    def get_pending(self) -> List[Payment]:
        return self.get_by_status('pending')
    
    def get_all(self) -> List[Payment]:
        try:
            payment_models = self.session.query(PaymentModel).all()
            return [self._to_domain(model) for model in payment_models]
        except Exception as e:
            raise ValueError(f'Error getting all payments: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_completed(self, payment_id: int) -> Optional[Payment]:
        try:
            payment_model = self.session.query(PaymentModel).filter_by(payment_id=payment_id).first()
            if not payment_model:
                return None
            payment_model.status = 'completed'
            self.session.commit()
            self.session.refresh(payment_model)
            return self._to_domain(payment_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking payment as completed: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_failed(self, payment_id: int) -> Optional[Payment]:
        try:
            payment_model = self.session.query(PaymentModel).filter_by(payment_id=payment_id).first()
            if not payment_model:
                return None
            payment_model.status = 'failed'
            self.session.commit()
            self.session.refresh(payment_model)
            return self._to_domain(payment_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking payment as failed: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, payment_id: int, **kwargs) -> Optional[Payment]:
        try:
            payment_model = self.session.query(PaymentModel).filter_by(payment_id=payment_id).first()
            if not payment_model:
                return None
            for key, value in kwargs.items():
                if hasattr(payment_model, key) and key not in ['payment_id', 'payment_time']:
                    setattr(payment_model, key, value)
            self.session.commit()
            self.session.refresh(payment_model)
            return self._to_domain(payment_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating payment: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, payment_id: int) -> bool:
        try:
            payment_model = self.session.query(PaymentModel).filter_by(payment_id=payment_id).first()
            if not payment_model:
                return False
            self.session.delete(payment_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting payment: {str(e)}')
        finally:
            self.session.close()
    
    def get_total_revenue(self, status: str) -> Decimal:
        try:
            total = self.session.query(func.sum(PaymentModel.amount)).filter_by(status=status).scalar()
            return Decimal(total) if total else Decimal(0)
        except Exception as e:
            raise ValueError(f'Error getting total revenue: {str(e)}')
        finally:
            self.session.close()
    
    def get_revenue_by_date_range(self, start_date: date, end_date: date) -> Decimal:
        try:
            total = self.session.query(func.sum(PaymentModel.amount)).filter(
                PaymentModel.payment_time >= start_date,
                PaymentModel.payment_time <= end_date,
                PaymentModel.status == 'completed'
            ).scalar()
            return Decimal(total) if total else Decimal(0)
        except Exception as e:
            raise ValueError(f'Error getting revenue by date range: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_status(self, status: str) -> int:
        try:
            return self.session.query(PaymentModel).filter_by(status=status).count()
        except Exception as e:
            raise ValueError(f'Error counting payments by status: {str(e)}')
        finally:
            self.session.close()
