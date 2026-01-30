from abc import ABC, abstractmethod
from .conversation import Conversation
from typing import List, Optional
from datetime import datetime

class IConversationRepository(ABC):
    @abstractmethod
    def add(self, patient_id: int, doctor_id: int, created_at: datetime, 
            status: str) -> Conversation:
        pass

    @abstractmethod
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        pass

    @abstractmethod
    def get_by_patient(self, patient_id: int) -> List[Conversation]:
        pass

    @abstractmethod
    def get_by_doctor(self, doctor_id: int) -> List[Conversation]:
        pass

    @abstractmethod
    def get_active_by_patient(self, patient_id: int) -> List[Conversation]:
        pass

    @abstractmethod
    def get_active_by_doctor(self, doctor_id: int) -> List[Conversation]:
        pass

    @abstractmethod
    def get_all(self) -> List[Conversation]:
        pass

    @abstractmethod
    def get_or_create_conversation(self, patient_id: int, doctor_id: int) -> Conversation:
        pass

    @abstractmethod
    def close_conversation(self, conversation_id: int) -> Optional[Conversation]:
        pass

    @abstractmethod
    def reopen_conversation(self, conversation_id: int) -> Optional[Conversation]:
        pass

    @abstractmethod
    def update(self, conversation_id: int, **kwargs) -> Optional[Conversation]:
        pass

    @abstractmethod
    def delete(self, conversation_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_patient(self, patient_id: int) -> int:
        pass

    @abstractmethod
    def count_by_doctor(self, doctor_id: int) -> int:
        pass

    @abstractmethod
    def count_active(self) -> int:
        pass

