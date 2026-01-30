from datetime import datetime

class RetinalImage:
    def __init__(self, image_id: int, patient_id: int, clinic_id: int, 
                 uploaded_by: int, image_type: str, eye_side: str, 
                 image_url: str, upload_time: datetime, status: str):
        self.image_id = image_id
        self.patient_id = patient_id
        self.clinic_id = clinic_id
        self.uploaded_by = uploaded_by
        self.image_type = image_type
        self.eye_side = eye_side
        self.image_url = image_url
        self.upload_time = upload_time
        self.status = status

