"""
Admin Service - Business Logic Layer
Handles admin operations: dashboard, analytics, AI configuration, and system management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from domain.models.iaccount_repository import IAccountRepository
from domain.models.iclinic_repository import IClinicRepository
from domain.models.ipatient_profile_repository import IPatientProfileRepository
from domain.models.idoctor_profile_repository import IDoctorProfileRepository
from domain.models.iretinal_image_repository import IRetinalImageRepository
from domain.models.iai_analysis_repository import IAiAnalysisRepository
from domain.models.iai_result_repository import IAiResultRepository
from domain.models.ipayment_repository import IPaymentRepository
from domain.models.isubscription_repository import ISubscriptionRepository
from domain.models.iai_model_version_repository import IAiModelVersionRepository
from domain.exceptions import NotFoundException


class AdminService:
    """Service for admin operations - Phase 4 requirements"""
    
    def __init__(self,
                 account_repository: IAccountRepository,
                 clinic_repository: IClinicRepository,
                 patient_repository: IPatientProfileRepository,
                 doctor_repository: IDoctorProfileRepository,
                 image_repository: IRetinalImageRepository,
                 analysis_repository: IAiAnalysisRepository,
                 result_repository: IAiResultRepository,
                 payment_repository: IPaymentRepository,
                 subscription_repository: ISubscriptionRepository,
                 model_version_repository: IAiModelVersionRepository):
        self.account_repository = account_repository
        self.clinic_repository = clinic_repository
        self.patient_repository = patient_repository
        self.doctor_repository = doctor_repository
        self.image_repository = image_repository
        self.analysis_repository = analysis_repository
        self.result_repository = result_repository
        self.payment_repository = payment_repository
        self.subscription_repository = subscription_repository
        self.model_version_repository = model_version_repository
    
    # ========== FR-35: Global Dashboard ==========
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get global dashboard summary (FR-35)
        Returns: usage, revenue, and AI performance metrics
        """
        # Get all accounts
        all_accounts = self.account_repository.get_all()
        
        # Count by role
        users_count = sum(1 for acc in all_accounts if acc.role_id == 1)  # Assuming role_id 1 = Patient
        doctors_count = sum(1 for acc in all_accounts if acc.role_id == 2)  # Assuming role_id 2 = Doctor
        clinics_count = len(self.clinic_repository.get_all())
        
        # Get all images
        all_images = self.image_repository.get_all()
        total_images = len(all_images)
        
        # Get all analyses
        all_analyses = self.analysis_repository.get_all()
        total_analyses = len(all_analyses)
        completed_analyses = sum(1 for a in all_analyses if hasattr(a, 'status') and a.status == 'completed')
        
        # Calculate revenue (from payments)
        all_payments = self.payment_repository.get_all()
        total_revenue = sum(float(p.amount) for p in all_payments if p.status == 'completed')
        
        # Get AI performance metrics
        all_results = self.result_repository.get_all()
        if all_results:
            avg_confidence = sum(float(r.confidence_score) for r in all_results) / len(all_results)
            risk_distribution = {
                'low': sum(1 for r in all_results if r.risk_level == 'low'),
                'medium': sum(1 for r in all_results if r.risk_level == 'medium'),
                'high': sum(1 for r in all_results if r.risk_level == 'high'),
                'critical': sum(1 for r in all_results if r.risk_level == 'critical')
            }
        else:
            avg_confidence = 0.0
            risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        # Get active AI model
        active_model = self.model_version_repository.get_active_model()
        active_model_info = None
        if active_model:
            active_model_info = {
                'model_name': active_model.model_name,
                'version': active_model.version,
                'trained_at': active_model.trained_at.isoformat() if active_model.trained_at else None
            }
        
        return {
            'users': {
                'total_users': users_count,
                'total_doctors': doctors_count,
                'total_clinics': clinics_count
            },
            'usage': {
                'total_images': total_images,
                'total_analyses': total_analyses,
                'completed_analyses': completed_analyses,
                'success_rate': (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
            },
            'revenue': {
                'total_revenue': round(total_revenue, 2),
                'total_payments': len([p for p in all_payments if p.status == 'completed'])
            },
            'ai_performance': {
                'average_confidence': round(avg_confidence, 2),
                'risk_distribution': risk_distribution,
                'active_model': active_model_info
            }
        }
    
    # ========== FR-36: System Analytics ==========
    
    def get_image_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get image analytics (FR-36)
        Args:
            days: Number of days to look back
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_images = self.image_repository.get_all()
        
        # Filter by date range
        recent_images = [
            img for img in all_images
            if hasattr(img, 'upload_time') and img.upload_time and start_date <= img.upload_time <= end_date
        ]
        
        # Count by type
        type_distribution = {}
        for img in recent_images:
            img_type = getattr(img, 'image_type', 'unknown')
            type_distribution[img_type] = type_distribution.get(img_type, 0) + 1
        
        # Count by status
        status_distribution = {}
        for img in recent_images:
            status = getattr(img, 'status', 'unknown')
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        return {
            'period_days': days,
            'total_images': len(recent_images),
            'type_distribution': type_distribution,
            'status_distribution': status_distribution,
            'daily_upload_trend': self._calculate_daily_trend(recent_images, 'upload_time')
        }
    
    def get_risk_distribution_analytics(self) -> Dict[str, Any]:
        """
        Get risk distribution analytics (FR-36)
        """
        all_results = self.result_repository.get_all()
        
        risk_distribution = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        
        confidence_scores = []
        
        for result in all_results:
            risk_level = result.risk_level.lower() if result.risk_level else 'unknown'
            if risk_level in risk_distribution:
                risk_distribution[risk_level] += 1
            
            if result.confidence_score:
                confidence_scores.append(float(result.confidence_score))
        
        total = sum(risk_distribution.values())
        percentages = {
            k: round((v / total * 100), 2) if total > 0 else 0
            for k, v in risk_distribution.items()
        }
        
        return {
            'risk_distribution': risk_distribution,
            'risk_percentages': percentages,
            'total_results': total,
            'average_confidence': round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0,
            'min_confidence': round(min(confidence_scores), 2) if confidence_scores else 0,
            'max_confidence': round(max(confidence_scores), 2) if confidence_scores else 0
        }
    
    def get_revenue_analytics(self, days: Optional[int] = 30) -> Dict[str, Any]:
        """
        Get revenue analytics (FR-36)
        Args:
            days: Number of days to look back (None = all time)
        """
        all_payments = self.payment_repository.get_all()
        
        # Filter by date range if days is specified
        if days is not None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Filter by date range
            recent_payments = [
                p for p in all_payments
                if hasattr(p, 'payment_time') and p.payment_time and start_date <= p.payment_time <= end_date
            ]
        else:
            # All payments (no date filter)
            recent_payments = all_payments
        
        completed_payments = [p for p in recent_payments if p.status == 'completed']
        
        total_revenue = sum(float(p.amount) for p in completed_payments)
        
        # Group by payment method
        method_distribution = {}
        for p in completed_payments:
            method = p.payment_method or 'unknown'
            method_distribution[method] = method_distribution.get(method, 0) + 1
        
        # Get all-time stats for comparison
        all_completed_payments = [p for p in all_payments if p.status == 'completed']
        all_time_revenue = sum(float(p.amount) for p in all_completed_payments)
        
        return {
            'period_days': days if days is not None else None,
            'period_label': f'Last {days} days' if days is not None else 'All time',
            'total_revenue': round(total_revenue, 2),
            'total_payments': len(completed_payments),
            'average_payment': round(total_revenue / len(completed_payments), 2) if completed_payments else 0,
            'payment_method_distribution': method_distribution,
            'daily_revenue_trend': self._calculate_daily_trend(completed_payments, 'payment_time', amount_field='amount'),
            # Additional context
            'all_time_total_revenue': round(all_time_revenue, 2),
            'all_time_total_payments': len(all_completed_payments),
            'has_data': len(completed_payments) > 0
        }
    
    def get_error_rate_analytics(self) -> Dict[str, Any]:
        """
        Get error rate analytics (FR-36)
        """
        all_analyses = self.analysis_repository.get_all()
        
        total = len(all_analyses)
        if total == 0:
            return {
                'total_analyses': 0,
                'error_rate': 0,
                'status_breakdown': {}
            }
        
        status_breakdown = {}
        for analysis in all_analyses:
            status = getattr(analysis, 'status', 'unknown')
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        failed_count = status_breakdown.get('failed', 0)
        error_rate = (failed_count / total * 100) if total > 0 else 0
        
        return {
            'total_analyses': total,
            'failed_analyses': failed_count,
            'error_rate': round(error_rate, 2),
            'status_breakdown': status_breakdown
        }
    
    # ========== FR-33: AI Configuration ==========
    
    def get_ai_configuration(self) -> Dict[str, Any]:
        """
        Get AI configuration (FR-33)
        Returns: model versions, thresholds, and retraining policies
        """
        all_models = self.model_version_repository.get_all()
        active_model = self.model_version_repository.get_active_model()
        
        models_info = []
        for model in all_models:
            models_info.append({
                'ai_model_version_id': model.ai_model_version_id,
                'model_name': model.model_name,
                'version': model.version,
                'threshold_config': model.threshold_config,
                'trained_at': model.trained_at.isoformat() if model.trained_at else None,
                'active_flag': model.active_flag
            })
        
        active_config = None
        if active_model:
            active_config = {
                'ai_model_version_id': active_model.ai_model_version_id,
                'model_name': active_model.model_name,
                'version': active_model.version,
                'threshold_config': active_model.threshold_config,
                'trained_at': active_model.trained_at.isoformat() if active_model.trained_at else None
            }
        
        return {
            'active_model': active_config,
            'all_models': models_info,
            'retraining_policies': {
                'auto_retrain': False,  # Placeholder - can be extended
                'retrain_threshold': 0.85,  # Placeholder
                'last_retrain': active_model.trained_at.isoformat() if active_model and active_model.trained_at else None
            }
        }
    
    def update_ai_configuration(self, threshold_config: Optional[str] = None,
                               retraining_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update AI configuration (FR-33)
        Args:
            threshold_config: New threshold configuration (JSON string)
            retraining_policy: Retraining policy settings
        """
        active_model = self.model_version_repository.get_active_model()
        if not active_model:
            raise NotFoundException("No active AI model found")
        
        updates = {}
        if threshold_config:
            updates['threshold_config'] = threshold_config
        
        if updates:
            updated_model = self.model_version_repository.update(
                active_model.ai_model_version_id,
                **updates
            )
            if not updated_model:
                raise ValueError("Failed to update AI configuration")
        
        return self.get_ai_configuration()
    
    # ========== Helper Methods ==========
    
    def _calculate_daily_trend(self, items: List[Any], date_field: str, amount_field: Optional[str] = None) -> List[Dict[str, Any]]:
        """Calculate daily trend from items"""
        daily_data = {}
        
        for item in items:
            date_value = getattr(item, date_field, None)
            if not date_value:
                continue
            
            if isinstance(date_value, datetime):
                date_key = date_value.date().isoformat()
            else:
                date_key = str(date_value)
            
            if date_key not in daily_data:
                daily_data[date_key] = {'count': 0, 'amount': 0.0}
            
            daily_data[date_key]['count'] += 1
            
            if amount_field:
                amount = getattr(item, amount_field, 0)
                if amount:
                    daily_data[date_key]['amount'] += float(amount)
        
        # Convert to list sorted by date
        trend = [
            {
                'date': date,
                'count': data['count'],
                'amount': round(data['amount'], 2) if amount_field else None
            }
            for date, data in sorted(daily_data.items())
        ]
        
        return trend