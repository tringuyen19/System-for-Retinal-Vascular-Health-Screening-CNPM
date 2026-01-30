from marshmallow import Schema, fields

class AiModelVersionCreateRequestSchema(Schema):
    """Schema for creating an AI Model Version"""
    model_name = fields.Str(required=True, metadata={'description': "AI model name"})
    version = fields.Str(required=True, metadata={'description': "Model version"})
    threshold_config = fields.Str(required=True, metadata={'description': "Threshold configuration (JSON string)"})
    active_flag = fields.Bool(load_default=True, metadata={'description': "Whether this version is active"})

class AiModelVersionUpdateRequestSchema(Schema):
    """Schema for updating an AI Model Version"""
    model_name = fields.Str(metadata={'description': "AI model name"})
    version = fields.Str(metadata={'description': "Model version"})
    threshold_config = fields.Str(metadata={'description': "Threshold configuration"})
    active_flag = fields.Bool(metadata={'description': "Whether this version is active"})

class AiModelVersionResponseSchema(Schema):
    """Schema for AI Model Version response"""
    ai_model_version_id = fields.Int(required=True, metadata={'description': "Unique model version identifier"})
    model_name = fields.Str(required=True, metadata={'description': "AI model name"})
    version = fields.Str(required=True, metadata={'description': "Model version"})
    threshold_config = fields.Str(required=True, metadata={'description': "Threshold configuration"})
    trained_at = fields.DateTime(required=True, metadata={'description': "Model training timestamp"})
    active_flag = fields.Bool(required=True, metadata={'description': "Whether this version is active"})

