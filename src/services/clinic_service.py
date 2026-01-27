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
        
        # Get analyses count (more accurate than checking image status)
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        analysis_repo = AiAnalysisRepository(session)
        
        total_analyses = 0
        for image in images:
            analysis = analysis_repo.get_by_image_id(image.image_id)
            if analysis:
                total_analyses += 1
        
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
                            # Use remaining_credits as total for now (simplified)
                            # In production, should track initial credits separately
                            remaining_credits += sub.remaining_credits
                            # Estimate total credits (assuming remaining is accurate)
                            total_credits += sub.remaining_credits  # Simplified
        
        credits_used = max(0, total_credits - remaining_credits) if total_credits > 0 else 0
        
        return {
            'clinic_id': clinic_id,
            'total_images_uploaded': len(images),
            'total_analyses': total_analyses,
            'active_subscriptions': active_subscriptions,
            'total_credits_allocated': total_credits,
            'remaining_credits': remaining_credits,
            'credits_used': credits_used,
            'usage_percentage': (credits_used / total_credits * 100) if total_credits > 0 else 0
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

      
    # ========== FR-25: Monitor Reports and Dashboard ==========
    
    def get_clinic_reports_summary(self, clinic_id: int, start_date: Optional[date] = None, 
                                   end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get summary of all reports for clinic patients (FR-25)
        
        Args:
            clinic_id: Clinic ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            dict: Reports summary with statistics
        """
        if not self.patient_repository or not self.report_repository:
            raise ValueError("Repositories not initialized")
        
        # Get all patients in clinic
        patients = self.patient_repository.get_by_clinic_id(clinic_id)
        
        all_reports = []
        for patient in patients:
            reports = self.report_repository.get_by_patient(patient.patient_id)
            # Filter by date range if provided
            if start_date and end_date:
                reports = [r for r in reports if r.created_at and 
                          start_date <= r.created_at.date() <= end_date]
            all_reports.extend(reports)
        
        # Calculate statistics
        total_reports = len(all_reports)
        reports_by_month = {}
        unique_patients = set()
        unique_doctors = set()
        
        for report in all_reports:
            if report.created_at:
                month_key = report.created_at.strftime('%Y-%m')
                reports_by_month[month_key] = reports_by_month.get(month_key, 0) + 1
            unique_patients.add(report.patient_id)
            unique_doctors.add(report.doctor_id)
        
        return {
            'clinic_id': clinic_id,
            'total_reports': total_reports,
            'unique_patients': len(unique_patients),
            'unique_doctors': len(unique_doctors),
            'reports_by_month': reports_by_month,
            'date_range': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }
        }
    
    # ========== FR-26: Clinic-wide Reports for Screening Campaigns ==========
    
    def generate_clinic_screening_report(self, clinic_id: int, campaign_name: Optional[str] = None,
                                        start_date: Optional[date] = None, 
                                        end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Generate clinic-wide report for screening campaigns (FR-26)
        
        Args:
            clinic_id: Clinic ID
            campaign_name: Optional campaign name
            start_date: Optional start date for campaign
            end_date: Optional end date for campaign
            
        Returns:
            dict: Screening campaign report
        """
        if not self.patient_repository or not self.result_repository:
            raise ValueError("Repositories not initialized")
        
        # Get risk aggregation
        risk_data = self.get_clinic_risk_aggregation(clinic_id)
        
        # Get usage summary
        usage_data = self.get_clinic_usage_summary(clinic_id)
        
        # Get reports summary
        reports_data = self.get_clinic_reports_summary(clinic_id, start_date, end_date)
        
        # Get high-risk alerts
        high_risk_alerts = self.get_high_risk_alerts(clinic_id, risk_level='high')
        
        # Compile screening report
        report = {
            'campaign_name': campaign_name or f"Screening Campaign - Clinic {clinic_id}",
            'clinic_id': clinic_id,
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'generated_at': datetime.now().isoformat()
            },
            'summary': {
                'total_patients_screened': risk_data.get('total_patients', 0),
                'total_images_analyzed': usage_data.get('total_analyses', 0),
                'total_reports_generated': reports_data.get('total_reports', 0),
                'high_risk_cases': len(high_risk_alerts)
            },
            'risk_distribution': risk_data.get('risk_distribution', {}),
            'usage_statistics': {
                'images_uploaded': usage_data.get('total_images_uploaded', 0),
                'credits_used': usage_data.get('credits_used', 0),
                'remaining_credits': usage_data.get('remaining_credits', 0)
            },
            'reports_statistics': {
                'total_reports': reports_data.get('total_reports', 0),
                'unique_patients': reports_data.get('unique_patients', 0),
                'unique_doctors': reports_data.get('unique_doctors', 0)
            },
            'high_risk_patients': high_risk_alerts[:20],  # Top 20
            'recommendations': self._generate_screening_recommendations(risk_data, usage_data)
        }
        
        return report
    
    def _generate_screening_recommendations(self, risk_data: Dict, usage_data: Dict) -> List[str]:
        """Generate recommendations based on screening data"""
        recommendations = []
        
        high_risk_count = risk_data.get('high_risk_patients_count', 0)
        total_patients = risk_data.get('total_patients', 0)
        
        if total_patients > 0:
            high_risk_percentage = (high_risk_count / total_patients) * 100
            
            if high_risk_percentage > 20:
                recommendations.append(
                    f"⚠️ High-risk rate is {high_risk_percentage:.1f}%. "
                    "Consider increasing screening frequency and follow-up care."
                )
            elif high_risk_percentage > 10:
                recommendations.append(
                    f"⚠️ Moderate high-risk rate ({high_risk_percentage:.1f}%). "
                    "Monitor these patients closely."
                )
        
        remaining_credits = usage_data.get('remaining_credits', 0)
        if remaining_credits < 100:
            recommendations.append(
                f"⚠️ Low credits remaining ({remaining_credits}). "
                "Consider renewing subscription to continue screening services."
            )
        
        if not recommendations:
            recommendations.append("✅ Screening campaign is running smoothly. Continue regular monitoring.")
        
        return recommendations
    
    # ========== FR-30: Export Statistics for Research ==========
    
    def export_clinic_statistics(self, clinic_id: int, format: str = 'json') -> Dict[str, Any]:
        """
        Export clinic statistics for clinical research or management (FR-30)
        
        Args:
            clinic_id: Clinic ID
            format: Export format ('json', 'csv_data')
            
        Returns:
            dict: Exported statistics data
        """
        # Gather all statistics
        risk_data = self.get_clinic_risk_aggregation(clinic_id)
        usage_data = self.get_clinic_usage_summary(clinic_id)
        reports_data = self.get_clinic_reports_summary(clinic_id)
        members_data = self.get_clinic_members(clinic_id)
        trends_data = self.detect_abnormal_trends(clinic_id, days=90)
        
        # Compile comprehensive statistics
        statistics = {
            'clinic_id': clinic_id,
            'export_date': datetime.now().isoformat(),
            'export_format': format,
            'clinic_info': {
                'total_doctors': members_data.get('total_doctors', 0),
                'total_patients': members_data.get('total_patients', 0)
            },
            'risk_statistics': {
                'total_analyses': risk_data.get('total_analyses', 0),
                'risk_distribution': risk_data.get('risk_distribution', {}),
                'high_risk_patients_count': risk_data.get('high_risk_patients_count', 0)
            },
            'usage_statistics': {
                'total_images_uploaded': usage_data.get('total_images_uploaded', 0),
                'total_analyses': usage_data.get('total_analyses', 0),
                'active_subscriptions': usage_data.get('active_subscriptions', 0),
                'credits_used': usage_data.get('credits_used', 0),
                'remaining_credits': usage_data.get('remaining_credits', 0)
            },
            'reports_statistics': {
                'total_reports': reports_data.get('total_reports', 0),
                'unique_patients': reports_data.get('unique_patients', 0),
                'unique_doctors': reports_data.get('unique_doctors', 0),
                'reports_by_month': reports_data.get('reports_by_month', {})
            },
            'trend_analysis': {
                'abnormal_trends_detected': trends_data.get('abnormal_trends_detected', False),
                'risk_increases_count': trends_data.get('summary', {}).get('risk_increases_count', 0),
                'sudden_spikes_count': trends_data.get('summary', {}).get('sudden_spikes_count', 0)
            }
        }
        
        # Convert to CSV format if requested
        if format == 'csv_data':
            statistics['csv_format'] = self._convert_to_csv_format(statistics)
        
        return statistics
    
    def _convert_to_csv_format(self, statistics: Dict[str, Any]) -> List[List[str]]:
        """Convert statistics to CSV format (list of rows)"""
        csv_rows = []
        
        # Header
        csv_rows.append(['Metric', 'Value'])
        
        # Clinic info
        csv_rows.append(['Clinic ID', str(statistics['clinic_id'])])
        csv_rows.append(['Total Doctors', str(statistics['clinic_info']['total_doctors'])])
        csv_rows.append(['Total Patients', str(statistics['clinic_info']['total_patients'])])
        csv_rows.append(['', ''])  # Empty row
        
        # Risk statistics
        csv_rows.append(['Risk Statistics', ''])
        csv_rows.append(['Total Analyses', str(statistics['risk_statistics']['total_analyses'])])
        risk_dist = statistics['risk_statistics']['risk_distribution']
        csv_rows.append(['Low Risk', str(risk_dist.get('low', 0))])
        csv_rows.append(['Medium Risk', str(risk_dist.get('medium', 0))])
        csv_rows.append(['High Risk', str(risk_dist.get('high', 0))])
        csv_rows.append(['Critical Risk', str(risk_dist.get('critical', 0))])
        csv_rows.append(['High Risk Patients', str(statistics['risk_statistics']['high_risk_patients_count'])])
        csv_rows.append(['', ''])  # Empty row
        
        # Usage statistics
        csv_rows.append(['Usage Statistics', ''])
        usage = statistics['usage_statistics']
        csv_rows.append(['Total Images Uploaded', str(usage['total_images_uploaded'])])
        csv_rows.append(['Total Analyses', str(usage['total_analyses'])])
        csv_rows.append(['Active Subscriptions', str(usage['active_subscriptions'])])
        csv_rows.append(['Credits Used', str(usage['credits_used'])])
        csv_rows.append(['Remaining Credits', str(usage['remaining_credits'])])
        csv_rows.append(['', ''])  # Empty row
        
        # Reports statistics
        csv_rows.append(['Reports Statistics', ''])
        reports = statistics['reports_statistics']
        csv_rows.append(['Total Reports', str(reports['total_reports'])])
        csv_rows.append(['Unique Patients', str(reports['unique_patients'])])
        csv_rows.append(['Unique Doctors', str(reports['unique_doctors'])])
        
        return csv_rows