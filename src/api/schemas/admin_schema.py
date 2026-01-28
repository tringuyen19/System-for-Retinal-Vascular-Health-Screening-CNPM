"""
Admin Schemas - Request/Response validation for admin endpoints
"""

from marshmallow import Schema, fields, validate


class AiConfigurationUpdateRequestSchema(Schema):
    """Schema for updating AI configuration"""
    threshold_config = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    retraining_policy = fields.Dict(required=False, allow_none=True)


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