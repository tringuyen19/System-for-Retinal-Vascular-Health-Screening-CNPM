from marshmallow import Schema, fields

class ConversationCreateRequestSchema(Schema):
    """Schema for creating a Conversation"""
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    status = fields.Str(load_default="active", metadata={'description': "Conversation status (active/closed)"})

class ConversationUpdateRequestSchema(Schema):
    """Schema for updating a Conversation"""
    status = fields.Str(metadata={'description': "Conversation status"})

class ConversationResponseSchema(Schema):
    """Schema for Conversation response"""
    conversation_id = fields.Int(required=True, metadata={'description': "Unique conversation identifier"})
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    doctor_id = fields.Int(required=True, metadata={'description': "Doctor ID"})
    created_at = fields.DateTime(required=True, metadata={'description': "Conversation creation timestamp"})
    status = fields.Str(required=True, metadata={'description': "Conversation status"})

