from marshmallow import Schema, fields

class RetinalImageCreateRequestSchema(Schema):
    """Schema for uploading a Retinal Image"""
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    clinic_id = fields.Int(required=True, metadata={'description': "Clinic ID"})
    uploaded_by = fields.Int(required=True, metadata={'description': "Account ID of uploader"})
    image_type = fields.Str(required=True, metadata={'description': "Type of retinal image"})
    eye_side = fields.Str(required=True, metadata={'description': "Eye side (left/right)"})
    image_url = fields.Str(required=True, metadata={'description': "URL to the image"})
    status = fields.Str(load_default="uploaded", metadata={'description': "Image status (uploaded/processing/analyzed)"})
    notes = fields.Str(allow_none=True, metadata={'description': "Optional notes about the image"})

class RetinalImageUpdateRequestSchema(Schema):
    """Schema for updating a Retinal Image"""
    image_type = fields.Str(metadata={'description': "Type of retinal image"})
    eye_side = fields.Str(metadata={'description': "Eye side"})
    image_url = fields.Str(metadata={'description': "URL to the image"})
    status = fields.Str(metadata={'description': "Image status"})

class RetinalImageResponseSchema(Schema):
    """Schema for Retinal Image response"""
    image_id = fields.Int(required=True, metadata={'description': "Unique image identifier"})
    patient_id = fields.Int(required=True, metadata={'description': "Patient ID"})
    clinic_id = fields.Int(required=True, metadata={'description': "Clinic ID"})
    uploaded_by = fields.Int(required=True, metadata={'description': "Account ID of uploader"})
    image_type = fields.Str(required=True, metadata={'description': "Type of retinal image"})
    eye_side = fields.Str(required=True, metadata={'description': "Eye side"})
    image_url = fields.Str(required=True, metadata={'description': "URL to the image"})
    upload_time = fields.DateTime(required=True, metadata={'description': "Upload timestamp"})
    status = fields.Str(required=True, metadata={'description': "Image status"})

class RetinalImageBulkCreateRequestSchema(Schema):
    """Schema for bulk image upload"""
    images = fields.List(fields.Nested(RetinalImageCreateRequestSchema), required=True)

