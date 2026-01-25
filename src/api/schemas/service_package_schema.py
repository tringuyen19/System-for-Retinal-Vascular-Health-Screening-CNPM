from marshmallow import Schema, fields

class ServicePackageCreateRequestSchema(Schema):
    """Schema for creating a Service Package"""
    name = fields.Str(required=True, metadata={'description': "Package name"})
    price = fields.Decimal(required=True, as_string=True, metadata={'description': "Package price"})
    image_limit = fields.Int(required=True, metadata={'description': "Number of images allowed"})
    duration_days = fields.Int(required=True, metadata={'description': "Package duration in days"})

class ServicePackageUpdateRequestSchema(Schema):
    """Schema for updating a Service Package"""
    name = fields.Str(metadata={'description': "Package name"})
    price = fields.Decimal(as_string=True, metadata={'description': "Package price"})
    image_limit = fields.Int(metadata={'description': "Number of images allowed"})
    duration_days = fields.Int(metadata={'description': "Package duration in days"})

class ServicePackageResponseSchema(Schema):
    """Schema for Service Package response"""
    package_id = fields.Int(required=True, metadata={'description': "Unique package identifier"})
    name = fields.Str(required=True, metadata={'description': "Package name"})
    price = fields.Decimal(required=True, as_string=True, metadata={'description': "Package price"})
    image_limit = fields.Int(required=True, metadata={'description': "Number of images allowed"})
    duration_days = fields.Int(required=True, metadata={'description': "Package duration in days"})

