from datetime import datetime
from typing import Optional

class NotificationTemplate:
    """Domain model for Notification Template - Pure Python, no framework dependencies"""
    def __init__(self, template_id: int, template_name: str, template_type: str,
                 subject: Optional[str], content_template: str,
                 variables_schema: Optional[str], is_active: bool,
                 created_at: datetime, updated_at: datetime):
        self.template_id = template_id
        self.template_name = template_name
        self.template_type = template_type
        self.subject = subject
        self.content_template = content_template
        self.variables_schema = variables_schema  # JSON string
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at