from abc import ABC, abstractmethod
from .subscription import Subscription
from typing import List, Optional
from datetime import date

class ISubscriptionRepository(ABC):
    @abstractmethod
    def add(self, account_id: int, package_id: int, start_date: date, 
            end_date: date, remaining_credits: int, status: str) -> Subscription:
        pass

    @abstractmethod
    def get_by_id(self, subscription_id: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    def get_by_account(self, account_id: int) -> List[Subscription]:
        pass

    @abstractmethod
    def get_active_by_account(self, account_id: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Subscription]:
        pass

    @abstractmethod
    def get_all(self) -> List[Subscription]:
        pass

    @abstractmethod
    def get_expiring_soon(self, days: int) -> List[Subscription]:
        pass

    @abstractmethod
    def deduct_credit(self, subscription_id: int, amount: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    def renew_subscription(self, subscription_id: int, new_end_date: date, 
                          additional_credits: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    def update(self, subscription_id: int, **kwargs) -> Optional[Subscription]:
        pass

    @abstractmethod
    def delete(self, subscription_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_status(self, status: str) -> int:
        pass

