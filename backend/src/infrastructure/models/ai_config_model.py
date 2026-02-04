"""
AI Configuration Model - SQLAlchemy ORM
FR-33: Store AI model configuration, thresholds, and retraining policies
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from datetime import datetime
from infrastructure.databases.base import Base


class AiConfigModel(Base):
    """
    AI Configuration Model - Stores threshold and retraining policies for AI models
    
    Fields:
    - config_id: Primary key
    - model_version_id: Foreign key to ai_model_versions
    - confidence_threshold: Min confidence score required for results (0.0-1.0)
    - risk_level_mapping: JSON mapping confidence ranges to risk levels
      Example: {"low": {"min": 0.0, "max": 0.3}, "medium": {"min": 0.3, "max": 0.6}, ...}
    - auto_retrain_enabled: Whether automatic retraining is enabled
    - retrain_threshold: Performance drop threshold triggering retrain (0.0-1.0)
    - retrain_schedule: Retraining schedule ('weekly', 'monthly', 'quarterly')
    - max_error_rate: Max error rate before triggering retrain (0.0-1.0)
    - performance_metric: Which metric to track ('accuracy', 'f1_score', 'auc')
    - created_at: When config was created
    - updated_at: Last update timestamp
    """
    
    __tablename__ = 'ai_configs'
    __table_args__ = {'extend_existing': True}
    
    config_id = Column(Integer, primary_key=True, autoincrement=True)
    model_version_id = Column(Integer, ForeignKey('ai_model_versions.ai_model_version_id'), nullable=False)
    
    # Threshold configuration
    confidence_threshold = Column(Float, nullable=False, default=0.8)  # 0.0-1.0
    risk_level_mapping = Column(JSON, nullable=False, default={
        'low': {'min': 0.0, 'max': 0.3},
        'medium': {'min': 0.3, 'max': 0.6},
        'high': {'min': 0.6, 'max': 0.85},
        'critical': {'min': 0.85, 'max': 1.0}
    })
    
    # Auto-retraining policy
    auto_retrain_enabled = Column(Boolean, nullable=False, default=False)
    retrain_threshold = Column(Float, nullable=False, default=0.85)  # Performance threshold
    retrain_schedule = Column(String(20), nullable=False, default='monthly')  # weekly, monthly, quarterly
    max_error_rate = Column(Float, nullable=False, default=0.15)  # 15% error triggers retrain
    performance_metric = Column(String(50), nullable=False, default='accuracy')  # accuracy, f1_score, auc
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<AiConfigModel(config_id={self.config_id}, model_version_id={self.model_version_id}, confidence_threshold={self.confidence_threshold})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'config_id': self.config_id,
            'model_version_id': self.model_version_id,
            'confidence_threshold': self.confidence_threshold,
            'risk_level_mapping': self.risk_level_mapping,
            'auto_retrain_enabled': self.auto_retrain_enabled,
            'retrain_threshold': self.retrain_threshold,
            'retrain_schedule': self.retrain_schedule,
            'max_error_rate': self.max_error_rate,
            'performance_metric': self.performance_metric,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
