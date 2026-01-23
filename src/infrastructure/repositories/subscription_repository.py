from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.billing.subscription_model import SubscriptionModel
from domain.models.subscription import Subscription
from domain.models.isubscription_repository import ISubscriptionRepository


class SubscriptionRepository(ISubscriptionRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: SubscriptionModel) -> Subscription:
        return Subscription(
            subscription_id=model.subscription_id, account_id=model.account_id, package_id=model.package_id,
            start_date=model.start_date, end_date=model.end_date,
            remaining_credits=model.remaining_credits, status=model.status
        )
    
    def add(self, account_id: int, package_id: int, start_date: date, end_date: date,
            remaining_credits: int, status: str) -> Subscription:
        try:
            sub_model = SubscriptionModel(
                account_id=account_id, package_id=package_id, start_date=start_date,
                end_date=end_date, remaining_credits=remaining_credits, status=status
            )
            self.session.add(sub_model)
            self.session.commit()
            self.session.refresh(sub_model)
            return self._to_domain(sub_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating subscription: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(subscription_id=subscription_id).first()
            return self._to_domain(sub_model) if sub_model else None
        except Exception as e:
            raise ValueError(f'Error getting subscription: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_account(self, account_id: int) -> List[Subscription]:
        try:
            sub_models = self.session.query(SubscriptionModel).filter_by(account_id=account_id).all()
            return [self._to_domain(model) for model in sub_models]
        except Exception as e:
            raise ValueError(f'Error getting subscriptions by account: {str(e)}')
        finally:
            self.session.close()
    
    def get_active_by_account(self, account_id: int) -> Optional[Subscription]:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(
                account_id=account_id, status='active'
            ).first()
            return self._to_domain(sub_model) if sub_model else None
        except Exception as e:
            raise ValueError(f'Error getting active subscription: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_status(self, status: str) -> List[Subscription]:
        try:
            sub_models = self.session.query(SubscriptionModel).filter_by(status=status).all()
            return [self._to_domain(model) for model in sub_models]
        except Exception as e:
            raise ValueError(f'Error getting subscriptions by status: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[Subscription]:
        try:
            sub_models = self.session.query(SubscriptionModel).all()
            return [self._to_domain(model) for model in sub_models]
        except Exception as e:
            raise ValueError(f'Error getting all subscriptions: {str(e)}')
        finally:
            self.session.close()
    
    def get_expiring_soon(self, days: int) -> List[Subscription]:
        try:
            expiry_date = date.today() + timedelta(days=days)
            sub_models = self.session.query(SubscriptionModel).filter(
                SubscriptionModel.status == 'active',
                SubscriptionModel.end_date <= expiry_date,
                SubscriptionModel.end_date >= date.today()
            ).all()
            return [self._to_domain(model) for model in sub_models]
        except Exception as e:
            raise ValueError(f'Error getting expiring subscriptions: {str(e)}')
        finally:
            self.session.close()
    
    def deduct_credit(self, subscription_id: int, amount: int) -> Optional[Subscription]:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(subscription_id=subscription_id).first()
            if not sub_model:
                return None
            sub_model.remaining_credits -= amount
            self.session.commit()
            self.session.refresh(sub_model)
            return self._to_domain(sub_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deducting credit: {str(e)}')
        finally:
            self.session.close()
    
    def renew_subscription(self, subscription_id: int, new_end_date: date, additional_credits: int) -> Optional[Subscription]:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(subscription_id=subscription_id).first()
            if not sub_model:
                return None
            sub_model.end_date = new_end_date
            sub_model.remaining_credits += additional_credits
            sub_model.status = 'active'
            self.session.commit()
            self.session.refresh(sub_model)
            return self._to_domain(sub_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error renewing subscription: {str(e)}')
        finally:
            self.session.close()
    
    def cancel_subscription(self, subscription_id: int) -> Optional[Subscription]:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(subscription_id=subscription_id).first()
            if not sub_model:
                return None
            sub_model.status = 'cancelled'
            self.session.commit()
            self.session.refresh(sub_model)
            return self._to_domain(sub_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error cancelling subscription: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, subscription_id: int, **kwargs) -> Optional[Subscription]:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(subscription_id=subscription_id).first()
            if not sub_model:
                return None
            for key, value in kwargs.items():
                if hasattr(sub_model, key) and key != 'subscription_id':
                    setattr(sub_model, key, value)
            self.session.commit()
            self.session.refresh(sub_model)
            return self._to_domain(sub_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating subscription: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, subscription_id: int) -> bool:
        try:
            sub_model = self.session.query(SubscriptionModel).filter_by(subscription_id=subscription_id).first()
            if not sub_model:
                return False
            self.session.delete(sub_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting subscription: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_status(self, status: str) -> int:
        try:
            return self.session.query(SubscriptionModel).filter_by(status=status).count()
        except Exception as e:
            raise ValueError(f'Error counting subscriptions by status: {str(e)}')
        finally:
            self.session.close()
