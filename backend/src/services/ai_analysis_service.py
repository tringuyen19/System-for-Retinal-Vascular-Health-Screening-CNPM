"""
AI Analysis Service - Business Logic Layer
Handles AI analysis workflow orchestration
"""

from typing import List, Optional
from datetime import datetime, date
from domain.models.ai_analysis import AiAnalysis
from domain.models.iai_analysis_repository import IAiAnalysisRepository
from domain.exceptions import NotFoundException, ValidationException


class AiAnalysisService:
    def __init__(self, repository: IAiAnalysisRepository):
        self.repository = repository
    
    def create_analysis(self, image_id: int, ai_model_version_id: int, 
                       status: str = 'pending', processing_time: Optional[int] = None) -> Optional[AiAnalysis]:
        """
        Create AI analysis
        
        Args:
            image_id: Retinal image ID
            ai_model_version_id: AI model version ID
            status: Analysis status (pending/processing/completed/failed)
            processing_time: Processing time in seconds (optional)
            
        Raises:
            ValidationException: If status is invalid
        """
        # Validate status
        valid_statuses = ['pending', 'processing', 'completed', 'failed']
        if status not in valid_statuses:
            raise ValidationException(f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}")
        
        return self.repository.add(
            image_id=image_id,
            ai_model_version_id=ai_model_version_id,
            analysis_time=datetime.now(),
            status=status,
            processing_time=processing_time
        )
    
    def get_analysis_by_id(self, analysis_id: int) -> AiAnalysis:
        """
        Get analysis by ID
        
        Raises:
            NotFoundException: If analysis not found
        """
        analysis = self.repository.get_by_id(analysis_id)
        if not analysis:
            raise NotFoundException(f"AI analysis {analysis_id} not found")
        return analysis
    
    def get_analysis_by_image(self, image_id: int) -> Optional[AiAnalysis]:
        """Get analysis by image ID (1:1 relationship)"""
        return self.repository.get_by_image_id(image_id)
    
    def get_patient_history(self, patient_id: int, limit: int = 50, offset: int = 0,
                           start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[AiAnalysis]:
        """
        Get analysis history for a patient with pagination and date filtering (FR-6)
        
        Args:
            patient_id: Patient ID
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List[AiAnalysis]: List of analyses sorted by date (newest first)
        """
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            raise ValidationException("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise ValidationException("Offset must be non-negative")
        
        # Validate date range
        if start_date and end_date and end_date < start_date:
            raise ValidationException("End date must be after start date")
        
        # Get analyses for patient (optimized query should use JOIN in repository)
        # This assumes repository has a method that joins with retinal_images table
        analyses = self.repository.get_by_patient_id(
            patient_id=patient_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        
        return analyses
    
    def get_analyses_by_status(self, status: str) -> List[AiAnalysis]:
        """Get analyses by status"""
        return self.repository.get_by_status(status)
    
    def get_pending_analyses(self) -> List[AiAnalysis]:
        """Get pending analyses"""
        return self.repository.get_pending()
    
    def get_processing_analyses(self) -> List[AiAnalysis]:
        """Get processing analyses"""
        return self.repository.get_processing()
    
    def get_completed_analyses(self) -> List[AiAnalysis]:
        """Get completed analyses"""
        return self.repository.get_completed()
    
    def mark_as_processing(self, analysis_id: int) -> Optional[AiAnalysis]:
        """Mark analysis as processing"""
        return self.repository.mark_as_processing(analysis_id)
    
    def mark_as_completed(self, analysis_id: int, processing_time: int) -> Optional[AiAnalysis]:
        """Mark analysis as completed with processing time"""
        return self.repository.mark_as_completed(analysis_id, processing_time)
    
    def mark_as_failed(self, analysis_id: int) -> Optional[AiAnalysis]:
        """Mark analysis as failed"""
        return self.repository.mark_as_failed(analysis_id)
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete analysis"""
        return self.repository.delete(analysis_id)
    
    def count_by_status(self, status: str) -> int:
        """Count analyses by status"""
        return self.repository.count_by_status(status)
    
    def get_average_processing_time(self) -> float:
        """Get average processing time"""
        return self.repository.get_average_processing_time()
    
    def get_analysis_statistics(self) -> dict:
        """Get analysis statistics"""
        return {
            'total_analyses': len(self.repository.get_all()),
            'pending': self.repository.count_by_status('pending'),
            'processing': self.repository.count_by_status('processing'),
            'completed': self.repository.count_by_status('completed'),
            'failed': self.repository.count_by_status('failed'),
            'avg_processing_time': self.repository.get_average_processing_time()
        }
    
    def get_patient_trend_data(self, patient_id: int, days: int = 90) -> dict:
        """
        Get trend data for a patient over time (FR-17)
        Optimized with JOIN queries instead of loops
        
        Args:
            patient_id: Patient ID
            days: Number of days to look back (default: 90)
            
        Returns:
            dict: Trend data including risk level changes, analysis frequency, etc.
        """
        from datetime import datetime, timedelta, date as date_type
        from infrastructure.repositories.ai_result_repository import AiResultRepository
        from infrastructure.databases.mssql import session
        
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Get analyses for patient (optimized - already uses JOIN in repository)
        analyses = self.get_patient_history(
            patient_id=patient_id,
            limit=1000,  # Get all for trend analysis
            offset=0,
            start_date=start_date,
            end_date=None
        )
        
        if not analyses:
            return {
                'patient_id': patient_id,
                'period_days': days,
                'total_analyses': 0,
                'risk_distribution': {},
                'average_confidence': 0.0,
                'analysis_dates': [],
                'risk_levels': [],
                'confidence_scores': [],
                'trend': 'no_data'
            }
        
        # Get all results for these analyses in one query (optimized)
        result_repo = AiResultRepository(session)
        analysis_ids = [a.analysis_id for a in analyses]
        
        # Get all results for all analyses (can be optimized further with bulk query)
        all_results = []
        for analysis_id in analysis_ids:
            results = result_repo.get_by_analysis_id(analysis_id)
            all_results.extend(results)
        
        # Process results (single pass)
        risk_levels = []
        confidence_scores = []
        dates = []
        risk_distribution = {}
        
        for analysis in analyses:
            # Get results for this analysis
            analysis_results = [r for r in all_results if r.analysis_id == analysis.analysis_id]
            
            for result in analysis_results:
                risk_level = result.risk_level
                risk_levels.append(risk_level)
                confidence_scores.append(float(result.confidence_score))
                dates.append(analysis.analysis_time.strftime('%Y-%m-%d'))
                
                # Count risk distribution
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine trend direction
        trend = 'stable'
        if len(risk_levels) > 1:
            # Simple trend: compare first and last risk levels
            first_risk = risk_levels[0]
            last_risk = risk_levels[-1]
            risk_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            if risk_order.get(last_risk, 0) < risk_order.get(first_risk, 0):
                trend = 'improving'
            elif risk_order.get(last_risk, 0) > risk_order.get(first_risk, 0):
                trend = 'worsening'
        
        return {
            'patient_id': patient_id,
            'period_days': days,
            'total_analyses': len(analyses),
            'risk_distribution': risk_distribution,
            'average_confidence': round(avg_confidence, 2),
            'analysis_dates': dates,
            'risk_levels': risk_levels,
            'confidence_scores': confidence_scores,
            'trend': trend
        }
