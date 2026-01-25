from marshmallow import Schema, fields

class AiResultCreateRequestSchema(Schema):
    """Schema for creating an AI Result"""
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    disease_type = fields.Str(required=True, metadata={'description': "Detected disease type"})
    risk_level = fields.Str(required=True, metadata={'description': "Risk level (low/medium/high)"})
    confidence_score = fields.Decimal(required=True, as_string=True, metadata={'description': "AI confidence score (0-1)"})

class AiResultUpdateRequestSchema(Schema):
    """Schema for updating an AI Result"""
    disease_type = fields.Str(metadata={'description': "Detected disease type"})
    risk_level = fields.Str(metadata={'description': "Risk level"})
    confidence_score = fields.Decimal(as_string=True, metadata={'description': "AI confidence score"})

class AiResultResponseSchema(Schema):
    """Schema for AI Result response"""
    result_id = fields.Int(required=True, metadata={'description': "Unique result identifier"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    disease_type = fields.Str(required=True, metadata={'description': "Detected disease type"})
    risk_level = fields.Str(required=True, metadata={'description': "Risk level"})
    confidence_score = fields.Decimal(required=True, as_string=True, metadata={'description': "AI confidence score"})

