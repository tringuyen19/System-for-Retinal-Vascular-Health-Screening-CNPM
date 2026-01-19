from datetime import datetime

class Clinic:
    def __init__(self, clinic_id: int, name: str, address: str, phone: str, 
                 logo_url: str, verification_status: str, created_at: datetime):
        self.clinic_id = clinic_id
        self.name = name
        self.address = address
        self.phone = phone
        self.logo_url = logo_url
        self.verification_status = verification_status
        self.created_at = created_at

