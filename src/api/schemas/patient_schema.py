from marshmallow import Schema, fields

class PatientProfileCreateRequestSchema(Schema):
    """Schema for creating a Patient Profile"""
    account_id = fields.Int(required=True, metadata={'description': "Associated account ID"})
    patient_name = fields.Str(required=True, metadata={'description': "Patient's full name"})
    date_of_birth = fields.Date(allow_none=True, metadata={'description': "Patient's date of birth"})
    gender = fields.Str(allow_none=True, metadata={'description': "Patient's gender"})
    medical_history = fields.Str(allow_none=True, metadata={'description': "Patient's medical history"})

class PatientProfileUpdateRequestSchema(Schema):
    """Schema for updating a Patient Profile"""
    patient_name = fields.Str(metadata={'description': "Patient's full name"})
    date_of_birth = fields.Date(allow_none=True, metadata={'description': "Patient's date of birth"})
    gender = fields.Str(allow_none=True, metadata={'description': "Patient's gender"})
    medical_history = fields.Str(allow_none=True, metadata={'description': "Patient's medical history"})

class PatientProfileResponseSchema(Schema):
    """Schema for Patient Profile response"""
    patient_id = fields.Int(required=True, metadata={'description': "Unique patient identifier"})
    account_id = fields.Int(required=True, metadata={'description': "Associated account ID"})
    patient_name = fields.Str(required=True, metadata={'description': "Patient's full name"})
    date_of_birth = fields.Date(allow_none=True, metadata={'description': "Patient's date of birth"})
    gender = fields.Str(allow_none=True, metadata={'description': "Patient's gender"})
    medical_history = fields.Str(allow_none=True, metadata={'description': "Patient's medical history"})

