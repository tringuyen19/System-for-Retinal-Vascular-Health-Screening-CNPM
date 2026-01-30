from marshmallow import Schema, fields

class AiAnnotationCreateRequestSchema(Schema):
    """Schema for creating an AI Annotation"""
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    heatmap_url = fields.Str(required=True, metadata={'description': "URL to the heatmap image"})
    description = fields.Str(allow_none=True, metadata={'description': "Annotation description"})

class AiAnnotationUpdateRequestSchema(Schema):
    """Schema for updating an AI Annotation"""
    heatmap_url = fields.Str(metadata={'description': "URL to the heatmap image"})
    description = fields.Str(allow_none=True, metadata={'description': "Annotation description"})

class AiAnnotationResponseSchema(Schema):
    """Schema for AI Annotation response"""
    annotation_id = fields.Int(required=True, metadata={'description': "Unique annotation identifier"})
    analysis_id = fields.Int(required=True, metadata={'description': "Analysis ID"})
    heatmap_url = fields.Str(required=True, metadata={'description': "URL to the heatmap image"})
    description = fields.Str(allow_none=True, metadata={'description': "Annotation description"})

