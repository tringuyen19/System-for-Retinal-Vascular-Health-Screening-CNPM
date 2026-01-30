from marshmallow import Schema, fields, validate

# Valid status values for AI Analysis
VALID_STATUSES = ['pending', 'processing', 'completed', 'failed']

class AiAnalysisCreateRequestSchema(Schema):
    """Schema for creating an AI Analysis"""
    image_id = fields.Int(required=True, metadata={'description': "Retinal image ID"})
    ai_model_version_id = fields.Int(required=True, metadata={'description': "AI model version ID"})
    status = fields.Str(
        load_default="pending", 
        validate=validate.OneOf(VALID_STATUSES),
        metadata={
            'description': "Analysis status",
            'enum': VALID_STATUSES,
            'example': 'pending'
        }
    )
    processing_time = fields.Int(allow_none=True, metadata={'description': "Processing time in seconds (optional)"})

class AiAnalysisUpdateRequestSchema(Schema):
    """Schema for updating an AI Analysis"""
    processing_time = fields.Int(metadata={'description': "Processing time in seconds"})
    status = fields.Str(
        validate=validate.OneOf(VALID_STATUSES),
        metadata={
            'description': "Analysis status",
            'enum': VALID_STATUSES,
            'example': 'completed'
        }
    )

class AiAnalysisResponseSchema(Schema):
    """Schema for AI Analysis response"""
    analysis_id = fields.Int(required=True, metadata={'description': "Unique analysis identifier"})
    image_id = fields.Int(required=True, metadata={'description': "Retinal image ID"})
    ai_model_version_id = fields.Int(required=True, metadata={'description': "AI model version ID"})
    analysis_time = fields.DateTime(required=True, metadata={'description': "Analysis timestamp"})
    processing_time = fields.Int(allow_none=True, metadata={'description': "Processing time in seconds"})
    status = fields.Str(required=True, metadata={'description': "Analysis status"})

