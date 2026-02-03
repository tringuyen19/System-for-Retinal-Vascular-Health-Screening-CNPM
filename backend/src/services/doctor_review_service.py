"""
Doctor Review Service - Business Logic Layer
Handles doctor review and validation of AI results (FR-15, FR-16)
"""

from typing import List, Optional
from datetime import datetime
from domain.models.doctor_review import DoctorReview
from domain.models.ai_analysis import AiAnalysis
from domain.models.idoctor_review_repository import IDoctorReviewRepository
from domain.models.iai_analysis_repository import IAiAnalysisRepository
from domain.exceptions import NotFoundException, ValidationException


class DoctorReviewService:
    def __init__(self, repository: IDoctorReviewRepository, analysis_repository: Optional[IAiAnalysisRepository] = None):
        self.repository = repository
        # Optional dependency: used for listing analyses that still need a doctor review (FR-15)
        self.analysis_repository = analysis_repository
    
    def create_review(self, analysis_id: int, doctor_id: int,
                     validation_status: str, comment: Optional[str] = None,
                     ai_accuracy_feedback: Optional[str] = None) -> DoctorReview:
        """
        Create or update doctor review for an analysis (FR-15, FR-16, FR-19).
        Table doctor_reviews has UNIQUE(analysis_id): one review per analysis.
        ai_accuracy_feedback: FR-19 - correct / incorrect / partially_correct for AI improvement.
        """
        valid_statuses = ['pending', 'approved', 'rejected', 'needs_revision']
        if validation_status.lower() not in valid_statuses:
            raise ValidationException(f"Invalid validation status. Must be one of: {valid_statuses}")
        valid_feedback = ['correct', 'incorrect', 'partially_correct']
        if ai_accuracy_feedback and ai_accuracy_feedback.lower() not in valid_feedback:
            ai_accuracy_feedback = None

        existing = self.repository.get_by_analysis_id(analysis_id)
        now = datetime.now()
        if existing:
            review = self.repository.update(
                existing.review_id,
                doctor_id=doctor_id,
                validation_status=validation_status.lower(),
                comment=comment,
                reviewed_at=now,
                ai_accuracy_feedback=(ai_accuracy_feedback.strip() if ai_accuracy_feedback else None)
            )
        else:
            review = self.repository.add(
                analysis_id=analysis_id,
                doctor_id=doctor_id,
                validation_status=validation_status.lower(),
                comment=comment,
                reviewed_at=now,
                ai_accuracy_feedback=(ai_accuracy_feedback.strip() if ai_accuracy_feedback else None)
            )

        if not review:
            raise ValueError("Failed to create or update doctor review")
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
    
    def get_pending_reviews(self) -> List[AiAnalysis]:
        """
        Get analyses that are completed but have NOT been reviewed by any doctor yet.
        This powers the "Cần duyệt" list for FR-15.
        """
        if not self.analysis_repository:
            return []
        return self.analysis_repository.get_completed_without_review()

    def get_reviews_needing_approval(self) -> List[DoctorReview]:
        """
        Get reviews whose validation_status is not 'approved' (pending, rejected, needs_revision).
        These must be displayed so the doctor can review and approve (FR-15).
        """
        return self.repository.get_where_status_in(['pending', 'rejected', 'needs_revision'])

    def get_doctors_who_reviewed_patient(self, patient_id: int) -> List[dict]:
        """Get list of doctors who reviewed this patient's analyses (FR-10: patient can chat with them)."""
        return self.repository.get_doctors_by_patient(patient_id)
    
    def approve_review(self, review_id: int, comment: Optional[str] = None,
                       ai_accuracy_feedback: Optional[str] = None) -> Optional[DoctorReview]:
        """Approve review (FR-19: optional ai_accuracy_feedback)."""
        valid = ['correct', 'incorrect', 'partially_correct']
        if ai_accuracy_feedback and ai_accuracy_feedback.lower() not in valid:
            ai_accuracy_feedback = None
        return self.repository.approve(review_id, comment, ai_accuracy_feedback=ai_accuracy_feedback)

    def reject_review(self, review_id: int, comment: str,
                      ai_accuracy_feedback: Optional[str] = None) -> DoctorReview:
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
        valid = ['correct', 'incorrect', 'partially_correct']
        if ai_accuracy_feedback and ai_accuracy_feedback.lower() not in valid:
            ai_accuracy_feedback = None
        review = self.repository.reject(review_id, comment, ai_accuracy_feedback=ai_accuracy_feedback)
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
        # FR-19: explicit AI accuracy feedback distribution
        ai_feedback_counts = {'correct': 0, 'incorrect': 0, 'partially_correct': 0, 'no_feedback': 0}

        for review in reviews:
            if review.validation_status in status_counts:
                status_counts[review.validation_status] += 1
            fb = getattr(review, 'ai_accuracy_feedback', None)
            if fb and (fb.lower() in ai_feedback_counts):
                ai_feedback_counts[fb.lower()] += 1
            else:
                ai_feedback_counts['no_feedback'] += 1

        total_reviews = len(reviews)
        # Prefer FR-19 ai_accuracy_feedback for estimated accuracy when available
        with_feedback = ai_feedback_counts['correct'] + ai_feedback_counts['incorrect'] + ai_feedback_counts['partially_correct']
        if with_feedback > 0:
            accuracy_score = (ai_feedback_counts['correct'] / with_feedback * 100) + (
                ai_feedback_counts['partially_correct'] / with_feedback * 50
            )
        else:
            accuracy_score = (status_counts['approved'] / total_reviews * 100) if total_reviews > 0 else 0

        return {
            'total_feedback_items': total_reviews,
            'validation_status_distribution': status_counts,
            'ai_accuracy_feedback_distribution': ai_feedback_counts,
            'estimated_ai_accuracy': round(accuracy_score, 2),
            'needs_improvement_count': status_counts['rejected'] + status_counts['needs_revision'],
            'improvement_rate': round((status_counts['rejected'] + status_counts['needs_revision']) / total_reviews * 100, 2) if total_reviews > 0 else 0,
            'feedback_summary': {
                'high_confidence': status_counts['approved'],
                'low_confidence': status_counts['needs_revision'],
                'incorrect': status_counts['rejected'],
                'ai_correct': ai_feedback_counts['correct'],
                'ai_incorrect': ai_feedback_counts['incorrect'],
                'ai_partially_correct': ai_feedback_counts['partially_correct'],
            }
        }