"""
AI Configuration Repository - Data access layer
FR-33: Manage AI configuration persistence
"""

from typing import Optional, List
from infrastructure.models.ai_config_model import AiConfigModel


class AiConfigRepository:
    """Repository for managing AI configuration data access"""
    
    def __init__(self, session):
        self.session = session
    
    def add(self, model_version_id: int, config_data: dict) -> Optional[AiConfigModel]:
        """
        Add new AI configuration
        
        Args:
            model_version_id: AI model version ID
            config_data: Dict with configuration fields
                {
                    'confidence_threshold': float,
                    'risk_level_mapping': dict,
                    'auto_retrain_enabled': bool,
                    'retrain_threshold': float,
                    'retrain_schedule': str,
                    'max_error_rate': float,
                    'performance_metric': str
                }
        
        Returns:
            AiConfigModel: Created configuration
        """
        try:
            config = AiConfigModel(
                model_version_id=model_version_id,
                confidence_threshold=config_data.get('confidence_threshold', 0.8),
                risk_level_mapping=config_data.get('risk_level_mapping', {
                    'low': {'min': 0.0, 'max': 0.3},
                    'medium': {'min': 0.3, 'max': 0.6},
                    'high': {'min': 0.6, 'max': 0.85},
                    'critical': {'min': 0.85, 'max': 1.0}
                }),
                auto_retrain_enabled=config_data.get('auto_retrain_enabled', False),
                retrain_threshold=config_data.get('retrain_threshold', 0.85),
                retrain_schedule=config_data.get('retrain_schedule', 'monthly'),
                max_error_rate=config_data.get('max_error_rate', 0.15),
                performance_metric=config_data.get('performance_metric', 'accuracy')
            )
            self.session.add(config)
            self.session.commit()
            return config
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating AI config: {str(e)}')
    
    def get_by_id(self, config_id: int) -> Optional[AiConfigModel]:
        """Get configuration by ID"""
        return self.session.query(AiConfigModel).filter(AiConfigModel.config_id == config_id).first()
    
    def get_by_model_version(self, model_version_id: int) -> Optional[AiConfigModel]:
        """Get configuration for a specific model version"""
        return self.session.query(AiConfigModel).filter(
            AiConfigModel.model_version_id == model_version_id
        ).first()
    
    def get_all(self) -> List[AiConfigModel]:
        """Get all configurations"""
        return self.session.query(AiConfigModel).all()
    
    def update(self, config_id: int, **kwargs) -> Optional[AiConfigModel]:
        """
        Update configuration
        
        Args:
            config_id: Configuration ID
            **kwargs: Fields to update
        
        Returns:
            AiConfigModel: Updated configuration
        """
        try:
            config = self.get_by_id(config_id)
            if not config:
                return None
            
            # Update allowed fields
            allowed_fields = [
                'confidence_threshold', 'risk_level_mapping', 'auto_retrain_enabled',
                'retrain_threshold', 'retrain_schedule', 'max_error_rate', 'performance_metric'
            ]
            
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    setattr(config, key, value)
            
            self.session.commit()
            return config
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating AI config: {str(e)}')
    
    def delete(self, config_id: int) -> bool:
        """Delete configuration by ID"""
        try:
            config = self.get_by_id(config_id)
            if not config:
                return False
            
            self.session.delete(config)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting AI config: {str(e)}')
    
    def delete_by_model(self, model_version_id: int) -> bool:
        """Delete configuration for a model version"""
        try:
            config = self.get_by_model_version(model_version_id)
            if not config:
                return False
            
            return self.delete(config.config_id)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting AI config by model: {str(e)}')
    
    def count(self) -> int:
        """Count total configurations"""
        return self.session.query(AiConfigModel).count()
    
    def validate_risk_mapping(self, mapping: dict) -> bool:
        """
        Validate risk level mapping
        
        Args:
            mapping: Risk level mapping dict
                Example: {"low": {"min": 0.0, "max": 0.3}, ...}
        
        Returns:
            bool: True if valid
        """
        required_levels = ['low', 'medium', 'high', 'critical']
        
        # Check all required levels exist
        if not all(level in mapping for level in required_levels):
            return False
        
        # Check ranges are valid (0.0-1.0) and non-overlapping
        for level, range_dict in mapping.items():
            if not isinstance(range_dict, dict) or 'min' not in range_dict or 'max' not in range_dict:
                return False
            
            min_val = range_dict['min']
            max_val = range_dict['max']
            
            if not (0.0 <= min_val < max_val <= 1.0):
                return False
        
        return True
