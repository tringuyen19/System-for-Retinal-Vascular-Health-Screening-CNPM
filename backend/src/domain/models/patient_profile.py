from datetime import date
from typing import Optional

class PatientProfile:
    def __init__(self, patient_id: int, account_id: int, patient_name: str, 
                 date_of_birth: Optional[date], gender: Optional[str], 
                 medical_history: Optional[str]):
        self.patient_id = patient_id
        self.account_id = account_id
        self.patient_name = patient_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.medical_history = medical_history

