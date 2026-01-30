"""
Doctor Review Service - Business Logic Layer
Handles doctor review and validation of AI results
"""

from typing import List, Optional
from datetime import datetime
from domain.models.doctor_review import DoctorReview
from domain.models.idoctor_review_repository import IDoctorReviewRepository
from domain.exceptions import NotFoundException, ValidationException


class DoctorReviewService:
    def __init__(self, repository: IDoctorReviewRepository):
        self.repository = repository
    
    def create_review(self, analysis_id: int, doctor_id: int, 
                     validation_status: str, comment: Optional[str] = None) -> DoctorReview:
        """
        Create doctor review with validation (FR-15, FR-16)
        
        Args:
            analysis_id: Analysis ID
            doctor_id: Doctor ID
            validation_status: Validation status ('pending', 'approved', 'rejected', 'needs_revision')
            comment: Optional comment/notes
            
        Returns:
            DoctorReview: Created review domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected', 'needs_revision']
        if validation_status.lower() not in valid_statuses:
            raise ValidationException(f"Invalid validation status. Must be one of: {valid_statuses}")
        
        review = self.repository.add(
            analysis_id=analysis_id,
            doctor_id=doctor_id,
            validation_status=validation_status.lower(),
            comment=comment,
            reviewed_at=datetime.now()
        )
        
        if not review:
            raise ValueError("Failed to create doctor review")
        
        return review
    
    def get_review_by_id(self, review_id: int) -> DoctorReview:
        """
        Get review by ID
        
        Raises:
            NotFoundException: If review not found
        """
        review = self.repository.get_by_id(review_id)
        if not review:
            raise NotFoundException(f"Doctor review {review_id} not found")
        return review
    
    def get_review_by_analysis(self, analysis_id: int) -> Optional[DoctorReview]:
        """Get review by analysis ID"""
        return self.repository.get_by_analysis_id(analysis_id)
    
    def get_reviews_by_doctor(self, doctor_id: int) -> List[DoctorReview]:
        """Get all reviews by a doctor"""
        return self.repository.get_by_doctor(doctor_id)
    
    def get_reviews_by_status(self, validation_status: str) -> List[DoctorReview]:
        """Get reviews by validation status"""
        return self.repository.get_by_status(validation_status)
    
    def get_pending_reviews(self) -> List[DoctorReview]:
        """Get pending reviews"""
        return self.repository.get_pending_reviews()
    
    def approve_review(self, review_id: int, comment: Optional[str] = None) -> Optional[DoctorReview]:
        """Approve review"""
        return self.repository.approve(review_id, comment)
    
    def reject_review(self, review_id: int, comment: str) -> DoctorReview:
        """
        Reject review with comment
        
        Args:
            review_id: Review ID
            comment: Rejection comment (required)
            
        Returns:
            DoctorReview: Updated review domain model
            
        Raises:
            ValidationException: If comment is missing
            NotFoundException: If review not found
        """
        if not comment or not comment.strip():
            raise ValidationException("Comment is required when rejecting a review")
        
        review = self.repository.reject(review_id, comment)
        if not review:
            raise NotFoundException(f"Doctor review {review_id} not found")
        
        return review
    
    def update_review(self, review_id: int, **kwargs) -> Optional[DoctorReview]:
        """Update review"""
        return self.repository.update(review_id, **kwargs)
    
    def delete_review(self, review_id: int) -> bool:
        """Delete review"""
        return self.repository.delete(review_id)
    
    def count_by_doctor(self, doctor_id: int) -> int:
        """Count reviews by doctor"""
        return self.repository.count_by_doctor(doctor_id)
    
    def count_by_status(self, validation_status: str) -> int:
        """Count reviews by status"""
        return self.repository.count_by_status(validation_status)
    
    def get_review_statistics(self) -> dict:
        """
        Get review statistics (optimized - uses count queries instead of get_all)
        
        Returns:
            dict: Review statistics
        """
        # Optimized: Use count queries instead of loading all reviews
        total = sum([
            self.repository.count_by_status('pending'),
            self.repository.count_by_status('approved'),
            self.repository.count_by_status('rejected'),
            self.repository.count_by_status('needs_revision')
        ])
        
        return {
            'total_reviews': total,
            'pending': self.repository.count_by_status('pending'),
            'approved': self.repository.count_by_status('approved'),
            'rejected': self.repository.count_by_status('rejected'),
            'needs_revision': self.repository.count_by_status('needs_revision')
        }
    
    def get_feedback_aggregation(self, doctor_id: Optional[int] = None) -> dict:
        """
        Aggregate feedback from doctor reviews for AI improvement (FR-19)
        
        Args:
            doctor_id: Optional doctor ID to filter by
            
        Returns:
            dict: Aggregated feedback statistics
        """
        if doctor_id:
            reviews = self.get_reviews_by_doctor(doctor_id)
        else:
            reviews = self.repository.get_all()
        
        # Count validation statuses
        status_counts = {
            'approved': 0,
            'rejected': 0,
            'needs_revision': 0,
            'pending': 0
        }
        
        for review in reviews:
            if review.validation_status in status_counts:
                status_counts[review.validation_status] += 1
        
        # Calculate accuracy feedback (if we had accuracy_feedback field)
        # For now, use validation_status as proxy
        total_reviews = len(reviews)
        accuracy_score = (status_counts['approved'] / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            'total_feedback_items': total_reviews,
            'validation_status_distribution': status_counts,
            'estimated_ai_accuracy': round(accuracy_score, 2),
            'needs_improvement_count': status_counts['rejected'] + status_counts['needs_revision'],
            'improvement_rate': round((status_counts['rejected'] + status_counts['needs_revision']) / total_reviews * 100, 2) if total_reviews > 0 else 0,
            'feedback_summary': {
                'high_confidence': status_counts['approved'],
                'low_confidence': status_counts['needs_revision'],
                'incorrect': status_counts['rejected']
            }
        }