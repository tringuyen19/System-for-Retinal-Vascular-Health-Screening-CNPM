"""
Doctor Profile Service - Business Logic Layer
Handles doctor profile management
"""

from typing import List, Optional
from domain.models.doctor_profile import DoctorProfile
from domain.models.idoctor_profile_repository import IDoctorProfileRepository
from domain.models.idoctor_review_repository import IDoctorReviewRepository
from domain.models.imedical_report_repository import IMedicalReportRepository
from domain.models.iconversation_repository import IConversationRepository
from domain.exceptions import NotFoundException


class DoctorProfileService:
    def __init__(self, repository: IDoctorProfileRepository,
                 review_repository: Optional[IDoctorReviewRepository] = None,
                 report_repository: Optional[IMedicalReportRepository] = None,
                 conversation_repository: Optional[IConversationRepository] = None):
        self.repository = repository
        self.review_repository = review_repository
        self.report_repository = report_repository
        self.conversation_repository = conversation_repository
    
    def create_doctor(self, account_id: int, doctor_name: str, 
                     specialization: str, license_number: str) -> Optional[DoctorProfile]:
        """Create doctor profile (with license validation)"""
        if self.repository.check_license_exists(license_number):
            raise ValueError(f"License number '{license_number}' already exists")
        
        return self.repository.add(
            account_id=account_id,
            doctor_name=doctor_name,
            specialization=specialization,
            license_number=license_number
        )
    
    def get_doctor_by_id(self, doctor_id: int) -> DoctorProfile:
        """
        Get doctor by ID
        
        Raises:
            NotFoundException: If doctor not found
        """
        doctor = self.repository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundException(f"Doctor {doctor_id} not found")
        return doctor
    
    def get_doctor_by_account(self, account_id: int) -> Optional[DoctorProfile]:
        """Get doctor by account ID"""
        return self.repository.get_by_account_id(account_id)
    
    def get_doctor_by_license(self, license_number: str) -> Optional[DoctorProfile]:
        """Get doctor by license number"""
        return self.repository.get_by_license_number(license_number)
    
    def search_by_specialization(self, specialization: str) -> List[DoctorProfile]:
        """Search doctors by specialization"""
        return self.repository.get_by_specialization(specialization)
    
    def search_doctors_by_name(self, doctor_name: str) -> List[DoctorProfile]:
        """Search doctors by name"""
        return self.repository.get_by_name(doctor_name)
    
    def list_all_doctors(self) -> List[DoctorProfile]:
        """Get all doctors"""
        return self.repository.get_all()
    
    def update_doctor(self, doctor_id: int, **kwargs) -> Optional[DoctorProfile]:
        """Update doctor profile"""
        return self.repository.update(doctor_id, **kwargs)
    
    def delete_doctor(self, doctor_id: int) -> bool:
        """Delete doctor"""
        return self.repository.delete(doctor_id)
    
    def count_doctors(self) -> int:
        """Count total doctors"""
        return self.repository.count_doctors()
    
    def count_by_specialization(self, specialization: str) -> int:
        """Count doctors by specialization"""
        return self.repository.count_by_specialization(specialization)
    
    def validate_license(self, license_number: str) -> bool:
        """Validate license number format and uniqueness"""
        if not license_number or len(license_number) < 5:
            return False
        return not self.repository.check_license_exists(license_number)
    
    def get_performance_summary(self, doctor_id: int) -> dict:
        """
        Get performance summary for a doctor (FR-21)
        Optimized with dependency injection
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            dict: Performance statistics including reviews, patients, reports, etc.
            
        Raises:
            NotFoundException: If doctor not found
            ValueError: If required repositories are not injected
        """
        doctor = self.get_doctor_by_id(doctor_id)
        
        # Check if repositories are injected
        if not self.review_repository or not self.report_repository or not self.conversation_repository:
            raise ValueError("Performance summary requires review, report, and conversation repositories to be injected")
        
        # Get reviews (optimized - single query)
        reviews = self.review_repository.get_by_doctor(doctor_id)
        
        # Get reports (optimized - single query)
        reports = self.report_repository.get_by_doctor(doctor_id)
        
        # Get conversations (optimized - single query)
        conversations = self.conversation_repository.get_by_doctor(doctor_id)
        
        # Calculate statistics (optimized - single pass)
        status_counts = {'approved': 0, 'rejected': 0, 'pending': 0, 'needs_revision': 0}
        for review in reviews:
            status = review.validation_status
            if status in status_counts:
                status_counts[status] += 1
        
        # Get unique patients (optimized - use set comprehension)
        unique_patients = set()
        unique_patients.update(conv.patient_id for conv in conversations)
        unique_patients.update(report.patient_id for report in reports)
        
        total_reviews = len(reviews)
        approved_count = status_counts['approved']
        
        return {
            'doctor_id': doctor_id,
            'doctor_name': doctor.doctor_name,
            'specialization': doctor.specialization,
            'total_reviews': total_reviews,
            'approved_reviews': approved_count,
            'rejected_reviews': status_counts['rejected'],
            'pending_reviews': status_counts['pending'],
            'needs_revision_reviews': status_counts['needs_revision'],
            'approval_rate': round(approved_count / total_reviews * 100, 2) if total_reviews > 0 else 0,
            'total_reports': len(reports),
            'total_conversations': len(conversations),
            'active_conversations': len([c for c in conversations if c.status == 'active']),
            'unique_patients': len(unique_patients),
            'performance_score': self._calculate_performance_score(
                approved_count, total_reviews, len(reports), len(conversations)
            )
        }
    
    def _calculate_performance_score(self, approved: int, total_reviews: int, 
                                    reports: int, conversations: int) -> float:
        """Calculate performance score (0-100)"""
        if total_reviews == 0:
            return 0.0
        
        review_score = (approved / total_reviews) * 0.5
        report_score = min(reports / 100, 1.0) * 0.3  # Normalize to max 100 reports
        conversation_score = min(conversations / 50, 1.0) * 0.2  # Normalize to max 50 conversations
        
        return round((review_score + report_score + conversation_score) * 100, 2)