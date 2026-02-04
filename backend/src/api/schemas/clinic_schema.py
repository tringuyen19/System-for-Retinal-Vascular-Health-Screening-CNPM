from marshmallow import Schema, fields, validate, ValidationError

class ClinicCreateRequestSchema(Schema):
    """Schema for creating a Clinic with manager account (FR-22)"""
    # Clinic information
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255), metadata={'description': "Clinic name"})
    address = fields.Str(required=True, validate=validate.Length(min=1, max=500), metadata={'description': "Clinic address"})
    phone = fields.Str(required=True, validate=validate.Length(min=1, max=50), metadata={'description': "Clinic phone number"})
    logo_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=255), metadata={'description': "Clinic logo URL (optional)"})
    
    # Organization verification fields (FR-22)
    license_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100), metadata={'description': "Business license number"})
    tax_id = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50), metadata={'description': "Tax identification number"})
    verification_documents = fields.List(fields.Str(), required=False, allow_none=True, metadata={'description': "List of document URLs for verification"})
    
    # Clinic manager account (FR-22)
    manager_email = fields.Email(required=True, metadata={'description': "Email for clinic manager account"})
    manager_password = fields.Str(required=True, validate=validate.Length(min=6), metadata={'description': "Password for clinic manager account"})
    
    verification_status = fields.Str(load_default="pending", validate=validate.OneOf(['pending', 'verified', 'rejected', 'suspended']), metadata={'description': "Verification status (default: pending)"})

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
    logo_url = fields.Str(allow_none=True, metadata={'description': "Clinic logo URL"})
    verification_status = fields.Str(required=True, metadata={'description': "Verification status"})
    license_number = fields.Str(allow_none=True, metadata={'description': "Business license number"})
    tax_id = fields.Str(allow_none=True, metadata={'description': "Tax identification number"})
    verification_documents = fields.List(fields.Str(), allow_none=True, metadata={'description': "List of document URLs"})
    manager_email = fields.Email(allow_none=True, metadata={'description': "Clinic manager email"})
    created_at = fields.DateTime(required=True, metadata={'description': "Clinic creation timestamp"})

