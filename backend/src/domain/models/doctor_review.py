from datetime import datetime
from typing import Optional

class DoctorReview:
    def __init__(self, review_id: int, analysis_id: int, doctor_id: int,
                 validation_status: str, comment: Optional[str], reviewed_at: datetime,
                 ai_accuracy_feedback: Optional[str] = None):
        self.review_id = review_id
        self.analysis_id = analysis_id
        self.doctor_id = doctor_id
        self.validation_status = validation_status
        self.comment = comment
        self.reviewed_at = reviewed_at
        self.ai_accuracy_feedback = ai_accuracy_feedback or None  # FR-19: correct / incorrect / partially_correct

