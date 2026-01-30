from datetime import datetime
from typing import Optional

class Notification:
    def __init__(self, notification_id: int, account_id: int, notification_type: str, 
                 content: str, is_read: bool, created_at: datetime):
        self.notification_id = notification_id
        self.account_id = account_id
        self.notification_type = notification_type
        self.content = content
        self.is_read = is_read
        self.created_at = created_at

