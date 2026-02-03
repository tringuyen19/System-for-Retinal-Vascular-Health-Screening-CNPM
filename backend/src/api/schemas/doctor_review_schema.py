from marshmallow import Schema, fields

class DoctorReviewCreateRequestSchema(Schema):
    """Schema for creating a Doctor Review (FR-19: ai_accuracy_feedback for AI improvement)"""
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    validation_status = fields.Str(required=True, metadata={'description': "Validation status (approved/rejected/needs_revision)"})
    comment = fields.Str(allow_none=True, metadata={'description': "Doctor's comment"})
    ai_accuracy_feedback = fields.Str(allow_none=True, metadata={'description': "FR-19: AI accuracy feedback (correct/incorrect/partially_correct)"})

class DoctorReviewUpdateRequestSchema(Schema):
    """Schema for updating a Doctor Review"""
    validation_status = fields.Str(metadata={'description': "Validation status"})
    comment = fields.Str(allow_none=True, metadata={'description': "Doctor's comment"})
    ai_accuracy_feedback = fields.Str(allow_none=True, metadata={'description': "FR-19: AI accuracy feedback"})

class DoctorReviewResponseSchema(Schema):
    """Schema for Doctor Review response"""
    review_id = fields.Int(required=True, metadata={'description': "Unique review identifier"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    validation_status = fields.Str(required=True, metadata={'description': "Validation status"})
    comment = fields.Str(allow_none=True, metadata={'description': "Doctor's comment"})
    ai_accuracy_feedback = fields.Str(allow_none=True, metadata={'description': "FR-19: AI accuracy feedback"})
    reviewed_at = fields.DateTime(required=True, metadata={'description': "Review timestamp"})

