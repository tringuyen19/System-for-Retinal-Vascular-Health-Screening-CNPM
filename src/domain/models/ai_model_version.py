from datetime import datetime

class AiModelVersion:
    def __init__(self, ai_model_version_id: int, model_name: str, version: str, 
                 threshold_config: str, trained_at: datetime, active_flag: bool):
        self.ai_model_version_id = ai_model_version_id
        self.model_name = model_name
        self.version = version
        self.threshold_config = threshold_config
        self.trained_at = trained_at
        self.active_flag = active_flag

