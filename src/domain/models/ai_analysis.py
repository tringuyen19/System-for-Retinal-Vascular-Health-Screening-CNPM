from datetime import datetime
from typing import Optional

class AiAnalysis:
    def __init__(self, analysis_id: int, image_id: int, ai_model_version_id: int, 
                 analysis_time: datetime, processing_time: Optional[int], status: str):
        self.analysis_id = analysis_id
        self.image_id = image_id
        self.ai_model_version_id = ai_model_version_id
        self.analysis_time = analysis_time
        self.processing_time = processing_time
        self.status = status

