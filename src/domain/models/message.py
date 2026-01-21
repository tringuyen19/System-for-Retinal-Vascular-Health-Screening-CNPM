from datetime import datetime

class Message:
    def __init__(self, message_id: int, conversation_id: int, sender_type: str, 
                 sender_name: str, content: str, message_type: str, sent_at: datetime):
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.sender_type = sender_type
        self.sender_name = sender_name
        self.content = content
        self.message_type = message_type
        self.sent_at = sent_at

