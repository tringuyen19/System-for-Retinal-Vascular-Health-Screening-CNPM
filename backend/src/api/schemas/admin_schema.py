"""
Admin Schemas - Request/Response validation for admin endpoints
"""

from marshmallow import Schema, fields, validate


class RetrainingPolicySchema(Schema):
    """Schema for retraining policy nested object"""
    auto_retrain = fields.Bool(required=False, allow_none=True)
    retrain_threshold = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0, max=1))
    retrain_schedule = fields.Str(required=False, allow_none=True, validate=validate.OneOf(['daily', 'weekly', 'monthly', 'quarterly']))
    min_samples_for_retrain = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    min_accuracy_improvement = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0, max=1))
    retrain_on_error_rate = fields.Bool(required=False, allow_none=True)
    max_error_rate_threshold = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0, max=1))


class AiConfigurationUpdateRequestSchema(Schema):
    """Schema for updating AI configuration"""
    threshold_config = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    retraining_policy = fields.Nested(RetrainingPolicySchema, required=False, allow_none=True)


class AdminDashboardResponseSchema(Schema):
    """Schema for admin dashboard response"""
    users = fields.Dict(required=True)
    usage = fields.Dict(required=True)
    revenue = fields.Dict(required=True)
    ai_performance = fields.Dict(required=True)


class AdminAnalyticsResponseSchema(Schema):
    """Schema for admin analytics response"""
    period_days = fields.Int(required=False)
    total_images = fields.Int(required=False)
    total_analyses = fields.Int(required=False)
    total_revenue = fields.Float(required=False)
    risk_distribution = fields.Dict(required=False)
    error_rate = fields.Float(required=False)
# Add other analytics fields as needed


class PrivacySettingsUpdateRequestSchema(Schema):
    """Schema for updating privacy settings (FR-37)"""
    data_retention_days = fields.Int(required=False, validate=validate.Range(min=1, max=3650))
    auto_anonymize_after_days = fields.Int(required=False, validate=validate.Range(min=1, max=3650))
    require_consent_for_ai_training = fields.Bool(required=False)
    allow_data_sharing = fields.Bool(required=False)
    anonymize_patient_data = fields.Bool(required=False)
    encrypt_sensitive_data = fields.Bool(required=False)
    audit_data_access = fields.Bool(required=False)
    gdpr_compliance_mode = fields.Bool(required=False)


class PrivacySettingsResponseSchema(Schema):
    """Schema for privacy settings response (FR-37)"""
    data_retention_days = fields.Int(required=True)
    auto_anonymize_after_days = fields.Int(required=True)
    require_consent_for_ai_training = fields.Bool(required=True)
    allow_data_sharing = fields.Bool(required=True)
    anonymize_patient_data = fields.Bool(required=True)
    encrypt_sensitive_data = fields.Bool(required=True)
    audit_data_access = fields.Bool(required=True)
    gdpr_compliance_mode = fields.Bool(required=True)


class CommunicationPolicySchema(Schema):
    """Schema for communication policy nested object (FR-39)"""
    enabled = fields.Bool(required=True)
    channels = fields.List(fields.Str(validate=validate.OneOf(['in_app', 'email', 'sms'])), required=True)
    recipients = fields.List(fields.Str(validate=validate.OneOf(['patient', 'doctor', 'clinic_manager', 'admin'])), required=True)
    frequency_limit = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    priority = fields.Str(required=True, validate=validate.OneOf(['low', 'normal', 'high', 'urgent']))


class CommunicationPolicyUpdateRequestSchema(Schema):
    """Schema for updating communication policy (FR-39)"""
    enabled = fields.Bool(required=False)
    channels = fields.List(fields.Str(validate=validate.OneOf(['in_app', 'email', 'sms'])), required=False)
    recipients = fields.List(fields.Str(validate=validate.OneOf(['patient', 'doctor', 'clinic_manager', 'admin'])), required=False)
    frequency_limit = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    priority = fields.Str(required=False, validate=validate.OneOf(['low', 'normal', 'high', 'urgent']))


class CommunicationPoliciesResponseSchema(Schema):
    """Schema for communication policies response (FR-39)"""
    policies = fields.Dict(required=True)