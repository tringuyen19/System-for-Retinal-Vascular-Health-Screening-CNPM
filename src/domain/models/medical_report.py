from datetime import datetime

class MedicalReport:
    def __init__(self, report_id: int, patient_id: int, analysis_id: int, 
                 doctor_id: int, report_url: str, created_at: datetime):
        self.report_id = report_id
        self.patient_id = patient_id
        self.analysis_id = analysis_id
        self.doctor_id = doctor_id
        self.report_url = report_url
        self.created_at = created_at

