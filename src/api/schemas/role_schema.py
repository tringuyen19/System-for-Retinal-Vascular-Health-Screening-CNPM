from marshmallow import Schema, fields

class RoleRequestSchema(Schema):
    """Schema for creating/updating a Role"""
    role_name = fields.Str(required=True, metadata={'description': "Name of the role"})

class RoleResponseSchema(Schema):
    """Schema for Role response"""
    role_id = fields.Int(required=True, metadata={'description': "Unique role identifier"})
    role_name = fields.Str(required=True, metadata={'description': "Name of the role"})

