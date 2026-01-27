"""
Clinic Service - Business Logic Layer
Handles clinic management and verification
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from domain.models.clinic import Clinic
from domain.models.iclinic_repository import IClinicRepository
from domain.models.iaccount_repository import IAccountRepository
from domain.models.ipatient_profile_repository import IPatientProfileRepository
from domain.models.idoctor_profile_repository import IDoctorProfileRepository
from domain.models.iretinal_image_repository import IRetinalImageRepository
from domain.models.iai_result_repository import IAiResultRepository
from domain.models.isubscription_repository import ISubscriptionRepository
from domain.models.imedical_report_repository import IMedicalReportRepository
from domain.exceptions import NotFoundException


class ClinicService:
    def __init__(self, repository: IClinicRepository,
                 account_repository: Optional[IAccountRepository] = None,
                 patient_repository: Optional[IPatientProfileRepository] = None,
                 doctor_repository: Optional[IDoctorProfileRepository] = None,
                 image_repository: Optional[IRetinalImageRepository] = None,
                 result_repository: Optional[IAiResultRepository] = None,
                 subscription_repository: Optional[ISubscriptionRepository] = None,
                 report_repository: Optional[IMedicalReportRepository] = None):
        self.repository = repository
        self.account_repository = account_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository
        self.image_repository = image_repository
        self.result_repository = result_repository
        self.subscription_repository = subscription_repository
        self.report_repository = report_repository

    def register_clinic(self, name: str, address: str, phone: str, 
                       logo_url: str, verification_status: str = 'pending') -> Optional[Clinic]:
        """Register new clinic"""
        return self.repository.add(
            name=name,
            address=address,
            phone=phone,
            logo_url=logo_url,
            verification_status=verification_status,
            created_at=datetime.now()
        )
    
    def get_clinic_by_id(self, clinic_id: int) -> Optional[Clinic]:
        """Get clinic by ID"""
        return self.repository.get_by_id(clinic_id)
    
    def search_clinics_by_name(self, name: str) -> List[Clinic]:
        """Search clinics by name"""
        return self.repository.get_by_name(name)
    
    def list_all_clinics(self, status: Optional[str] = None) -> List[Clinic]:
        """Get all clinics (optionally filter by status)"""
        if status:
            return self.repository.get_by_status(status)
        return self.repository.get_all()
    
    def get_verified_clinics(self) -> List[Clinic]:
        """Get all verified clinics"""
        return self.repository.get_verified()
    
    def get_pending_clinics(self) -> List[Clinic]:
        """Get clinics pending verification"""
        return self.repository.get_pending()
    
    def verify_clinic(self, clinic_id: int, admin_notes: Optional[str] = None) -> Optional[Clinic]:
        """
        Verify clinic (Admin only) - FR-22 Verification Workflow
        
        Workflow: pending → verified
        
        Args:
            clinic_id: Clinic ID
            admin_notes: Optional notes from admin (for audit trail)
            
        Returns:
            Clinic: Updated clinic with verification_status = 'verified'
            
        Raises:
            ValueError: If clinic is not in 'pending' status
        """
        clinic = self.get_clinic_by_id(clinic_id)
        if not clinic:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        
        # Validate workflow: Only pending clinics can be verified
        if clinic.verification_status != 'pending':
            raise ValueError(
                f"Cannot verify clinic. Current status: {clinic.verification_status}. "
                f"Only clinics with 'pending' status can be verified."
            )
        
        return self.repository.verify_clinic(clinic_id)
    
    def reject_clinic(self, clinic_id: int, rejection_reason: Optional[str] = None) -> Optional[Clinic]:
        """
        Reject clinic verification (Admin only) - FR-22 Verification Workflow
        
        Workflow: pending → rejected
        
        Args:
            clinic_id: Clinic ID
            rejection_reason: Reason for rejection (required for audit trail)
            
        Returns:
            Clinic: Updated clinic with verification_status = 'rejected'
            
        Raises:
            ValueError: If clinic is not in 'pending' status
        """
        clinic = self.get_clinic_by_id(clinic_id)
        if not clinic:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        
        # Validate workflow: Only pending clinics can be rejected
        if clinic.verification_status != 'pending':
            raise ValueError(
                f"Cannot reject clinic. Current status: {clinic.verification_status}. "
                f"Only clinics with 'pending' status can be rejected."
            )
        
        # Rejection reason is recommended but not enforced
        if not rejection_reason:
            # Log warning but proceed
            print(f"Warning: Rejecting clinic {clinic_id} without rejection reason")
        
        return self.repository.reject_clinic(clinic_id)
    
    def update_clinic(self, clinic_id: int, **kwargs) -> Optional[Clinic]:
        """Update clinic information"""
        return self.repository.update(clinic_id, **kwargs)
    
    def delete_clinic(self, clinic_id: int) -> bool:
        """Delete clinic"""
        return self.repository.delete(clinic_id)
    
    def count_clinics(self, status: Optional[str] = None) -> int:
        """Count clinics by status"""
        return self.repository.count_clinics(status)
    
    def get_clinic_statistics(self) -> dict:
        """Get clinic statistics"""
        return {
            'total_clinics': self.repository.count_clinics(None),
            'verified': self.repository.count_clinics('verified'),
            'pending': self.repository.count_clinics('pending'),
            'rejected': self.repository.count_clinics('rejected')
        }

    # ========== FR-22: Verification Workflow ==========
    
    def get_verification_status(self, clinic_id: int) -> str:
        """
        Get clinic verification status (FR-22)
        
        Returns:
            str: Verification status (pending, verified, rejected)
        """
        clinic = self.get_clinic_by_id(clinic_id)
        if not clinic:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        return clinic.verification_status
    
    # ========== FR-23: Manage Doctors and Patients ==========
    
    def get_clinic_members(self, clinic_id: int) -> Dict[str, Any]:
        """
        Get all members (doctors and patients) in a clinic (FR-23)
        
        Args:
            clinic_id: Clinic ID
            
        Returns:
            dict: Dictionary with doctors and patients lists
        """
        if not self.account_repository:
            raise ValueError("Account repository not initialized")
        
        # Get all accounts in clinic
        accounts = self.account_repository.get_by_clinic(clinic_id)
        
        doctors = []
        patients = []
        
        for account in accounts:
            if account.role_id == 2:  # Doctor role
                if self.doctor_repository:
                    doctor = self.doctor_repository.get_by_account_id(account.account_id)
                    if doctor:
                        doctors.append({
                            'account_id': account.account_id,
                            'doctor_id': doctor.doctor_id,
                            'doctor_name': doctor.doctor_name,
                            'specialization': doctor.specialization,
                            'license_number': doctor.license_number
                        })
            elif account.role_id == 3:  # Patient role
                if self.patient_repository:
                    patient = self.patient_repository.get_by_account_id(account.account_id)
                    if patient:
                        patients.append({
                            'account_id': account.account_id,
                            'patient_id': patient.patient_id,
                            'patient_name': patient.patient_name,
                            'date_of_birth': patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                            'gender': patient.gender
                        })
        
        return {
            'clinic_id': clinic_id,
            'doctors': doctors,
            'patients': patients,
            'total_doctors': len(doctors),
            'total_patients': len(patients)
        }
    
    # ========== FR-25: Aggregated Reports and Risk Data ==========
    
    def get_clinic_risk_aggregation(self, clinic_id: int) -> Dict[str, Any]:
        """
        Get aggregated risk data for all patients in clinic (FR-25)
        
        Args:
            clinic_id: Clinic ID
            
        Returns:
            dict: Aggregated risk statistics
        """
        if not self.patient_repository or not self.result_repository:
            raise ValueError("Repositories not initialized")
        
        # Get all patients in clinic
        patients = self.patient_repository.get_by_clinic_id(clinic_id)
        
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        total_results = 0
        high_risk_patients = []
        
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        
        analysis_repo = AiAnalysisRepository(session)
        
        for patient in patients:
            # Get patient's images
            if self.image_repository:
                images = self.image_repository.get_by_patient(patient.patient_id)
                
                for image in images:
                    # Get analysis for image first
                    analysis = analysis_repo.get_by_image_id(image.image_id)
                    if analysis:
                        # Get analysis results using analysis_id
                        if self.result_repository:
                            results = self.result_repository.get_by_analysis_id(analysis.analysis_id)
                            
                            for result in results:
                                risk_level = result.risk_level.lower()
                                if risk_level in risk_distribution:
                                    risk_distribution[risk_level] += 1
                                total_results += 1
                                
                                # Track high-risk patients
                                if risk_level in ['high', 'critical']:
                                    if patient.patient_id not in [p['patient_id'] for p in high_risk_patients]:
                                        high_risk_patients.append({
                                            'patient_id': patient.patient_id,
                                            'patient_name': patient.patient_name,
                                            'risk_level': risk_level
                                        })
        
        return {
            'clinic_id': clinic_id,
            'total_patients': len(patients),
            'total_analyses': total_results,
            'risk_distribution': risk_distribution,
            'high_risk_patients_count': len(high_risk_patients),
            'high_risk_patients': high_risk_patients[:10]  # Limit to 10 for response size
        }
    
    # ========== FR-27: Usage Tracking ==========
    
    def get_clinic_usage_summary(self, clinic_id: int) -> Dict[str, Any]:
        """
        Get clinic usage summary including images analyzed and package usage (FR-27)
        
        Args:
            clinic_id: Clinic ID
            
        Returns:
            dict: Usage statistics
        """
        if not self.image_repository or not self.subscription_repository:
            raise ValueError("Repositories not initialized")
        
        # Get all images uploaded by clinic
        images = self.image_repository.get_by_clinic(clinic_id) if hasattr(self.image_repository, 'get_by_clinic') else []
        
        # Get clinic subscriptions (via accounts)
        total_credits = 0
        remaining_credits = 0
        active_subscriptions = 0
        
        if self.account_repository:
            accounts = self.account_repository.get_by_clinic(clinic_id)
            for account in accounts:
                if self.subscription_repository:
                    subscriptions = self.subscription_repository.get_by_account(account.account_id)
                    for sub in subscriptions:
                        if sub.status == 'active':
                            active_subscriptions += 1
                            total_credits += sub.remaining_credits
                            remaining_credits += sub.remaining_credits
        
        return {
            'clinic_id': clinic_id,
            'total_images_uploaded': len(images),
            'total_analyses': len([img for img in images if img.status == 'analyzed']),
            'active_subscriptions': active_subscriptions,
            'total_credits_allocated': total_credits,
            'remaining_credits': remaining_credits,
            'credits_used': total_credits - remaining_credits
        }
    
    # ========== FR-29: High-Risk Alerts ==========
    
    def get_high_risk_alerts(self, clinic_id: int, risk_level: str = 'high') -> List[Dict[str, Any]]:
        """
        Get high-risk patient alerts for clinic (FR-29)
        
        Args:
            clinic_id: Clinic ID
            risk_level: Risk level to filter (default: 'high')
            
        Returns:
            List[dict]: List of high-risk patients with details
        """
        if not self.patient_repository:
            raise ValueError("Patient repository not initialized")
        
        # Get patients by risk level in clinic
        high_risk_patients = self.patient_repository.get_by_risk_level(
            risk_level=risk_level,
            clinic_id=clinic_id
        )
        
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        
        analysis_repo = AiAnalysisRepository(session)
        
        alerts = []
        for patient in high_risk_patients:
            # Get latest analysis for patient
            latest_analysis = None
            if self.image_repository and self.result_repository:
                images = self.image_repository.get_by_patient(patient.patient_id)
                if images:
                    # Get results for latest image
                    latest_image = max(images, key=lambda x: x.upload_time if hasattr(x, 'upload_time') else datetime.min)
                    # Get analysis for image first
                    analysis = analysis_repo.get_by_image_id(latest_image.image_id)
                    if analysis:
                        # Get results using analysis_id
                        results = self.result_repository.get_by_analysis_id(analysis.analysis_id)
                        if results:
                            latest_result = max(results, key=lambda x: float(x.confidence_score) if hasattr(x, 'confidence_score') else 0)
                            latest_analysis = {
                                'risk_level': latest_result.risk_level,
                                'confidence_score': float(latest_result.confidence_score) if hasattr(latest_result, 'confidence_score') else None,
                                'disease_type': latest_result.disease_type if hasattr(latest_result, 'disease_type') else None
                            }
            
            alerts.append({
                'patient_id': patient.patient_id,
                'patient_name': patient.patient_name,
                'risk_level': risk_level,
                'latest_analysis': latest_analysis,
                'alert_timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    # ========== FR-29: Abnormal Trend Detection ==========
    
    def detect_abnormal_trends(self, clinic_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Detect abnormal trends in clinic patient data (FR-29)
        
        Args:
            clinic_id: Clinic ID
            days: Number of days to analyze (default: 30)
            
        Returns:
            dict: Abnormal trend alerts
        """
        if not self.patient_repository or not self.result_repository:
            raise ValueError("Repositories not initialized")
        
        from datetime import datetime, timedelta
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        
        analysis_repo = AiAnalysisRepository(session)
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Get all patients in clinic
        patients = self.patient_repository.get_by_clinic_id(clinic_id)
        
        abnormal_trends = []
        risk_increases = []
        sudden_spikes = []
        
        for patient in patients:
            # Get patient trend data
            if self.image_repository:
                images = self.image_repository.get_by_patient(patient.patient_id)
                
                # Get analyses for recent period
                recent_analyses = []
                for image in images:
                    analysis = analysis_repo.get_by_image_id(image.image_id)
                    if analysis and analysis.analysis_time:
                        if analysis.analysis_time.date() >= start_date:
                            recent_analyses.append(analysis)
                
                if len(recent_analyses) < 2:
                    continue  # Need at least 2 analyses to detect trend
                
                # Sort by date
                recent_analyses.sort(key=lambda x: x.analysis_time)
                
                # Get results for each analysis
                risk_levels = []
                for analysis in recent_analyses:
                    if self.result_repository:
                        results = self.result_repository.get_by_analysis_id(analysis.analysis_id)
                        if results:
                            # Get highest risk result
                            highest_risk = max(results, key=lambda r: self._risk_level_to_number(r.risk_level))
                            risk_levels.append({
                                'date': analysis.analysis_time.date(),
                                'risk_level': highest_risk.risk_level,
                                'confidence': float(highest_risk.confidence_score)
                            })
                
                # Detect trends
                if len(risk_levels) >= 2:
                    first_risk = self._risk_level_to_number(risk_levels[0]['risk_level'])
                    last_risk = self._risk_level_to_number(risk_levels[-1]['risk_level'])
                    
                    # Risk increase trend
                    if last_risk > first_risk:
                        risk_increases.append({
                            'patient_id': patient.patient_id,
                            'patient_name': patient.patient_name,
                            'from_risk': risk_levels[0]['risk_level'],
                            'to_risk': risk_levels[-1]['risk_level'],
                            'increase': last_risk - first_risk
                        })
                    
                    # Sudden spike (jump from low/medium to high/critical)
                    for i in range(1, len(risk_levels)):
                        prev_risk = self._risk_level_to_number(risk_levels[i-1]['risk_level'])
                        curr_risk = self._risk_level_to_number(risk_levels[i]['risk_level'])
                        
                        if prev_risk <= 2 and curr_risk >= 3:  # Jump from low/medium to high/critical
                            sudden_spikes.append({
                                'patient_id': patient.patient_id,
                                'patient_name': patient.patient_name,
                                'date': risk_levels[i]['date'].isoformat(),
                                'from_risk': risk_levels[i-1]['risk_level'],
                                'to_risk': risk_levels[i]['risk_level'],
                                'confidence': risk_levels[i]['confidence']
                            })
        
        # Compile abnormal trends
        if risk_increases or sudden_spikes:
            abnormal_trends = {
                'risk_increases': risk_increases[:10],  # Limit to 10
                'sudden_spikes': sudden_spikes[:10],
                'total_abnormal_cases': len(risk_increases) + len(sudden_spikes)
            }
        
        return {
            'clinic_id': clinic_id,
            'period_days': days,
            'total_patients_analyzed': len(patients),
            'abnormal_trends_detected': len(abnormal_trends) > 0 if abnormal_trends else False,
            'abnormal_trends': abnormal_trends if abnormal_trends else {},
            'summary': {
                'risk_increases_count': len(risk_increases),
                'sudden_spikes_count': len(sudden_spikes)
            }
        }
    
    def _risk_level_to_number(self, risk_level: str) -> int:
        """Convert risk level to number for comparison"""
        risk_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        return risk_map.get(risk_level.lower(), 0)