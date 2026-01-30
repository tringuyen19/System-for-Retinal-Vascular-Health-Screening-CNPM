from marshmallow import Schema, fields

class AccountCreateRequestSchema(Schema):
    """Schema for creating an Account"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    role_id = fields.Int(required=True)
    clinic_id = fields.Int(allow_none=True)
    status = fields.Str(load_default="active")

class AccountUpdateRequestSchema(Schema):
    """Schema for updating an Account"""
    email = fields.Email()
    password = fields.Str(load_only=True)
    role_id = fields.Int()
    clinic_id = fields.Int(allow_none=True)
    status = fields.Str()

class AccountResponseSchema(Schema):
    """Schema for Account response"""
    account_id = fields.Int(required=True)
    email = fields.Email(required=True)
    role_id = fields.Int(required=True)
    clinic_id = fields.Int(allow_none=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(required=True)

