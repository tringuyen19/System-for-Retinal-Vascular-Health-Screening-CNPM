from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.ai.ai_result_model import AiResultModel
from domain.models.ai_result import AiResult
from domain.models.iai_result_repository import IAiResultRepository


class AiResultRepository(IAiResultRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: AiResultModel) -> AiResult:
        return AiResult(
            result_id=model.result_id, analysis_id=model.analysis_id,
            disease_type=model.disease_type, risk_level=model.risk_level,
            confidence_score=model.confidence_score
        )
    
    def add(self, analysis_id: int, disease_type: str, risk_level: str, confidence_score: Decimal) -> AiResult:
        try:
            result_model = AiResultModel(
                analysis_id=analysis_id, disease_type=disease_type,
                risk_level=risk_level, confidence_score=confidence_score
            )
            self.session.add(result_model)
            self.session.commit()
            self.session.refresh(result_model)
            return self._to_domain(result_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating AI result: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, result_id: int) -> Optional[AiResult]:
        try:
            result_model = self.session.query(AiResultModel).filter_by(result_id=result_id).first()
            return self._to_domain(result_model) if result_model else None
        except Exception as e:
            raise ValueError(f'Error getting AI result: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_analysis_id(self, analysis_id: int) -> List[AiResult]:
        try:
            result_models = self.session.query(AiResultModel).filter_by(analysis_id=analysis_id).all()
            return [self._to_domain(model) for model in result_models]
        except Exception as e:
            raise ValueError(f'Error getting results by analysis: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_risk_level(self, risk_level: str) -> List[AiResult]:
        try:
            result_models = self.session.query(AiResultModel).filter_by(risk_level=risk_level).all()
            return [self._to_domain(model) for model in result_models]
        except Exception as e:
            raise ValueError(f'Error getting results by risk level: {str(e)}')
        finally:
            self.session.close()
    
    def get_high_risk(self) -> List[AiResult]:
        try:
            result_models = self.session.query(AiResultModel).filter(
                AiResultModel.risk_level.in_(['high', 'critical'])
            ).all()
            return [self._to_domain(model) for model in result_models]
        except Exception as e:
            raise ValueError(f'Error getting high risk results: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_disease_type(self, disease_type: str) -> List[AiResult]:
        try:
            result_models = self.session.query(AiResultModel).filter_by(disease_type=disease_type).all()
            return [self._to_domain(model) for model in result_models]
        except Exception as e:
            raise ValueError(f'Error getting results by disease type: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[AiResult]:
        try:
            result_models = self.session.query(AiResultModel).all()
            return [self._to_domain(model) for model in result_models]
        except Exception as e:
            raise ValueError(f'Error getting all results: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, result_id: int, **kwargs) -> Optional[AiResult]:
        try:
            result_model = self.session.query(AiResultModel).filter_by(result_id=result_id).first()
            if not result_model:
                return None
            for key, value in kwargs.items():
                if hasattr(result_model, key) and key != 'result_id':
                    setattr(result_model, key, value)
            self.session.commit()
            self.session.refresh(result_model)
            return self._to_domain(result_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating result: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, result_id: int) -> bool:
        try:
            result_model = self.session.query(AiResultModel).filter_by(result_id=result_id).first()
            if not result_model:
                return False
            self.session.delete(result_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting result: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_risk_level(self, risk_level: str) -> int:
        try:
            return self.session.query(AiResultModel).filter_by(risk_level=risk_level).count()
        except Exception as e:
            raise ValueError(f'Error counting results by risk level: {str(e)}')
        finally:
            self.session.close()
