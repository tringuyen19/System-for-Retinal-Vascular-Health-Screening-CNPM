from marshmallow import Schema, fields

class NotificationCreateRequestSchema(Schema):
    """Schema for creating a Notification"""
    account_id = fields.Int(required=True, metadata={'description': "Recipient account ID"})
    notification_type = fields.Str(required=True, metadata={'description': "Type of notification"})
    content = fields.Str(required=True, metadata={'description': "Notification content"})
    is_read = fields.Bool(load_default=False, metadata={'description': "Read status"})

class NotificationUpdateRequestSchema(Schema):
    """Schema for updating a Notification"""
    is_read = fields.Bool(metadata={'description': "Read status"})

class NotificationResponseSchema(Schema):
    """Schema for Notification response"""
    notification_id = fields.Int(required=True, metadata={'description': "Unique notification identifier"})
    account_id = fields.Int(required=True, metadata={'description': "Recipient account ID"})
    notification_type = fields.Str(required=True, metadata={'description': "Type of notification"})
    content = fields.Str(required=True, metadata={'description': "Notification content"})
    is_read = fields.Bool(required=True, metadata={'description': "Read status"})
    created_at = fields.DateTime(required=True, metadata={'description': "Notification creation timestamp"})

