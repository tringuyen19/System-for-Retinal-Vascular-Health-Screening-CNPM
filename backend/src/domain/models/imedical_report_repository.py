from abc import ABC, abstractmethod
from .medical_report import MedicalReport
from typing import List, Optional
from datetime import datetime, date

class IMedicalReportRepository(ABC):
    @abstractmethod
    def add(self, patient_id: int, analysis_id: int, doctor_id: int, 
            report_url: str, created_at: datetime) -> MedicalReport:
        pass

    @abstractmethod
    def get_by_id(self, report_id: int) -> Optional[MedicalReport]:
        pass

    @abstractmethod
    def get_by_analysis_id(self, analysis_id: int) -> Optional[MedicalReport]:
        pass

    @abstractmethod
    def get_by_patient(self, patient_id: int) -> List[MedicalReport]:
        pass

    @abstractmethod
    def get_recent_by_patient(self, patient_id: int, limit: int) -> List[MedicalReport]:
        pass

    @abstractmethod
    def get_by_doctor(self, doctor_id: int) -> List[MedicalReport]:
        pass

    @abstractmethod
    def get_all(self) -> List[MedicalReport]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> List[MedicalReport]:
        pass

    @abstractmethod
    def update_report_url(self, report_id: int, report_url: str) -> Optional[MedicalReport]:
        pass

    @abstractmethod
    def delete(self, report_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_patient(self, patient_id: int) -> int:
        pass

    @abstractmethod
    def count_by_doctor(self, doctor_id: int) -> int:
        pass

