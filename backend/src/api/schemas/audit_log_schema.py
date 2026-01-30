"""
Audit Log Schemas - Request/Response validation for audit log endpoints
"""

from marshmallow import Schema, fields, validate
from datetime import date


class AuditLogCreateRequestSchema(Schema):
    """Schema for creating audit log entry"""
    account_id = fields.Int(required=False, allow_none=True)
    action_type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    entity_type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    entity_id = fields.Int(required=False, allow_none=True)
    old_values = fields.Dict(required=False, allow_none=True)
    new_values = fields.Dict(required=False, allow_none=True)
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))
    ip_address = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    user_agent = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))


class AuditLogResponseSchema(Schema):
    """Schema for audit log response"""
    audit_log_id = fields.Int(required=True)
    account_id = fields.Int(required=False, allow_none=True)
    action_type = fields.Str(required=True)
    entity_type = fields.Str(required=True)
    entity_id = fields.Int(required=False, allow_none=True)
    old_values = fields.Str(required=False, allow_none=True)  # JSON string
    new_values = fields.Str(required=False, allow_none=True)  # JSON string
    description = fields.Str(required=False, allow_none=True)
    ip_address = fields.Str(required=False, allow_none=True)
    user_agent = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(required=True)


class AuditLogSearchRequestSchema(Schema):
    """Schema for audit log search filters"""
    account_id = fields.Int(required=False, allow_none=True)
    action_type = fields.Str(required=False, allow_none=True)
    entity_type = fields.Str(required=False, allow_none=True)
    entity_id = fields.Int(required=False, allow_none=True)
    start_date = fields.Date(required=False, allow_none=True)
    end_date = fields.Date(required=False, allow_none=True)
    limit = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=1000))
    offset = fields.Int(required=False, load_default=0, validate=validate.Range(min=0))