from abc import ABC, abstractmethod
from .message import Message
from typing import List, Optional
from datetime import datetime

class IMessageRepository(ABC):
    @abstractmethod
    def add(self, conversation_id: int, sender_type: str, sender_name: str, 
            content: str, message_type: str, sent_at: datetime) -> Message:
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[Message]:
        pass

    @abstractmethod
    def get_by_conversation(self, conversation_id: int) -> List[Message]:
        pass

    @abstractmethod
    def get_last_message(self, conversation_id: int) -> Optional[Message]:
        pass

    @abstractmethod
    def get_by_sender(self, conversation_id: int, sender_type: str) -> List[Message]:
        pass

    @abstractmethod
    def search_messages(self, conversation_id: int, search_term: str) -> List[Message]:
        pass

    @abstractmethod
    def update(self, message_id: int, **kwargs) -> Optional[Message]:
        pass

    @abstractmethod
    def delete(self, message_id: int) -> bool:
        pass

    @abstractmethod
    def delete_all_by_conversation(self, conversation_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_conversation(self, conversation_id: int) -> int:
        pass

    @abstractmethod
    def count_by_sender(self, conversation_id: int, sender_type: str) -> int:
        pass

