from typing import List, Optional, Dict, Any
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

    def get_risk_distribution_analytics(self, days: Optional[int] = 30) -> Dict[str, Any]:
        """
        FR-36: Risk distribution analytics over a period.
        Logic: for each analysis, pick the worst risk among its results, then count distribution.
        - days: None or 0 => all time
        """
        try:
            from datetime import datetime, timedelta

            risk_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

            end_dt = datetime.now()
            start_dt = None
            if days not in (None, 0):
                start_dt = end_dt - timedelta(days=int(days))

            q = (
                self.session.query(
                    AiResultModel.analysis_id,
                    AiResultModel.risk_level,
                    AiResultModel.confidence_score,
                )
                .join(AiAnalysisModel, AiResultModel.analysis_id == AiAnalysisModel.analysis_id)
                .filter(AiAnalysisModel.status == 'completed')
            )
            if start_dt is not None:
                q = q.filter(AiAnalysisModel.analysis_time >= start_dt).filter(AiAnalysisModel.analysis_time <= end_dt)

            rows = q.all()

            # Per analysis aggregation
            worst_by_analysis: Dict[int, str] = {}
            confidence_scores: List[float] = []

            for analysis_id, risk_level, confidence_score in rows:
                rl = (risk_level or 'unknown').strip().lower()
                if rl not in risk_order:
                    rl = 'unknown'

                if analysis_id is not None:
                    prev = worst_by_analysis.get(int(analysis_id))
                    if prev is None:
                        worst_by_analysis[int(analysis_id)] = rl
                    else:
                        if risk_order.get(rl, 0) > risk_order.get(prev, 0):
                            worst_by_analysis[int(analysis_id)] = rl

                if confidence_score is not None:
                    try:
                        confidence_scores.append(float(confidence_score))
                    except Exception:
                        pass

            dist: Dict[str, int] = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0, 'unknown': 0}
            for rl in worst_by_analysis.values():
                dist[rl] = dist.get(rl, 0) + 1

            total_analyses = len(worst_by_analysis)
            percentages = {
                k: round((v / total_analyses * 100.0), 2) if total_analyses > 0 else 0.0
                for k, v in dist.items()
            }

            avg_conf = (sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0.0
            min_conf = min(confidence_scores) if confidence_scores else 0.0
            max_conf = max(confidence_scores) if confidence_scores else 0.0

            period_label = 'Tất cả thời gian' if days in (None, 0) else f'Trong {int(days)} ngày gần đây'
            return {
                'period_days': None if days in (None, 0) else int(days),
                'period_label': period_label,
                'risk_distribution': dist,
                'risk_percentages': percentages,
                'total_analyses': total_analyses,
                'average_confidence': round(avg_conf, 2),
                'min_confidence': round(min_conf, 2),
                'max_confidence': round(max_conf, 2),
                'has_data': total_analyses > 0
            }
        except Exception as e:
            raise ValueError(f'Error getting risk distribution analytics: {str(e)}')
        finally:
            self.session.close()
