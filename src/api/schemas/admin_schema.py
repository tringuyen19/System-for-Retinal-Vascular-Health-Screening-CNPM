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