from abc import ABC, abstractmethod
from .doctor_review import DoctorReview
from typing import List, Optional
from datetime import datetime

class IDoctorReviewRepository(ABC):
    @abstractmethod
    def add(self, analysis_id: int, doctor_id: int, validation_status: str, 
            comment: Optional[str], reviewed_at: datetime) -> DoctorReview:
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
    def get_pending_reviews(self) -> List[DoctorReview]:
        pass

    @abstractmethod
    def get_all(self) -> List[DoctorReview]:
        pass

    @abstractmethod
    def approve(self, review_id: int, comment: Optional[str]) -> Optional[DoctorReview]:
        pass

    @abstractmethod
    def reject(self, review_id: int, comment: str) -> Optional[DoctorReview]:
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

