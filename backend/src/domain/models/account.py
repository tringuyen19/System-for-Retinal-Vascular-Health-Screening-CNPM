from datetime import datetime
from typing import Optional

class Account:
    def __init__(self, account_id: int, email: str, password_hash: str, 
                 role_id: int, clinic_id: Optional[int], status: str, created_at: datetime):
        self.account_id = account_id
        self.email = email
        self.password_hash = password_hash
        self.role_id = role_id
        self.clinic_id = clinic_id
        self.status = status
        self.created_at = created_at

