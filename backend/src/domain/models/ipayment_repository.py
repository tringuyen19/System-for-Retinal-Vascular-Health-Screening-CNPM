from abc import ABC, abstractmethod
from .payment import Payment
from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal

class IPaymentRepository(ABC):
    @abstractmethod
    def add(self, subscription_id: int, amount: Decimal, payment_method: str, 
            payment_time: datetime, status: str) -> Payment:
        pass

    @abstractmethod
    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    def get_by_subscription(self, subscription_id: int) -> List[Payment]:
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Payment]:
        pass

    @abstractmethod
    def get_pending(self) -> List[Payment]:
        pass

    @abstractmethod
    def get_all(self) -> List[Payment]:
        pass

    @abstractmethod
    def mark_as_completed(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    def mark_as_failed(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    def update(self, payment_id: int, **kwargs) -> Optional[Payment]:
        pass

    @abstractmethod
    def delete(self, payment_id: int) -> bool:
        pass

    @abstractmethod
    def get_total_revenue(self, status: str) -> Decimal:
        pass

    @abstractmethod
    def get_revenue_by_date_range(self, start_date: date, end_date: date) -> Decimal:
        pass

    @abstractmethod
    def count_by_status(self, status: str) -> int:
        pass

