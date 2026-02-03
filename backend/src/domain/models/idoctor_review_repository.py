from abc import ABC, abstractmethod
from .doctor_review import DoctorReview
from typing import List, Optional
from datetime import datetime

class IDoctorReviewRepository(ABC):
    @abstractmethod
    def add(self, analysis_id: int, doctor_id: int, validation_status: str,
            comment: Optional[str], reviewed_at: datetime,
            ai_accuracy_feedback: Optional[str] = None) -> DoctorReview:
        pass

    @abstractmethod
    def get_by_id(self, review_id: int) -> Optional[DoctorReview]:
        pass

    @abstractmethod
    def get_by_analysis_id(self, analysis_id: int) -> Optional[DoctorReview]:
        pass

    @abstractmethod
    def get_by_doctor(self, doctor_id: int) -> List[DoctorReview]:
        pass

    @abstractmethod
    def get_by_status(self, validation_status: str) -> List[DoctorReview]:
        pass

    @abstractmethod
    def get_where_status_in(self, statuses: List[str]) -> List[DoctorReview]:
        """Reviews whose validation_status is in the given list (e.g. pending, rejected, needs_revision)."""
        pass

    @abstractmethod
    def get_pending_reviews(self) -> List[DoctorReview]:
        pass

    @abstractmethod
    def get_all(self) -> List[DoctorReview]:
        pass

    @abstractmethod
    def approve(self, review_id: int, comment: Optional[str], ai_accuracy_feedback: Optional[str] = None) -> Optional[DoctorReview]:
        pass

    @abstractmethod
    def reject(self, review_id: int, comment: str, ai_accuracy_feedback: Optional[str] = None) -> Optional[DoctorReview]:
        pass

    @abstractmethod
    def update(self, review_id: int, **kwargs) -> Optional[DoctorReview]:
        pass

    @abstractmethod
    def delete(self, review_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_doctor(self, doctor_id: int) -> int:
        pass

    @abstractmethod
    def count_by_status(self, validation_status: str) -> int:
        pass

    @abstractmethod
    def get_patients_by_doctor(self, doctor_id: int) -> List[dict]:
        """Get distinct patients of this doctor via DoctorReview -> AiAnalysis -> RetinalImage -> patient_id."""
        pass

