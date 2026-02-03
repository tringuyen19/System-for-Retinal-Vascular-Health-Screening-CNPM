from datetime import datetime
from typing import Optional

class MedicalReport:
    def __init__(self, report_id: int, patient_id: int, analysis_id: int,
                 doctor_id: int, report_url: Optional[str], created_at: datetime,
                 medical_notes: Optional[str] = None, diagnosis: Optional[str] = None,
                 treatment_recommendations: Optional[str] = None):
        self.report_id = report_id
        self.patient_id = patient_id
        self.analysis_id = analysis_id
        self.doctor_id = doctor_id
        self.report_url = report_url or ''
        self.created_at = created_at
        self.medical_notes = medical_notes or ''
        self.diagnosis = diagnosis or ''
        self.treatment_recommendations = treatment_recommendations or ''

