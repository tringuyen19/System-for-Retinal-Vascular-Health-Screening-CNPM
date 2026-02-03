"""
Medical Report Service - Business Logic Layer
Handles medical report generation and management
"""

from typing import List, Optional
from datetime import datetime, date
from domain.models.medical_report import MedicalReport
from domain.models.imedical_report_repository import IMedicalReportRepository


class MedicalReportService:
    def __init__(self, repository: IMedicalReportRepository):
        self.repository = repository
    
    def generate_report(self, patient_id: int, analysis_id: int,
                       doctor_id: int, report_url: str = '',
                       medical_notes: str = '', diagnosis: str = '',
                       treatment_recommendations: str = '') -> Optional[MedicalReport]:
        """Generate medical report (FR-16: medical notes, diagnosis, treatment recommendations)"""
        return self.repository.add(
            patient_id=patient_id,
            analysis_id=analysis_id,
            doctor_id=doctor_id,
            report_url=report_url or '',
            created_at=datetime.now(),
            medical_notes=medical_notes or None,
            diagnosis=diagnosis or None,
            treatment_recommendations=treatment_recommendations or None
        )
    
    def get_report_by_id(self, report_id: int) -> Optional[MedicalReport]:
        """Get report by ID"""
        return self.repository.get_by_id(report_id)
    
    def get_report_by_analysis(self, analysis_id: int) -> Optional[MedicalReport]:
        """Get report by analysis ID"""
        return self.repository.get_by_analysis_id(analysis_id)
    
    def get_reports_by_patient(self, patient_id: int) -> List[MedicalReport]:
        """Get all reports for a patient"""
        return self.repository.get_by_patient(patient_id)
    
    def get_recent_reports_by_patient(self, patient_id: int, limit: int = 5) -> List[MedicalReport]:
        """Get recent reports for a patient"""
        return self.repository.get_recent_by_patient(patient_id, limit)
    
    def get_reports_by_doctor(self, doctor_id: int) -> List[MedicalReport]:
        """Get all reports by a doctor"""
        return self.repository.get_by_doctor(doctor_id)
    
    def list_all_reports(self) -> List[MedicalReport]:
        """Get all reports"""
        return self.repository.get_all()
    
    def get_reports_by_date_range(self, start_date: date, end_date: date) -> List[MedicalReport]:
        """Get reports within date range"""
        return self.repository.get_by_date_range(start_date, end_date)
    
    def update_report_url(self, report_id: int, report_url: str) -> Optional[MedicalReport]:
        """Update report URL"""
        return self.repository.update_report_url(report_id, report_url)

    def update_report(self, report_id: int, report_url: Optional[str] = None,
                      medical_notes: Optional[str] = None, diagnosis: Optional[str] = None,
                      treatment_recommendations: Optional[str] = None) -> Optional[MedicalReport]:
        """Update report (URL and/or FR-16: medical notes, diagnosis, treatment recommendations)"""
        return self.repository.update_report(
            report_id, report_url=report_url, medical_notes=medical_notes,
            diagnosis=diagnosis, treatment_recommendations=treatment_recommendations
        )
    
    def delete_report(self, report_id: int) -> bool:
        """Delete report"""
        return self.repository.delete(report_id)
    
    def count_by_patient(self, patient_id: int) -> int:
        """Count reports by patient"""
        return self.repository.count_by_patient(patient_id)
    
    def count_by_doctor(self, doctor_id: int) -> int:
        """Count reports by doctor"""
        return self.repository.count_by_doctor(doctor_id)
    
    def get_report_statistics(self) -> dict:
        """Get report statistics"""
        all_reports = self.repository.get_all()
        return {
            'total_reports': len(all_reports),
            'reports_today': len([r for r in all_reports if r.created_at.date() == date.today()])
        }
