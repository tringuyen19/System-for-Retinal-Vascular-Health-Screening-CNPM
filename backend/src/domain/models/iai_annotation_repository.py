from abc import ABC, abstractmethod
from .ai_annotation import AiAnnotation
from typing import List, Optional

class IAiAnnotationRepository(ABC):
    @abstractmethod
    def add(self, analysis_id: int, heatmap_url: str, description: Optional[str]) -> AiAnnotation:
        pass

    @abstractmethod
    def get_by_id(self, annotation_id: int) -> Optional[AiAnnotation]:
        pass

    @abstractmethod
    def get_by_analysis_id(self, analysis_id: int) -> Optional[AiAnnotation]:
        pass

    @abstractmethod
    def get_all(self) -> List[AiAnnotation]:
        pass

    @abstractmethod
    def get_all_with_descriptions(self) -> List[AiAnnotation]:
        pass

    @abstractmethod
    def update_heatmap(self, annotation_id: int, heatmap_url: str) -> Optional[AiAnnotation]:
        pass

    @abstractmethod
    def update(self, annotation_id: int, **kwargs) -> Optional[AiAnnotation]:
        pass

    @abstractmethod
    def delete(self, annotation_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

