from marshmallow import Schema, fields

class MedicalReportCreateRequestSchema(Schema):
    """Schema for creating a Medical Report"""
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    report_url = fields.Str(required=True, metadata={'description': "URL to the report document"})

class MedicalReportUpdateRequestSchema(Schema):
    """Schema for updating a Medical Report"""
    report_url = fields.Str(metadata={'description': "URL to the report document"})

class MedicalReportResponseSchema(Schema):
    """Schema for Medical Report response"""
    report_id = fields.Int(required=True, metadata={'description': "Unique report identifier"})
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    report_url = fields.Str(required=True, metadata={'description': "URL to the report document"})
    created_at = fields.DateTime(required=True, metadata={'description': "Report creation timestamp"})

