from datetime import datetime

class Conversation:
    def __init__(self, conversation_id: int, patient_id: int, doctor_id: int, 
                 created_at: datetime, status: str):
        self.conversation_id = conversation_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.created_at = created_at
        self.status = status

