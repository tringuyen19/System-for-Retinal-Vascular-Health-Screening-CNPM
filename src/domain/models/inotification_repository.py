from abc import ABC, abstractmethod
from .notification import Notification
from typing import List, Optional
from datetime import datetime

class INotificationRepository(ABC):
    @abstractmethod
    def send_notification(self, account_id: int, notification_type: str, 
                         content: str, created_at: datetime) -> Notification:
        pass

    @abstractmethod
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        pass

    @abstractmethod
    def get_by_account(self, account_id: int) -> List[Notification]:
        pass

    @abstractmethod
    def get_unread_by_account(self, account_id: int) -> List[Notification]:
        pass

    @abstractmethod
    def get_recent_by_account(self, account_id: int, limit: int) -> List[Notification]:
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        pass

    @abstractmethod
    def mark_all_as_read(self, account_id: int) -> bool:
        pass

    @abstractmethod
    def delete(self, notification_id: int) -> bool:
        pass

    @abstractmethod
    def delete_all_by_account(self, account_id: int) -> bool:
        pass

    @abstractmethod
    def count_unread(self, account_id: int) -> int:
        pass

    @abstractmethod
    def count_by_type(self, account_id: int, notification_type: str) -> int:
        pass

