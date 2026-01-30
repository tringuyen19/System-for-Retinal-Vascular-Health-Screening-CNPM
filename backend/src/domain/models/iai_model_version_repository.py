from abc import ABC, abstractmethod
from .ai_model_version import AiModelVersion
from typing import List, Optional
from datetime import datetime

class IAiModelVersionRepository(ABC):
    @abstractmethod
    def add(self, model_name: str, version: str, threshold_config: str, 
            trained_at: datetime, active_flag: bool) -> AiModelVersion:
        pass

    @abstractmethod
    def get_by_id(self, ai_model_version_id: int) -> Optional[AiModelVersion]:
        pass

    @abstractmethod
    def get_active_model(self) -> Optional[AiModelVersion]:
        pass

    @abstractmethod
    def get_by_version(self, version: str) -> Optional[AiModelVersion]:
        pass

    @abstractmethod
    def get_all(self) -> List[AiModelVersion]:
        pass

    @abstractmethod
    def set_active(self, ai_model_version_id: int) -> Optional[AiModelVersion]:
        pass

    @abstractmethod
    def update(self, ai_model_version_id: int, **kwargs) -> Optional[AiModelVersion]:
        pass

    @abstractmethod
    def delete(self, ai_model_version_id: int) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

