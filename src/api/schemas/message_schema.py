from marshmallow import Schema, fields

class MessageCreateRequestSchema(Schema):
    """Schema for creating a Message"""
    conversation_id = fields.Int(required=True, metadata={'description': "Conversation ID"})
    sender_type = fields.Str(required=True, metadata={'description': "Sender type (patient/doctor)"})
    sender_name = fields.Str(required=True, metadata={'description': "Sender's name"})
    content = fields.Str(required=True, metadata={'description': "Message content"})
    message_type = fields.Str(required=True, metadata={'description': "Message type (text/image/file)"})

class MessageResponseSchema(Schema):
    """Schema for Message response"""
    message_id = fields.Int(required=True, metadata={'description': "Unique message identifier"})
    conversation_id = fields.Int(required=True, metadata={'description': "Conversation ID"})
    sender_type = fields.Str(required=True, metadata={'description': "Sender type"})
    sender_name = fields.Str(required=True, metadata={'description': "Sender's name"})
    content = fields.Str(required=True, metadata={'description': "Message content"})
    message_type = fields.Str(required=True, metadata={'description': "Message type"})
    sent_at = fields.DateTime(required=True, metadata={'description': "Message sent timestamp"})

