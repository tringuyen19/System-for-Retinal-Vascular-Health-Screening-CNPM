"""
Notification Template Schemas - Request/Response validation for notification template endpoints
"""

from marshmallow import Schema, fields, validate


class NotificationTemplateCreateRequestSchema(Schema):
    """Schema for creating notification template"""
    template_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    template_type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    subject = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))
    content_template = fields.Str(required=True, validate=validate.Length(min=1))
    variables_schema = fields.Dict(required=False, allow_none=True)
    is_active = fields.Bool(required=False, load_default=False)


class NotificationTemplateUpdateRequestSchema(Schema):
    """Schema for updating notification template"""
    template_name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    subject = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255))
    content_template = fields.Str(required=False, validate=validate.Length(min=1))
    variables_schema = fields.Dict(required=False, allow_none=True)


class NotificationTemplateRenderRequestSchema(Schema):
    """Schema for rendering template with variables"""
    variables = fields.Dict(required=True)


class NotificationTemplateResponseSchema(Schema):
    """Schema for notification template response"""
    template_id = fields.Int(required=True)
    template_name = fields.Str(required=True)
    template_type = fields.Str(required=True)
    subject = fields.Str(required=False, allow_none=True)
    content_template = fields.Str(required=True)
    variables_schema = fields.Str(required=False, allow_none=True)  # JSON string
    is_active = fields.Bool(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)