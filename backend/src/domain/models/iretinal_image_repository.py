from abc import ABC, abstractmethod
from .retinal_image import RetinalImage
from typing import List, Optional
from datetime import datetime

class IRetinalImageRepository(ABC):
    @abstractmethod
    def add(self, patient_id: int, clinic_id: int, uploaded_by: int, 
            image_type: str, eye_side: str, image_url: str, 
            upload_time: datetime, status: str) -> RetinalImage:
        pass

    @abstractmethod
    def get_by_id(self, image_id: int) -> Optional[RetinalImage]:
        pass

    @abstractmethod
    def get_by_patient(self, patient_id: int) -> List[RetinalImage]:
        pass

    @abstractmethod
    def get_by_clinic(self, clinic_id: int) -> List[RetinalImage]:
        pass

    @abstractmethod
    def get_all(self) -> List[RetinalImage]:
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[RetinalImage]:
        pass

    @abstractmethod
    def get_pending_analysis(self) -> List[RetinalImage]:
        pass

    @abstractmethod
    def mark_as_processing(self, image_id: int) -> Optional[RetinalImage]:
        pass

    @abstractmethod
    def mark_as_analyzed(self, image_id: int) -> Optional[RetinalImage]:
        pass

    @abstractmethod
    def mark_as_error(self, image_id: int) -> Optional[RetinalImage]:
        pass

    @abstractmethod
    def update(self, image_id: int, **kwargs) -> Optional[RetinalImage]:
        pass

    @abstractmethod
    def delete(self, image_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_status(self, status: str) -> int:
        pass

