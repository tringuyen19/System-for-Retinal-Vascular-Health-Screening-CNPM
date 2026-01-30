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
      
        # Retraining policies storage (in-memory, can be persisted to file/DB later)
        self._retraining_policies = {
            'auto_retrain': False,
            'retrain_threshold': 0.85,
            'retrain_schedule': 'monthly',  # daily, weekly, monthly, quarterly
            'min_samples_for_retrain': 1000,
            'min_accuracy_improvement': 0.02,  # 2% improvement required
            'last_retrain': None,
            'next_scheduled_retrain': None,
            'retrain_on_error_rate': True,
            'max_error_rate_threshold': 0.15  # 15% error rate triggers retrain
        }

     # Privacy settings storage (in-memory, can be persisted to file/DB later) - FR-37
        self._privacy_settings = {
            'data_retention_days': 365,  # Days to retain data
            'auto_anonymize_after_days': 730,  # Auto anonymize after 2 years
            'require_consent_for_ai_training': True,
            'allow_data_sharing': False,
            'anonymize_patient_data': True,
            'encrypt_sensitive_data': True,
            'audit_data_access': True,
            'gdpr_compliance_mode': True
        }
        
        # Communication policies storage (in-memory, can be persisted to file/DB later) - FR-39
        self._communication_policies = {
            'ai_result_ready': {
                'enabled': True,
                'channels': ['in_app'],  # in_app, email, sms
                'recipients': ['patient'],  # patient, doctor, clinic_manager
                'frequency_limit': None,  # None = no limit, or number per day
                'priority': 'normal'  # low, normal, high, urgent
            },
            'clinic_approved': {
                'enabled': True,
                'channels': ['in_app', 'email'],
                'recipients': ['clinic_manager'],
                'frequency_limit': None,
                'priority': 'high'
            },
            'payment_success': {
                'enabled': True,
                'channels': ['in_app', 'email'],
                'recipients': ['patient', 'clinic_manager'],
                'frequency_limit': None,
                'priority': 'normal'
            },
            'high_risk_alert': {
                'enabled': True,
                'channels': ['in_app', 'email', 'sms'],
                'recipients': ['doctor', 'clinic_manager'],
                'frequency_limit': 10,  # Max 10 per day
                'priority': 'urgent'
            }
        }

    # ========== FR-35: Global Dashboard ==========
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get global dashboard summary (FR-35)
        Returns: usage, revenue, and AI performance metrics
        """
        # Get all accounts
        all_accounts = self.account_repository.get_all()
        
        # Count by role - Get role names dynamically
        from infrastructure.repositories.role_repository import RoleRepository
        from infrastructure.databases.mssql import session
        role_repo = RoleRepository(session)
        
        patient_role = role_repo.get_by_name('Patient')
        doctor_role = role_repo.get_by_name('Doctor')
        
        users_count = sum(1 for acc in all_accounts if patient_role and acc.role_id == patient_role.role_id)
        doctors_count = sum(1 for acc in all_accounts if doctor_role and acc.role_id == doctor_role.role_id)
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
        
        # Get last retrain date from active model if available
        last_retrain = None
        if active_model and active_model.trained_at:
            last_retrain = active_model.trained_at.isoformat()
            # Update stored policy with actual last retrain date
            if not self._retraining_policies.get('last_retrain'):
                self._retraining_policies['last_retrain'] = last_retrain
        
        # Calculate next scheduled retrain if auto_retrain is enabled
        next_scheduled = None
        if self._retraining_policies.get('auto_retrain') and last_retrain:
            from datetime import datetime, timedelta
            last_retrain_dt = datetime.fromisoformat(last_retrain.replace('Z', '+00:00'))
            schedule_days = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30,
                'quarterly': 90
            }
            days = schedule_days.get(self._retraining_policies.get('retrain_schedule', 'monthly'), 30)
            next_scheduled = (last_retrain_dt + timedelta(days=days)).isoformat()
        
        retraining_policies = {
            'auto_retrain': self._retraining_policies.get('auto_retrain', False),
            'retrain_threshold': self._retraining_policies.get('retrain_threshold', 0.85),
            'retrain_schedule': self._retraining_policies.get('retrain_schedule', 'monthly'),
            'min_samples_for_retrain': self._retraining_policies.get('min_samples_for_retrain', 1000),
            'min_accuracy_improvement': self._retraining_policies.get('min_accuracy_improvement', 0.02),
            'last_retrain': last_retrain or self._retraining_policies.get('last_retrain'),
            'next_scheduled_retrain': next_scheduled or self._retraining_policies.get('next_scheduled_retrain'),
            'retrain_on_error_rate': self._retraining_policies.get('retrain_on_error_rate', True),
            'max_error_rate_threshold': self._retraining_policies.get('max_error_rate_threshold', 0.15)
        }

        return {
            'active_model': active_config,
            'all_models': models_info,
            'retraining_policies': retraining_policies
        }
    
    def update_ai_configuration(self, threshold_config: Optional[str] = None,
                               retraining_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update AI configuration (FR-33)
        Args:
            threshold_config: New threshold configuration (JSON string)
            retraining_policy: Retraining policy settings (dict with keys: auto_retrain, retrain_threshold, 
                            retrain_schedule, min_samples_for_retrain, min_accuracy_improvement, 
                            retrain_on_error_rate, max_error_rate_threshold)
        """
        active_model = self.model_version_repository.get_active_model()
        if not active_model:
            raise NotFoundException("No active AI model found")
        
        updates = {}
        if threshold_config:
            updates['threshold_config'] = threshold_config
        
        # Update threshold config in model if provided
        if updates:
            updated_model = self.model_version_repository.update(
                active_model.ai_model_version_id,
                **updates
            )
            if not updated_model:
                raise ValueError("Failed to update AI configuration")
        
        # Update retraining policies if provided
        if retraining_policy:
            # Validate and update retraining policy fields
            allowed_keys = [
                'auto_retrain', 'retrain_threshold', 'retrain_schedule',
                'min_samples_for_retrain', 'min_accuracy_improvement',
                'retrain_on_error_rate', 'max_error_rate_threshold'
            ]
            
            for key, value in retraining_policy.items():
                if key in allowed_keys:
                    self._retraining_policies[key] = value
                else:
                    raise ValueError(f"Invalid retraining policy key: {key}. Allowed keys: {allowed_keys}")
            
            # Validate retrain_threshold range
            if 'retrain_threshold' in retraining_policy:
                threshold = retraining_policy['retrain_threshold']
                if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 1):
                    raise ValueError("retrain_threshold must be a number between 0 and 1")
            
            # Validate retrain_schedule
            if 'retrain_schedule' in retraining_policy:
                schedule = retraining_policy['retrain_schedule']
                if schedule not in ['daily', 'weekly', 'monthly', 'quarterly']:
                    raise ValueError("retrain_schedule must be one of: daily, weekly, monthly, quarterly")
            
            # Validate min_accuracy_improvement
            if 'min_accuracy_improvement' in retraining_policy:
                improvement = retraining_policy['min_accuracy_improvement']
                if not isinstance(improvement, (int, float)) or not (0 <= improvement <= 1):
                    raise ValueError("min_accuracy_improvement must be a number between 0 and 1")
            
            # Validate max_error_rate_threshold
            if 'max_error_rate_threshold' in retraining_policy:
                error_rate = retraining_policy['max_error_rate_threshold']
                if not isinstance(error_rate, (int, float)) or not (0 <= error_rate <= 1):
                    raise ValueError("max_error_rate_threshold must be a number between 0 and 1")

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
 
    # ========== FR-37: Privacy Settings Management ==========
    
    def get_privacy_settings(self) -> Dict[str, Any]:
        """
        Get privacy settings (FR-37)
        Returns: Current privacy settings configuration
        """
        return self._privacy_settings.copy()
    
    def update_privacy_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update privacy settings (FR-37)
        Args:
            settings: Dictionary with privacy settings to update
        Returns: Updated privacy settings
        """
        # Validate settings
        valid_keys = set(self._privacy_settings.keys())
        provided_keys = set(settings.keys())
        
        invalid_keys = provided_keys - valid_keys
        if invalid_keys:
            raise ValueError(f"Invalid privacy settings keys: {invalid_keys}")
        
        # Update settings
        self._privacy_settings.update(settings)
        
        return self._privacy_settings.copy()
    
    # ========== FR-39: Communication Policies Management ==========
    
    def get_communication_policies(self) -> Dict[str, Any]:
        """
        Get communication policies (FR-39)
        Returns: Current communication policies configuration
        """
        return self._communication_policies.copy()
    
    def get_communication_policy_by_type(self, notification_type: str) -> Optional[Dict[str, Any]]:
        """
        Get communication policy for a specific notification type (FR-39)
        Args:
            notification_type: Type of notification (ai_result_ready, clinic_approved, etc.)
        Returns: Policy for the notification type, or None if not found
        """
        return self._communication_policies.get(notification_type)
    
    def update_communication_policy(self, notification_type: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update communication policy for a notification type (FR-39)
        Args:
            notification_type: Type of notification
            policy: Policy settings (enabled, channels, recipients, frequency_limit, priority)
        Returns: Updated policy
        """
        if notification_type not in self._communication_policies:
            raise ValueError(f"Unknown notification type: {notification_type}")
        
        # Validate policy structure
        valid_keys = {'enabled', 'channels', 'recipients', 'frequency_limit', 'priority'}
        provided_keys = set(policy.keys())
        
        invalid_keys = provided_keys - valid_keys
        if invalid_keys:
            raise ValueError(f"Invalid policy keys: {invalid_keys}")
        
        # Validate values
        if 'enabled' in policy and not isinstance(policy['enabled'], bool):
            raise ValueError("'enabled' must be a boolean")
        
        if 'channels' in policy:
            valid_channels = {'in_app', 'email', 'sms'}
            if not all(ch in valid_channels for ch in policy['channels']):
                raise ValueError(f"Invalid channels. Must be one of: {valid_channels}")
        
        if 'recipients' in policy:
            valid_recipients = {'patient', 'doctor', 'clinic_manager', 'admin'}
            if not all(r in valid_recipients for r in policy['recipients']):
                raise ValueError(f"Invalid recipients. Must be one of: {valid_recipients}")
        
        if 'priority' in policy:
            valid_priorities = {'low', 'normal', 'high', 'urgent'}
            if policy['priority'] not in valid_priorities:
                raise ValueError(f"Invalid priority. Must be one of: {valid_priorities}")
        
        # Update policy
        self._communication_policies[notification_type].update(policy)
        
        return self._communication_policies[notification_type].copy()
    
    def create_communication_policy(self, notification_type: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new communication policy for a notification type (FR-39)
        Args:
            notification_type: Type of notification
            policy: Policy settings
        Returns: Created policy
        """
        if notification_type in self._communication_policies:
            raise ValueError(f"Policy for {notification_type} already exists. Use update instead.")
        
        # Validate and create
        required_keys = {'enabled', 'channels', 'recipients', 'priority'}
        if not all(key in policy for key in required_keys):
            raise ValueError(f"Missing required keys: {required_keys - set(policy.keys())}")
        
        self._communication_policies[notification_type] = {
            'enabled': policy['enabled'],
            'channels': policy['channels'],
            'recipients': policy['recipients'],
            'frequency_limit': policy.get('frequency_limit'),
            'priority': policy['priority']
        }
        
        return self._communication_policies[notification_type].copy()