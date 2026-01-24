"""
AI Result Service - Business Logic Layer
Handles AI analysis results management
"""

from typing import List, Optional
from decimal import Decimal
from domain.models.ai_result import AiResult
from domain.models.iai_result_repository import IAiResultRepository
from domain.exceptions import NotFoundException, ValidationException


class AiResultService:
    def __init__(self, repository: IAiResultRepository):
        self.repository = repository
    
    def create_result(self, analysis_id: int, disease_type: str, 
                     risk_level: str, confidence_score: Decimal) -> AiResult:
        """
        Create AI result with validation
        
        Args:
            analysis_id: Analysis ID
            disease_type: Type of disease detected
            risk_level: Risk level ('low', 'medium', 'high', 'critical')
            confidence_score: Confidence score (0-100)
            
        Returns:
            AiResult: Created result domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate risk level
        valid_levels = ['low', 'medium', 'high', 'critical']
        if risk_level.lower() not in valid_levels:
            raise ValidationException(f"Invalid risk level. Must be one of: {valid_levels}")
        
        # Validate confidence score
        if confidence_score < 0 or confidence_score > 100:
            raise ValidationException("Confidence score must be between 0 and 100")
        
        result = self.repository.add(
            analysis_id=analysis_id,
            disease_type=disease_type,
            risk_level=risk_level.lower(),
            confidence_score=confidence_score
        )
        
        if not result:
            raise ValueError("Failed to create AI result")
        
        return result
    
    def get_result_by_id(self, result_id: int) -> AiResult:
        """
        Get result by ID
        
        Raises:
            NotFoundException: If result not found
        """
        result = self.repository.get_by_id(result_id)
        if not result:
            raise NotFoundException(f"AI result {result_id} not found")
        return result
    
    def get_results_by_analysis(self, analysis_id: int) -> List[AiResult]:
        """
        Get all results for an analysis
        
        Returns:
            List[AiResult]: List of results (empty list if none found)
        """
        return self.repository.get_by_analysis_id(analysis_id)
    
    def get_results_by_risk_level(self, risk_level: str) -> List[AiResult]:
        """Get results by risk level"""
        return self.repository.get_by_risk_level(risk_level)
    
    def get_high_risk_results(self) -> List[AiResult]:
        """Get high risk results"""
        return self.repository.get_high_risk()
    
    def get_results_by_disease(self, disease_type: str) -> List[AiResult]:
        """Get results by disease type"""
        return self.repository.get_by_disease_type(disease_type)
    
    def list_all_results(self) -> List[AiResult]:
        """Get all results"""
        return self.repository.get_all()
    
    def update_result(self, result_id: int, **kwargs) -> Optional[AiResult]:
        """Update result"""
        return self.repository.update(result_id, **kwargs)
    
    def delete_result(self, result_id: int) -> bool:
        """Delete result"""
        return self.repository.delete(result_id)
    
    def count_by_risk_level(self, risk_level: str) -> int:
        """Count results by risk level"""
        return self.repository.count_by_risk_level(risk_level)
    
    def get_result_statistics(self) -> dict:
        """Get result statistics"""
        return {
            'total_results': len(self.repository.get_all()),
            'low_risk': self.repository.count_by_risk_level('low'),
            'medium_risk': self.repository.count_by_risk_level('medium'),
            'high_risk': self.repository.count_by_risk_level('high'),
            'critical_risk': self.repository.count_by_risk_level('critical')
        }
