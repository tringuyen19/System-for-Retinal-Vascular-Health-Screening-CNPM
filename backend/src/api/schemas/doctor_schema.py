from marshmallow import Schema, fields

class DoctorProfileCreateRequestSchema(Schema):
    """Schema for creating a Doctor Profile"""
    account_id = fields.Int(required=True, metadata={'description': "Associated account ID"})
    doctor_name = fields.Str(required=True, metadata={'description': "Doctor's full name"})
    specialization = fields.Str(required=True, metadata={'description': "Doctor's specialization"})
    license_number = fields.Str(required=True, metadata={'description': "Medical license number"})

class DoctorProfileUpdateRequestSchema(Schema):
    """Schema for updating a Doctor Profile"""
    doctor_name = fields.Str(metadata={'description': "Doctor's full name"})
    specialization = fields.Str(metadata={'description': "Doctor's specialization"})
    license_number = fields.Str(metadata={'description': "Medical license number"})

class DoctorProfileResponseSchema(Schema):
    """Schema for Doctor Profile response"""
    doctor_id = fields.Int(required=True, metadata={'description': "Unique doctor identifier"})
    account_id = fields.Int(required=True, metadata={'description': "Associated account ID"})
    doctor_name = fields.Str(required=True, metadata={'description': "Doctor's full name"})
    specialization = fields.Str(required=True, metadata={'description': "Doctor's specialization"})
    license_number = fields.Str(required=True, metadata={'description': "Medical license number"})

