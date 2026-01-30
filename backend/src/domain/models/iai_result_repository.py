from abc import ABC, abstractmethod
from .ai_result import AiResult
from typing import List, Optional
from decimal import Decimal

class IAiResultRepository(ABC):
    @abstractmethod
    def add(self, analysis_id: int, disease_type: str, risk_level: str, 
            confidence_score: Decimal) -> AiResult:
        pass

    @abstractmethod
    def get_by_id(self, result_id: int) -> Optional[AiResult]:
        pass

    @abstractmethod
    def get_by_analysis_id(self, analysis_id: int) -> List[AiResult]:
        pass

    @abstractmethod
    def get_by_risk_level(self, risk_level: str) -> List[AiResult]:
        pass

    @abstractmethod
    def get_high_risk(self) -> List[AiResult]:
        pass

    @abstractmethod
    def get_by_disease_type(self, disease_type: str) -> List[AiResult]:
        pass

    @abstractmethod
    def get_all(self) -> List[AiResult]:
        pass

    @abstractmethod
    def update(self, result_id: int, **kwargs) -> Optional[AiResult]:
        pass

    @abstractmethod
    def delete(self, result_id: int) -> bool:
        pass

    @abstractmethod
    def count_by_risk_level(self, risk_level: str) -> int:
        pass

