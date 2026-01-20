from abc import ABC, abstractmethod
from .doctor_profile import DoctorProfile
from typing import List, Optional

class IDoctorProfileRepository(ABC):
    @abstractmethod
    def add(self, account_id: int, doctor_name: str, specialization: str, 
            license_number: str) -> DoctorProfile:
        pass

    @abstractmethod
    def get_by_id(self, doctor_id: int) -> Optional[DoctorProfile]:
        pass

    @abstractmethod
    def get_by_account_id(self, account_id: int) -> Optional[DoctorProfile]:
        pass

    @abstractmethod
    def get_by_license_number(self, license_number: str) -> Optional[DoctorProfile]:
        pass

    @abstractmethod
    def get_by_specialization(self, specialization: str) -> List[DoctorProfile]:
        pass

    @abstractmethod
    def get_by_name(self, doctor_name: str) -> List[DoctorProfile]:
        pass

    @abstractmethod
    def get_all(self) -> List[DoctorProfile]:
        pass

    @abstractmethod
    def update(self, doctor_id: int, **kwargs) -> Optional[DoctorProfile]:
        pass

    @abstractmethod
    def delete(self, doctor_id: int) -> bool:
        pass

    @abstractmethod
    def count_doctors(self) -> int:
        pass

    @abstractmethod
    def count_by_specialization(self, specialization: str) -> int:
        pass

    @abstractmethod
    def check_license_exists(self, license_number: str) -> bool:
        pass

