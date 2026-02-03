from marshmallow import Schema, fields

class MedicalReportCreateRequestSchema(Schema):
    """Schema for creating a Medical Report (FR-16: medical notes, diagnosis, treatment recommendations)"""
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    report_url = fields.Str(load_default='', metadata={'description': "URL to the report document (optional)"})
    medical_notes = fields.Str(load_default='', metadata={'description': "Ghi chú y khoa"})
    diagnosis = fields.Str(load_default='', metadata={'description': "Chẩn đoán"})
    treatment_recommendations = fields.Str(load_default='', metadata={'description': "Khuyến nghị điều trị"})

class MedicalReportUpdateRequestSchema(Schema):
    """Schema for updating a Medical Report"""
    report_url = fields.Str(metadata={'description': "URL to the report document"})
    medical_notes = fields.Str(metadata={'description': "Ghi chú y khoa"})
    diagnosis = fields.Str(metadata={'description': "Chẩn đoán"})
    treatment_recommendations = fields.Str(metadata={'description': "Khuyến nghị điều trị"})

class MedicalReportResponseSchema(Schema):
    """Schema for Medical Report response"""
    report_id = fields.Int(required=True, metadata={'description': "Unique report identifier"})
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    report_url = fields.Str(metadata={'description': "URL to the report document"})
    medical_notes = fields.Str(metadata={'description': "Ghi chú y khoa"})
    diagnosis = fields.Str(metadata={'description': "Chẩn đoán"})
    treatment_recommendations = fields.Str(metadata={'description': "Khuyến nghị điều trị"})
    created_at = fields.DateTime(required=True, metadata={'description': "Report creation timestamp"})

