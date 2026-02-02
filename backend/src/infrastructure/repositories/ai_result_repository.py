from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.ai.ai_result_model import AiResultModel
from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
from infrastructure.models.imaging.retinal_image_model import RetinalImageModel
from infrastructure.models.profiles.patient_profile_model import PatientProfileModel
from infrastructure.models.medical.doctor_review_model import DoctorReviewModel
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

    def get_all_by_doctor(self, doctor_id: int) -> List[AiResult]:
        """Get results for analyses that this doctor has reviewed (patient belongs to doctor)."""
        try:
            result_models = (
                self.session.query(AiResultModel)
                .join(DoctorReviewModel, AiResultModel.analysis_id == DoctorReviewModel.analysis_id)
                .filter(DoctorReviewModel.doctor_id == doctor_id)
                .distinct()
                .all()
            )
            return [self._to_domain(model) for model in result_models]
        except Exception as e:
            raise ValueError(f'Error getting results by doctor: {str(e)}')
        finally:
            self.session.close()

    def get_all_by_doctor_with_patient(self, doctor_id: int) -> List[dict]:
        """
        Get results with patient_name for doctor (for API display).
        Bao gồm toàn bộ ai_results của các patient đã từng được bác sĩ này review
        (không chỉ những analysis đã review).
        """
        try:
            # Subquery: all patient_ids that this doctor has reviewed at least once
            patient_subq = (
                self.session.query(RetinalImageModel.patient_id)
                .join(AiAnalysisModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(DoctorReviewModel, DoctorReviewModel.analysis_id == AiAnalysisModel.analysis_id)
                .filter(DoctorReviewModel.doctor_id == doctor_id)
                .distinct()
                .subquery()
            )

            # Main query: all ai_results whose image.patient_id is in that patient set
            rows = (
                self.session.query(
                    AiResultModel.result_id,
                    AiResultModel.analysis_id,
                    AiResultModel.disease_type,
                    AiResultModel.risk_level,
                    AiResultModel.confidence_score,
                    PatientProfileModel.patient_name,
                )
                .join(AiAnalysisModel, AiResultModel.analysis_id == AiAnalysisModel.analysis_id)
                .join(RetinalImageModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(PatientProfileModel, RetinalImageModel.patient_id == PatientProfileModel.patient_id)
                .filter(RetinalImageModel.patient_id.in_(select(patient_subq.c.patient_id)))
                .all()
            )
            return [
                {
                    'result_id': r.result_id,
                    'analysis_id': r.analysis_id,
                    'disease_type': r.disease_type,
                    'risk_level': r.risk_level,
                    'confidence_score': float(r.confidence_score) if r.confidence_score is not None else None,
                    'patient_name': r.patient_name or '-',
                }
                for r in rows
            ]
        except Exception as e:
            raise ValueError(f'Error getting results by doctor with patient: {str(e)}')
        finally:
            self.session.close()

    def get_all_with_patient(self) -> List[dict]:
        """Get all results with patient_name (for Admin API display)."""
        try:
            rows = (
                self.session.query(
                    AiResultModel.result_id,
                    AiResultModel.analysis_id,
                    AiResultModel.disease_type,
                    AiResultModel.risk_level,
                    AiResultModel.confidence_score,
                    PatientProfileModel.patient_name,
                )
                .join(AiAnalysisModel, AiResultModel.analysis_id == AiAnalysisModel.analysis_id)
                .join(RetinalImageModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(PatientProfileModel, RetinalImageModel.patient_id == PatientProfileModel.patient_id)
                .all()
            )
            return [
                {
                    'result_id': r.result_id,
                    'analysis_id': r.analysis_id,
                    'disease_type': r.disease_type,
                    'risk_level': r.risk_level,
                    'confidence_score': float(r.confidence_score) if r.confidence_score is not None else None,
                    'patient_name': r.patient_name or '-',
                }
                for r in rows
            ]
        except Exception as e:
            raise ValueError(f'Error getting all results with patient: {str(e)}')
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
