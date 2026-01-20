from abc import ABC, abstractmethod
from .patient_profile import PatientProfile
from typing import List, Optional
from datetime import date

class IPatientProfileRepository(ABC):
    @abstractmethod
    def add(self, account_id: int, patient_name: str, date_of_birth: Optional[date], 
            gender: Optional[str], medical_history: Optional[str]) -> PatientProfile:
        pass

    @abstractmethod
    def get_by_id(self, patient_id: int) -> Optional[PatientProfile]:
        pass

    @abstractmethod
    def get_by_account_id(self, account_id: int) -> Optional[PatientProfile]:
        pass

    @abstractmethod
    def get_by_name(self, patient_name: str) -> List[PatientProfile]:
        pass

    @abstractmethod
    def get_all(self) -> List[PatientProfile]:
        pass

    @abstractmethod
    def update(self, patient_id: int, **kwargs) -> Optional[PatientProfile]:
        pass

    @abstractmethod
    def update_medical_history(self, patient_id: int, medical_history: str) -> Optional[PatientProfile]:
        pass

    @abstractmethod
    def delete(self, patient_id: int) -> bool:
        pass

    @abstractmethod
    def count_patients(self) -> int:
        pass
    
    @abstractmethod
    def get_by_clinic_id(self, clinic_id: int) -> List[PatientProfile]:
        """Get patients assigned to a clinic (via account.clinic_id)"""
        pass
    
    @abstractmethod
    def search_by_name_and_clinic(self, patient_name: str, clinic_id: Optional[int] = None) -> List[PatientProfile]:
        """Search patients by name, optionally filtered by clinic"""
        pass
    
    @abstractmethod
    def get_by_risk_level(self, risk_level: str, clinic_id: Optional[int] = None, 
                         patient_name: Optional[str] = None) -> List[PatientProfile]:
        """
        Get patients by risk level with optional filters
        Uses JOIN with retinal_images -> ai_analysis -> ai_results
        """
        pass

