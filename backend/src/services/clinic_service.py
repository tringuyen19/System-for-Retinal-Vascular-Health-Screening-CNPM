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
from domain.models.iservice_package_repository import IServicePackageRepository
from domain.models.ipayment_repository import IPaymentRepository
from domain.exceptions import NotFoundException


class ClinicService:
    def __init__(self, repository: IClinicRepository,
                 account_repository: Optional[IAccountRepository] = None,
                 patient_repository: Optional[IPatientProfileRepository] = None,
                 doctor_repository: Optional[IDoctorProfileRepository] = None,
                 image_repository: Optional[IRetinalImageRepository] = None,
                 result_repository: Optional[IAiResultRepository] = None,
                 subscription_repository: Optional[ISubscriptionRepository] = None,
                 report_repository: Optional[IMedicalReportRepository] = None,
                 service_package_repository: Optional[IServicePackageRepository] = None,
                 payment_repository: Optional[IPaymentRepository] = None):
        self.repository = repository
        self.account_repository = account_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository
        self.image_repository = image_repository
        self.result_repository = result_repository
        self.subscription_repository = subscription_repository
        self.report_repository = report_repository
        self.service_package_repository = service_package_repository
        self.payment_repository = payment_repository
    
    def register_clinic(self, name: str, address: str, phone: str, 
                       manager_email: str, manager_password: str,
                       logo_url: Optional[str] = None, license_number: Optional[str] = None, 
                       tax_id: Optional[str] = None, verification_documents: Optional[List[str]] = None,
                       verification_status: str = 'pending') -> Optional[Clinic]:
        """
        Register new clinic with manager account (FR-22)
        
        This method:
        1. Creates the clinic record
        2. Creates a ClinicManager account linked to the clinic
        3. Returns the created clinic
        
        Args:
            name: Clinic name
            address: Clinic address
            phone: Clinic phone number
            manager_email: Email for clinic manager account
            manager_password: Password for clinic manager account
            logo_url: Clinic logo URL (optional)
            license_number: Optional business license number
            tax_id: Optional tax identification number
            verification_documents: Optional list of document URLs
            verification_status: Verification status (default: 'pending')
            
        Returns:
            Clinic: Created clinic domain model
            
        Raises:
            ValueError: If account creation fails
            ConflictException: If email already exists
        """
        from domain.exceptions import ConflictException
        
        # Step 1: Create clinic record
        clinic = self.repository.add(
            name=name,
            address=address,
            phone=phone,
            verification_status=verification_status,
            created_at=datetime.now(),
            logo_url=logo_url,
            license_number=license_number,
            tax_id=tax_id,
            verification_documents=verification_documents,
            manager_email=manager_email
        )
        
        if not clinic:
            raise ValueError("Failed to create clinic")
        
        # Step 2: Create clinic manager account (role_id = 4)
        if not self.account_repository:
            raise ValueError("Account repository not initialized")
        
        # Check if email already exists
        if self.account_repository.check_email_exists(manager_email):
            # Rollback clinic creation
            self.repository.delete(clinic.clinic_id)
            raise ConflictException(f"Email '{manager_email}' already exists")
        
        # Import account service to create account properly
        from services.account_service import AccountService
        account_service = AccountService(self.account_repository)
        
        try:
            # Create clinic manager account
            account = account_service.register_account(
                email=manager_email,
                password=manager_password,
                role_id=4,  # ClinicManager role
                clinic_id=clinic.clinic_id,
                status='active'  # Active by default, but clinic needs verification
            )
            
            if not account:
                # Rollback clinic creation
                self.repository.delete(clinic.clinic_id)
                raise ValueError("Failed to create clinic manager account")
            
            return clinic
            
        except Exception as e:
            # Rollback clinic creation on error
            try:
                self.repository.delete(clinic.clinic_id)
            except:
                pass
            raise e
    
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
    
    def approve_clinic(self, clinic_id: int, admin_notes: Optional[str] = None) -> Optional[Clinic]:
        """
        Approve clinic registration (FR-38)
        Can approve pending clinics or unsuspend suspended clinics
        
        Args:
            clinic_id: Clinic ID
            admin_notes: Optional notes from admin (for audit trail)
            
        Returns:
            Clinic: Updated clinic with verification_status = 'verified'
            
        Raises:
            ValueError: If clinic is not in 'pending' or 'suspended' status
        """
        clinic = self.get_clinic_by_id(clinic_id)
        if not clinic:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        
        # Validate workflow: Only pending or suspended clinics can be approved
        if clinic.verification_status not in ['pending', 'suspended']:
            raise ValueError(
                f"Cannot approve clinic. Current status: {clinic.verification_status}. "
                f"Only clinics with 'pending' or 'suspended' status can be approved."
            )
        
        # Admin notes are recommended but not enforced
        if not admin_notes:
            print(f"Info: Approving clinic {clinic_id} without admin notes")
        
        return self.repository.approve_clinic(clinic_id)
    
    def suspend_clinic(self, clinic_id: int, suspension_reason: Optional[str] = None) -> Optional[Clinic]:
        """
        Suspend clinic registration (FR-38)
        Can suspend verified clinics
        
        Args:
            clinic_id: Clinic ID
            suspension_reason: Reason for suspension (recommended for audit trail)
            
        Returns:
            Clinic: Updated clinic with verification_status = 'suspended'
        """
        clinic = self.get_clinic_by_id(clinic_id)
        if not clinic:
            raise NotFoundException(f"Clinic {clinic_id} not found")
        
        # Can only suspend verified clinics
        if clinic.verification_status != 'verified':
            raise ValueError(
                f"Cannot suspend clinic. Current status: {clinic.verification_status}. "
                f"Only verified clinics can be suspended."
            )
        
        if not suspension_reason:
            print(f"Warning: Suspending clinic {clinic_id} without suspension reason")
        
        return self.repository.suspend_clinic(clinic_id)
    
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
    
    def get_clinic_risk_aggregation(self, clinic_id: int,
                                   start_date: Optional[date] = None,
                                   end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get aggregated risk data for all patients in clinic (FR-25).
        Optional start_date/end_date filter analyses by analysis_time (for campaign reports).

        Returns:
            dict: risk_distribution (by result), risk_distribution_patients (by person, for %),
                  total_patients (in period if dates set), total_analyses, high_risk_patients_count, high_risk_patients.
        """
        if not self.patient_repository or not self.result_repository:
            raise ValueError("Repositories not initialized")

        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session

        analysis_repo = AiAnalysisRepository(session)
        patients = self.patient_repository.get_by_clinic_id(clinic_id)

        risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        total_results = 0
        high_risk_patients = []
        # Per-patient max risk in period (for anonymous campaign report: counts and %)
        patient_max_risk: Dict[int, str] = {}  # patient_id -> 'low'|'medium'|'high' (high includes critical)

        def risk_rank(r: str) -> int:
            return {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}.get(r.lower(), 0)

        for patient in patients:
            if not self.image_repository:
                continue
            images = self.image_repository.get_by_patient(patient.patient_id)
            patient_best = 'low'
            had_any_in_period = False

            for image in images:
                analysis = analysis_repo.get_by_image_id(image.image_id)
                if not analysis:
                    continue
                if start_date or end_date:
                    at = getattr(analysis, 'analysis_time', None)
                    if at:
                        ad = at.date() if hasattr(at, 'date') else at
                        if start_date and ad < start_date:
                            continue
                        if end_date and ad > end_date:
                            continue
                if self.result_repository:
                    results = self.result_repository.get_by_analysis_id(analysis.analysis_id)
                    for result in results:
                        risk_level = result.risk_level.lower()
                        had_any_in_period = True
                        if risk_level in risk_distribution:
                            risk_distribution[risk_level] += 1
                        total_results += 1
                        if risk_rank(risk_level) > risk_rank(patient_best):
                            patient_best = 'high' if risk_level in ('high', 'critical') else risk_level
                        if risk_level in ['high', 'critical']:
                            if patient.patient_id not in [p['patient_id'] for p in high_risk_patients]:
                                high_risk_patients.append({
                                    'patient_id': patient.patient_id,
                                    'patient_name': patient.patient_name,
                                    'risk_level': risk_level
                                })
            if had_any_in_period:
                patient_max_risk[patient.patient_id] = patient_best

        # Patient-based distribution for campaign report (high = high + critical)
        risk_distribution_patients = {'low': 0, 'medium': 0, 'high': 0}
        for pid, level in patient_max_risk.items():
            if level in ('high', 'critical'):
                risk_distribution_patients['high'] += 1
            elif level in risk_distribution_patients:
                risk_distribution_patients[level] += 1
        total_patients_screened = sum(risk_distribution_patients.values())

        return {
            'clinic_id': clinic_id,
            'total_patients': total_patients_screened,
            'total_analyses': total_results,
            'risk_distribution': risk_distribution,
            'risk_distribution_patients': risk_distribution_patients,
            'high_risk_patients_count': len(high_risk_patients),
            'high_risk_patients': high_risk_patients[:10]
        }
    
    # ========== FR-27: Usage Tracking ==========
    
    def get_clinic_usage_summary(self, clinic_id: int) -> Dict[str, Any]:
        """
        Get clinic usage summary including images analyzed and service package usage (FR-27).
        Credits = image_limit per package at subscription start; each analysis deducts 1.
        """
        if not self.image_repository or not self.subscription_repository:
            raise ValueError("Repositories not initialized")
        
        # Get all images for this clinic (clinic_id)
        images = self.image_repository.get_by_clinic(clinic_id) if hasattr(self.image_repository, 'get_by_clinic') else []
        
        # Phân tách: số ảnh do clinic (staff) tải vs do patient thuộc clinic tải
        # Clinic = tài khoản phòng khám (ClinicManager, Doctor). Patient = ảnh do tài khoản bệnh nhân thuộc phòng khám tải lên.
        clinic_account_ids = set()
        if self.account_repository:
            clinic_account_ids = {a.account_id for a in self.account_repository.get_by_clinic(clinic_id)}
        images_used_by_clinic = sum(1 for img in images if getattr(img, 'uploaded_by', None) in clinic_account_ids)
        # Số lượt tải ảnh mà bệnh nhân đã dùng = ảnh có uploaded_by là account_id của bệnh nhân thuộc phòng khám
        patient_account_ids = set()
        if self.patient_repository and hasattr(self.patient_repository, 'get_by_clinic_id'):
            patients = self.patient_repository.get_by_clinic_id(clinic_id)
            patient_account_ids = {getattr(p, 'account_id', None) for p in patients if getattr(p, 'account_id', None) is not None}
        images_used_by_patients = sum(1 for img in images if getattr(img, 'uploaded_by', None) in patient_account_ids)
        
        # Get analyses count (images that have been analyzed)
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        analysis_repo = AiAnalysisRepository(session)
        
        total_analyses = 0
        for image in images:
            analysis = analysis_repo.get_by_image_id(image.image_id)
            if analysis:
                total_analyses += 1
        
        # Đã sử dụng = số lượt upload ảnh của clinic + patient thuộc clinic (dùng chung cho mọi gói)
        credits_used = len(images)

        # Chỉ tính gói dịch vụ cấp phòng khám (package_id 6-8). Gói 1-5 là cho patient.
        # Số lượt đã cấp = mua gói mới + gia hạn (mỗi payment = 1 lần cấp thêm image_limit của gói)
        CLINIC_PACKAGE_IDS = (6, 7, 8)
        total_credits_allocated = 0
        remaining_credits = 0
        active_subscriptions = 0
        package_usage: List[Dict[str, Any]] = []
        
        if self.account_repository:
            accounts = self.account_repository.get_by_clinic(clinic_id)
            for account in accounts:
                if not self.subscription_repository:
                    continue
                subscriptions = self.subscription_repository.get_by_account(account.account_id)
                for sub in subscriptions:
                    if sub.status != 'active':
                        continue
                    if sub.package_id not in CLINIC_PACKAGE_IDS:
                        continue  # Bỏ qua gói patient (1-5), chỉ lấy gói clinic (6-8)
                    active_subscriptions += 1
                    remaining_credits += sub.remaining_credits
                    # image_limit của gói (dùng cho initial_for_sub và tính đã cấp)
                    initial_for_sub = sub.remaining_credits  # fallback
                    package_name = f"Gói #{sub.package_id}"
                    if self.service_package_repository:
                        pkg = self.service_package_repository.get_by_id(sub.package_id)
                        if pkg:
                            initial_for_sub = pkg.image_limit
                            package_name = pkg.name or package_name
                    # Đã cấp cho subscription này = số lần mua + gia hạn (mỗi payment = + image_limit)
                    num_payments = 0
                    if self.payment_repository:
                        payments = self.payment_repository.get_by_subscription(sub.subscription_id)
                        num_payments = len(payments)
                        total_credits_allocated += num_payments * initial_for_sub
                    else:
                        total_credits_allocated += initial_for_sub
                        num_payments = 1
                    credits_allocated_for_sub = num_payments * initial_for_sub
                    # Còn lại = Credits ban đầu - Đã sử dụng (đã sử dụng = tổng upload clinic + patient)
                    remaining_for_sub = max(0, credits_allocated_for_sub - credits_used)
                    start_str = sub.start_date.isoformat() if sub.start_date and hasattr(sub.start_date, 'isoformat') else None
                    end_str = sub.end_date.isoformat() if sub.end_date and hasattr(sub.end_date, 'isoformat') else None
                    package_usage.append({
                        'subscription_id': sub.subscription_id,
                        'account_id': account.account_id,
                        'package_id': sub.package_id,
                        'package_name': package_name,
                        'initial_credits': credits_allocated_for_sub,
                        'remaining_credits': remaining_for_sub,  # Credits ban đầu - Đã sử dụng
                        'credits_used': credits_used,  # số lượt upload ảnh của clinic + patient thuộc clinic
                        'start_date': start_str,
                        'end_date': end_str,
                    })
        
        remaining_credits = max(0, total_credits_allocated - credits_used) if total_credits_allocated > 0 else 0
        
        return {
            'clinic_id': clinic_id,
            'total_images_uploaded': len(images),
            'images_used_by_clinic': images_used_by_clinic,
            'images_used_by_patients': images_used_by_patients,
            'total_analyses': total_analyses,
            'active_subscriptions': active_subscriptions,
            'total_credits_allocated': total_credits_allocated,
            'remaining_credits': remaining_credits,
            'credits_used': credits_used,
            'usage_percentage': round((credits_used / total_credits_allocated * 100), 1) if total_credits_allocated > 0 else 0,
            'package_usage': package_usage,
        }
    
    # ========== FR-29: High-Risk Alerts ==========
    
    def get_high_risk_alerts(self, clinic_id: int, risk_level: str = 'high') -> List[Dict[str, Any]]:
        """
        Get high-risk patient alerts for clinic (FR-29).
        Khi risk_level='high' trả về cả bệnh nhân high và critical; khi 'critical' chỉ critical.
        """
        if not self.patient_repository:
            raise ValueError("Patient repository not initialized")
        
        # Lấy bệnh nhân theo mức rủi ro: 'high' => cả high và critical, 'critical' => chỉ critical
        levels_to_fetch = ['high', 'critical'] if risk_level == 'high' else [risk_level]
        seen_patient_ids = set()
        high_risk_patients = []
        for lvl in levels_to_fetch:
            patients = self.patient_repository.get_by_risk_level(risk_level=lvl, clinic_id=clinic_id)
            for p in patients:
                if p.patient_id not in seen_patient_ids:
                    seen_patient_ids.add(p.patient_id)
                    high_risk_patients.append(p)
        
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        
        analysis_repo = AiAnalysisRepository(session)
        
        alerts = []
        for patient in high_risk_patients:
            latest_analysis = None
            actual_risk_level = risk_level
            analysis_time = None
            if self.image_repository and self.result_repository:
                images = self.image_repository.get_by_patient(patient.patient_id)
                if images:
                    # Lấy tất cả analysis của bệnh nhân, chọn analysis mới nhất theo analysis_time
                    analyses_with_time = []
                    for img in images:
                        analysis = analysis_repo.get_by_image_id(img.image_id)
                        if analysis and getattr(analysis, 'analysis_time', None):
                            analyses_with_time.append(analysis)
                    if analyses_with_time:
                        latest_analysis_obj = max(analyses_with_time, key=lambda a: a.analysis_time)
                        analysis_time = getattr(latest_analysis_obj, 'analysis_time', None)
                        results = self.result_repository.get_by_analysis_id(latest_analysis_obj.analysis_id)
                        if results:
                            latest_result = max(results, key=lambda x: (
                                self._risk_level_to_number(x.risk_level),
                                float(x.confidence_score) if hasattr(x, 'confidence_score') else 0
                            ))
                            actual_risk_level = latest_result.risk_level or risk_level
                            conf = getattr(latest_result, 'confidence_score', None)
                            latest_analysis = {
                                'risk_level': latest_result.risk_level,
                                'confidence_score': float(conf) if conf is not None else None,
                                'disease_type': getattr(latest_result, 'disease_type', None),
                                'analysis_time': analysis_time.isoformat() if analysis_time and hasattr(analysis_time, 'isoformat') else (str(analysis_time) if analysis_time else None)
                            }
            
            alerts.append({
                'patient_id': patient.patient_id,
                'patient_name': patient.patient_name,
                'risk_level': actual_risk_level,
                'latest_analysis': latest_analysis,
                'alert_timestamp': datetime.now().isoformat()
            })
        
        # Sắp xếp: critical trước, sau đó high; cùng mức theo tên bệnh nhân
        def sort_key(a):
            r = (a.get('risk_level') or '').lower()
            return (0 if r == 'critical' else 1, (a.get('patient_name') or '').lower())
        alerts.sort(key=sort_key)
        return alerts
    
    # ========== FR-29: Abnormal Trend Detection ==========
    
    def detect_abnormal_trends(self, clinic_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Phát hiện xu hướng bất thường trong dữ liệu bệnh nhân của phòng khám (FR-29).
        - Tăng mức rủi ro: so sánh lần phân tích đầu và cuối trong khoảng thời gian.
        - Bước nhảy đột ngột: từ low/medium lên high/critical giữa hai lần phân tích liên tiếp.
        """
        if not self.patient_repository or not self.result_repository:
            raise ValueError("Repositories not initialized")
        
        from datetime import datetime, timedelta
        from infrastructure.repositories.ai_analysis_repository import AiAnalysisRepository
        from infrastructure.databases.mssql import session
        
        analysis_repo = AiAnalysisRepository(session)
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        patients = self.patient_repository.get_by_clinic_id(clinic_id)
        risk_increases = []
        sudden_spikes = []
        seen_risk_increase = set()  # patient_id -> keep one per patient (max increase)
        seen_spike_key = set()     # (patient_id, date) để tránh trùng
        
        for patient in patients:
            if not self.image_repository:
                continue
            images = self.image_repository.get_by_patient(patient.patient_id)
            recent_analyses = []
            for image in images:
                analysis = analysis_repo.get_by_image_id(image.image_id)
                if analysis and getattr(analysis, 'analysis_time', None):
                    at = analysis.analysis_time
                    adate = at.date() if hasattr(at, 'date') else at
                    if adate >= start_date:
                        recent_analyses.append(analysis)
            
            if len(recent_analyses) < 2:
                continue
            
            recent_analyses.sort(key=lambda x: x.analysis_time)
            risk_levels = []
            for analysis in recent_analyses:
                results = self.result_repository.get_by_analysis_id(analysis.analysis_id)
                if results:
                    highest_risk = max(results, key=lambda r: self._risk_level_to_number(r.risk_level))
                    risk_levels.append({
                        'date': analysis.analysis_time.date() if hasattr(analysis.analysis_time, 'date') else analysis.analysis_time,
                        'risk_level': highest_risk.risk_level,
                        'confidence': float(highest_risk.confidence_score) if getattr(highest_risk, 'confidence_score', None) is not None else None
                    })
            
            if len(risk_levels) < 2:
                continue
            
            first_risk = self._risk_level_to_number(risk_levels[0]['risk_level'])
            last_risk = self._risk_level_to_number(risk_levels[-1]['risk_level'])
            if last_risk > first_risk:
                inc = last_risk - first_risk
                # Mỗi bệnh nhân chỉ giữ một bản ghi tăng rủi ro (ưu tiên mức tăng lớn hơn)
                if patient.patient_id not in seen_risk_increase:
                    seen_risk_increase.add(patient.patient_id)
                    risk_increases.append({
                        'patient_id': patient.patient_id,
                        'patient_name': patient.patient_name,
                        'from_risk': risk_levels[0]['risk_level'],
                        'to_risk': risk_levels[-1]['risk_level'],
                        'increase': inc
                    })
            
            for i in range(1, len(risk_levels)):
                prev_risk = self._risk_level_to_number(risk_levels[i-1]['risk_level'])
                curr_risk = self._risk_level_to_number(risk_levels[i]['risk_level'])
                if prev_risk <= 2 and curr_risk >= 3:
                    d = risk_levels[i]['date']
                    dstr = d.isoformat() if hasattr(d, 'isoformat') else str(d)
                    key = (patient.patient_id, dstr)
                    if key not in seen_spike_key:
                        seen_spike_key.add(key)
                        sudden_spikes.append({
                            'patient_id': patient.patient_id,
                            'patient_name': patient.patient_name,
                            'date': dstr,
                            'from_risk': risk_levels[i-1]['risk_level'],
                            'to_risk': risk_levels[i]['risk_level'],
                            'confidence': risk_levels[i].get('confidence')
                        })
        
        # Luôn trả về cùng cấu trúc; giới hạn số lượng hiển thị
        risk_increases_sorted = sorted(risk_increases, key=lambda x: -x.get('increase', 0))[:20]
        sudden_spikes_sorted = sudden_spikes[:20]
        total = len(risk_increases_sorted) + len(sudden_spikes_sorted)
        abnormal_trends = {
            'risk_increases': risk_increases_sorted,
            'sudden_spikes': sudden_spikes_sorted,
            'total_abnormal_cases': total
        }
        
        return {
            'clinic_id': clinic_id,
            'period_days': days,
            'total_patients_analyzed': len(patients),
            'abnormal_trends_detected': total > 0,
            'abnormal_trends': abnormal_trends,
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
        Generate clinic-wide SUMMARY report for screening campaigns (FR-26).
        Report is AGGREGATED and ANONYMOUS by campaign (no individual patient list).
        """
        if not self.patient_repository or not self.result_repository:
            raise ValueError("Repositories not initialized")

        # Dữ liệu rủi ro tổng hợp (all-time, cùng nguồn với trang Báo cáo & Rủi ro tổng hợp)
        risk_aggregation = self.get_clinic_risk_aggregation(clinic_id)
        usage_data = self.get_clinic_usage_summary(clinic_id)
        reports_data = self.get_clinic_reports_summary(clinic_id, start_date, end_date)

        # Campaign overview: clinic as location & organizing unit
        clinic = self.get_clinic_by_id(clinic_id)
        clinic_name = clinic.name if clinic else f"Phòng khám #{clinic_id}"
        clinic_address = clinic.address if clinic else ""

        # Tổng số người được sàng lọc = số patient_id thuộc clinic (toàn bộ danh sách bệnh nhân của phòng khám)
        patients_in_clinic = self.patient_repository.get_by_clinic_id(clinic_id)
        total_patients_screened_count = len(patients_in_clinic)

        # Phân bố mức độ nguy cơ (tỷ lệ người): lấy từ Dữ liệu rủi ro tổng hợp (risk_aggregation, không lọc kỳ)
        dist_patients = risk_aggregation.get('risk_distribution_patients') or {'low': 0, 'medium': 0, 'high': 0}
        low_c, medium_c, high_c = dist_patients.get('low', 0), dist_patients.get('medium', 0), dist_patients.get('high', 0)
        total_with_risk = risk_aggregation.get('total_patients', 0)

        risk_percentages = {'low': 0.0, 'medium': 0.0, 'high': 0.0}
        if total_with_risk > 0:
            risk_percentages['low'] = round(100.0 * low_c / total_with_risk, 1)
            risk_percentages['medium'] = round(100.0 * medium_c / total_with_risk, 1)
            risk_percentages['high'] = round(100.0 * high_c / total_with_risk, 1)

        # Kết quả khuyến nghị: số người theo nhóm rủi ro (cùng nguồn rủi ro tổng hợp)
        recommendation_counts = {
            'recommend_specialist': high_c,
            'recommend_bp_diabetes_check': medium_c,
            'recommend_follow_up': low_c
        }

        report = {
            'campaign_name': campaign_name or f"Chiến dịch sàng lọc - {clinic_name}",
            'clinic_id': clinic_id,
            'campaign_overview': {
                'campaign_name': campaign_name or f"Chiến dịch sàng lọc - {clinic_name}",
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'location': clinic_address or clinic_name,
                'organizing_unit': clinic_name,
                'purpose': 'Quản lý & báo cáo hành chính.'
            },
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'generated_at': datetime.now().isoformat()
            },
            'summary': {
                'total_patients_screened': total_patients_screened_count,
                'total_images_analyzed': usage_data.get('total_images_uploaded', 0),
                'total_reports_generated': reports_data.get('total_reports', 0),
                'high_risk_cases': risk_aggregation.get('high_risk_patients_count', 0)
            },
            'risk_distribution': risk_aggregation.get('risk_distribution', {}),
            'risk_distribution_patients': dist_patients,
            'risk_percentages': risk_percentages,
            'recommendation_counts': recommendation_counts,
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
            'recommendations': self._generate_screening_recommendations(risk_aggregation, usage_data)
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