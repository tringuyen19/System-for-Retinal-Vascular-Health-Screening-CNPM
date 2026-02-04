from datetime import datetime
from typing import Optional, List

class Clinic:
    def __init__(self, clinic_id: int, name: str, address: str, phone: str, 
                 logo_url: str, verification_status: str, created_at: datetime,
                 license_number: Optional[str] = None, tax_id: Optional[str] = None,
                 verification_documents: Optional[List[str]] = None, manager_email: Optional[str] = None):
        self.clinic_id = clinic_id
        self.name = name
        self.address = address
        self.phone = phone
        self.logo_url = logo_url
        self.verification_status = verification_status
        self.created_at = created_at
        # Organization verification fields (FR-22)
        self.license_number = license_number
        self.tax_id = tax_id
        self.verification_documents = verification_documents or []
        self.manager_email = manager_email

