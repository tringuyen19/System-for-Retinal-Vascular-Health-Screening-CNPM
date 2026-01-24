from marshmallow import Schema, fields

class ClinicCreateRequestSchema(Schema):
    """Schema for creating a Clinic"""
    name = fields.Str(required=True, metadata={'description': "Clinic name"})
    address = fields.Str(required=True, metadata={'description': "Clinic address"})
    phone = fields.Str(required=True, metadata={'description': "Clinic phone number"})
    logo_url = fields.Str(required=True, metadata={'description': "Clinic logo URL"})
    verification_status = fields.Str(load_default="pending", metadata={'description': "Verification status (pending/verified/rejected)"})

class ClinicUpdateRequestSchema(Schema):
    """Schema for updating a Clinic"""
    name = fields.Str(metadata={'description': "Clinic name"})
    address = fields.Str(metadata={'description': "Clinic address"})
    phone = fields.Str(metadata={'description': "Clinic phone number"})
    logo_url = fields.Str(metadata={'description': "Clinic logo URL"})
    verification_status = fields.Str(metadata={'description': "Verification status"})

class ClinicResponseSchema(Schema):
    """Schema for Clinic response"""
    clinic_id = fields.Int(required=True, metadata={'description': "Unique clinic identifier"})
    name = fields.Str(required=True, metadata={'description': "Clinic name"})
    address = fields.Str(required=True, metadata={'description': "Clinic address"})
    phone = fields.Str(required=True, metadata={'description': "Clinic phone number"})
    logo_url = fields.Str(required=True, metadata={'description': "Clinic logo URL"})
    verification_status = fields.Str(required=True, metadata={'description': "Verification status"})
    created_at = fields.DateTime(required=True, metadata={'description': "Clinic creation timestamp"})

