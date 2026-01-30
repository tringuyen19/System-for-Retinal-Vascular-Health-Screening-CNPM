from abc import ABC, abstractmethod
from .ai_analysis import AiAnalysis
from typing import List, Optional
from datetime import datetime, date

class IAiAnalysisRepository(ABC):
    @abstractmethod
    def add(self, image_id: int, ai_model_version_id: int, 
            analysis_time: datetime, status: str, processing_time: Optional[int] = None) -> AiAnalysis:
        pass

    @abstractmethod
    def get_by_id(self, analysis_id: int) -> Optional[AiAnalysis]:
        pass

    @abstractmethod
    def get_by_image_id(self, image_id: int) -> Optional[AiAnalysis]:
        pass

    @abstractmethod
    def get_all(self) -> List[AiAnalysis]:
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[AiAnalysis]:
        pass

    @abstractmethod
    def get_pending(self) -> List[AiAnalysis]:
        pass

    @abstractmethod
    def get_processing(self) -> List[AiAnalysis]:
        pass

    @abstractmethod
    def get_completed(self) -> List[AiAnalysis]:
        pass

    @abstractmethod
    def mark_as_processing(self, analysis_id: int) -> Optional[AiAnalysis]:
        pass

    @abstractmethod
    def mark_as_completed(self, analysis_id: int, processing_time: int) -> Optional[AiAnalysis]:
        pass

    @abstractmethod
    def mark_as_failed(self, analysis_id: int) -> Optional[AiAnalysis]:
        pass

    @abstractmethod
    def delete(self, analysis_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_status(self, status: str) -> int:
        pass

    @abstractmethod
    def get_average_processing_time(self) -> float:
        pass
    
    @abstractmethod
    def get_by_patient_id(self, patient_id: int, limit: int = 50, offset: int = 0,
                         start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[AiAnalysis]:
        """
        Get analyses for a patient with pagination and date filtering
        Uses JOIN with retinal_images table
        """
        pass

