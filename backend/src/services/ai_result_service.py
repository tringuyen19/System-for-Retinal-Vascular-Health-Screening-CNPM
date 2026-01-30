"""
AI Result Service - Business Logic Layer
Handles AI analysis results management
"""

from typing import List, Optional
from decimal import Decimal
from domain.models.ai_result import AiResult
from domain.models.iai_result_repository import IAiResultRepository
from domain.models.inotification_repository import INotificationRepository
from domain.models.iai_analysis_repository import IAiAnalysisRepository
from domain.models.iretinal_image_repository import IRetinalImageRepository
from domain.exceptions import NotFoundException, ValidationException


class AiResultService:
    def __init__(self, repository: IAiResultRepository,
                 notification_repository: Optional[INotificationRepository] = None,
                 analysis_repository: Optional[IAiAnalysisRepository] = None,
                 image_repository: Optional[IRetinalImageRepository] = None):
        self.repository = repository
        self.notification_repository = notification_repository
        self.analysis_repository = analysis_repository
        self.image_repository = image_repository
    
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

        # Auto-alert for high-risk results (FR-29)
        if risk_level.lower() in ['high', 'critical'] and self.notification_repository:
            self._send_high_risk_alert(result)
        
        return result

    def _send_high_risk_alert(self, result: AiResult):
        """
        Send high-risk alert notification automatically (FR-29)
        
        Args:
            result: AI Result with high/critical risk
        """
        try:
            from datetime import datetime
            from services.notification_service import NotificationService
            
            # Get analysis to find patient
            if not self.analysis_repository:
                return
            
            analysis = self.analysis_repository.get_by_id(result.analysis_id)
            if not analysis:
                return
            
            # Get image to find patient and clinic
            if not self.image_repository:
                return
            
            image = self.image_repository.get_by_id(analysis.image_id)
            if not image:
                return
            
            # Get clinic accounts (doctors and clinic managers) to notify
            from infrastructure.repositories.account_repository import AccountRepository
            from infrastructure.databases.mssql import session
            
            account_repo = AccountRepository(session)
            clinic_accounts = account_repo.get_by_clinic(image.clinic_id)
            
            # Filter to doctors and clinic managers (role_id 2 = Doctor, 4 = ClinicManager)
            target_accounts = [acc for acc in clinic_accounts if acc.role_id in [2, 4]]
            
            # Send alert to all relevant accounts
            notification_service = NotificationService(self.notification_repository)
            for account in target_accounts:
                notification_service.send_high_risk_alert(
                    account_id=account.account_id,
                    patient_id=image.patient_id,
                    risk_level=result.risk_level,
                    disease_type=result.disease_type,
                    confidence_score=float(result.confidence_score)
                )
        except Exception as e:
            # Don't fail the result creation if notification fails
            print(f"Warning: Failed to send high-risk alert: {str(e)}")
    
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
