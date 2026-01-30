from abc import ABC, abstractmethod
from .clinic import Clinic
from typing import List, Optional
from datetime import datetime

class IClinicRepository(ABC):
    @abstractmethod
    def add(self, name: str, address: str, phone: str, logo_url: str, 
            verification_status: str, created_at: datetime) -> Clinic:
        pass

    @abstractmethod
    def get_by_id(self, clinic_id: int) -> Optional[Clinic]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> List[Clinic]:
        pass

    @abstractmethod
    def get_all(self) -> List[Clinic]:
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Clinic]:
        pass

    @abstractmethod
    def get_verified(self) -> List[Clinic]:
        pass

    @abstractmethod
    def get_pending(self) -> List[Clinic]:
        pass

    @abstractmethod
    def verify_clinic(self, clinic_id: int) -> Optional[Clinic]:
        pass

    @abstractmethod
    def reject_clinic(self, clinic_id: int) -> Optional[Clinic]:
        pass

    @abstractmethod
    def update(self, clinic_id: int, **kwargs) -> Optional[Clinic]:
        pass

    @abstractmethod
    def delete(self, clinic_id: int) -> bool:
        pass

    @abstractmethod
    def count_clinics(self, status: Optional[str]) -> int:
        pass

