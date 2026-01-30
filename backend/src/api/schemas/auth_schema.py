from marshmallow import Schema, fields, validate

class LoginRequestSchema(Schema):
    """Schema for login request"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)

class RegisterRequestSchema(Schema):
    """Schema for registration request"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6, error="Password must be at least 6 characters"))
    role_id = fields.Int(required=True)
    clinic_id = fields.Int(allow_none=True)

class AuthResponseSchema(Schema):
    """Schema for authentication response"""
    access_token = fields.Str(required=True)
    account_id = fields.Int(required=True)
    email = fields.Email(required=True)
    role_id = fields.Int(required=True)
    clinic_id = fields.Int(allow_none=True)

