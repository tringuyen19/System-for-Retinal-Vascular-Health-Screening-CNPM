from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.ai.ai_model_version_model import AiModelVersionModel
from domain.models.ai_model_version import AiModelVersion
from domain.models.iai_model_version_repository import IAiModelVersionRepository


class AiModelVersionRepository(IAiModelVersionRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: AiModelVersionModel) -> AiModelVersion:
        return AiModelVersion(
            ai_model_version_id=model.ai_model_version_id, model_name=model.model_name,
            version=model.version, threshold_config=model.threshold_config,
            trained_at=model.trained_at, active_flag=model.active_flag
        )
    
    def add(self, model_name: str, version: str, threshold_config: str,
            trained_at: datetime, active_flag: bool) -> AiModelVersion:
        try:
            model_ver = AiModelVersionModel(
                model_name=model_name, version=version, threshold_config=threshold_config,
                trained_at=trained_at, active_flag=active_flag
            )
            self.session.add(model_ver)
            self.session.commit()
            self.session.refresh(model_ver)
            return self._to_domain(model_ver)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating AI model version: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, ai_model_version_id: int) -> Optional[AiModelVersion]:
        try:
            model_ver = self.session.query(AiModelVersionModel).filter_by(ai_model_version_id=ai_model_version_id).first()
            return self._to_domain(model_ver) if model_ver else None
        except Exception as e:
            raise ValueError(f'Error getting model version: {str(e)}')
        finally:
            self.session.close()
    
    def get_active_model(self) -> Optional[AiModelVersion]:
        try:
            model_ver = self.session.query(AiModelVersionModel).filter_by(active_flag=True).first()
            return self._to_domain(model_ver) if model_ver else None
        except Exception as e:
            raise ValueError(f'Error getting active model: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_version(self, version: str) -> Optional[AiModelVersion]:
        try:
            model_ver = self.session.query(AiModelVersionModel).filter_by(version=version).first()
            return self._to_domain(model_ver) if model_ver else None
        except Exception as e:
            raise ValueError(f'Error getting model by version: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[AiModelVersion]:
        try:
            model_vers = self.session.query(AiModelVersionModel).all()
            return [self._to_domain(model) for model in model_vers]
        except Exception as e:
            raise ValueError(f'Error getting all model versions: {str(e)}')
        finally:
            self.session.close()
    
    def set_active(self, ai_model_version_id: int) -> Optional[AiModelVersion]:
        try:
            # Deactivate all models
            self.session.query(AiModelVersionModel).update({AiModelVersionModel.active_flag: False})
            # Activate target model
            model_ver = self.session.query(AiModelVersionModel).filter_by(ai_model_version_id=ai_model_version_id).first()
            if not model_ver:
                return None
            model_ver.active_flag = True
            self.session.commit()
            self.session.refresh(model_ver)
            return self._to_domain(model_ver)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error setting active model: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, ai_model_version_id: int, **kwargs) -> Optional[AiModelVersion]:
        try:
            model_ver = self.session.query(AiModelVersionModel).filter_by(ai_model_version_id=ai_model_version_id).first()
            if not model_ver:
                return None
            for key, value in kwargs.items():
                if hasattr(model_ver, key) and key not in ['ai_model_version_id', 'trained_at']:
                    setattr(model_ver, key, value)
            self.session.commit()
            self.session.refresh(model_ver)
            return self._to_domain(model_ver)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating model version: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, ai_model_version_id: int) -> bool:
        try:
            model_ver = self.session.query(AiModelVersionModel).filter_by(ai_model_version_id=ai_model_version_id).first()
            if not model_ver:
                return False
            self.session.delete(model_ver)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting model version: {str(e)}')
        finally:
            self.session.close()
    
    def count(self) -> int:
        try:
            return self.session.query(AiModelVersionModel).count()
        except Exception as e:
            raise ValueError(f'Error counting model versions: {str(e)}')
        finally:
            self.session.close()
