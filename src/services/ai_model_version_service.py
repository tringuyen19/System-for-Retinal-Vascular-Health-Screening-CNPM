"""
AI Model Version Service - Business Logic Layer
Handles AI model version management
"""

from typing import List, Optional
from datetime import datetime
from domain.models.ai_model_version import AiModelVersion
from domain.models.iai_model_version_repository import IAiModelVersionRepository


class AiModelVersionService:
    def __init__(self, repository: IAiModelVersionRepository):
        self.repository = repository
    
    def create_model_version(self, model_name: str, version: str, 
                            threshold_config: str, active_flag: bool = False) -> Optional[AiModelVersion]:
        """Create AI model version"""
        return self.repository.add(
            model_name=model_name,
            version=version,
            threshold_config=threshold_config,
            trained_at=datetime.now(),
            active_flag=active_flag
        )
    
    def get_model_by_id(self, ai_model_version_id: int) -> Optional[AiModelVersion]:
        """Get model by ID"""
        return self.repository.get_by_id(ai_model_version_id)
    
    def get_active_model(self) -> Optional[AiModelVersion]:
        """Get currently active model"""
        return self.repository.get_active_model()
    
    def get_model_by_version(self, version: str) -> Optional[AiModelVersion]:
        """Get model by version"""
        return self.repository.get_by_version(version)
    
    def list_all_models(self) -> List[AiModelVersion]:
        """Get all model versions"""
        return self.repository.get_all()
    
    def set_active_model(self, ai_model_version_id: int) -> Optional[AiModelVersion]:
        """Set model as active (deactivates other models)"""
        return self.repository.set_active(ai_model_version_id)
    
    def update_model(self, ai_model_version_id: int, **kwargs) -> Optional[AiModelVersion]:
        """Update model version"""
        return self.repository.update(ai_model_version_id, **kwargs)
    
    def delete_model(self, ai_model_version_id: int) -> bool:
        """Delete model version"""
        model = self.repository.get_by_id(ai_model_version_id)
        if model and model.active_flag:
            raise ValueError("Cannot delete active model. Set another model as active first.")
        return self.repository.delete(ai_model_version_id)
    
    def count_models(self) -> int:
        """Count total model versions"""
        return self.repository.count()
