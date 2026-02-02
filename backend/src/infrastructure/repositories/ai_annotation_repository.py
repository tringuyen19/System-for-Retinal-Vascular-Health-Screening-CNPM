from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.ai.ai_annotation_model import AiAnnotationModel
from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
from infrastructure.models.imaging.retinal_image_model import RetinalImageModel
from infrastructure.models.profiles.patient_profile_model import PatientProfileModel
from infrastructure.models.medical.doctor_review_model import DoctorReviewModel
from domain.models.ai_annotation import AiAnnotation
from domain.models.iai_annotation_repository import IAiAnnotationRepository


class AiAnnotationRepository(IAiAnnotationRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: AiAnnotationModel) -> AiAnnotation:
        return AiAnnotation(
            annotation_id=model.annotation_id, analysis_id=model.analysis_id,
            heatmap_url=model.heatmap_url, description=model.description
        )
    
    def add(self, analysis_id: int, heatmap_url: str, description: Optional[str]) -> AiAnnotation:
        try:
            annotation_model = AiAnnotationModel(
                analysis_id=analysis_id, heatmap_url=heatmap_url, description=description
            )
            self.session.add(annotation_model)
            self.session.commit()
            self.session.refresh(annotation_model)
            return self._to_domain(annotation_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating AI annotation: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, annotation_id: int) -> Optional[AiAnnotation]:
        try:
            annotation_model = self.session.query(AiAnnotationModel).filter_by(annotation_id=annotation_id).first()
            return self._to_domain(annotation_model) if annotation_model else None
        except Exception as e:
            raise ValueError(f'Error getting AI annotation: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_analysis_id(self, analysis_id: int) -> Optional[AiAnnotation]:
        try:
            annotation_model = self.session.query(AiAnnotationModel).filter_by(analysis_id=analysis_id).first()
            return self._to_domain(annotation_model) if annotation_model else None
        except Exception as e:
            raise ValueError(f'Error getting annotation by analysis: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[AiAnnotation]:
        try:
            annotation_models = self.session.query(AiAnnotationModel).all()
            return [self._to_domain(model) for model in annotation_models]
        except Exception as e:
            raise ValueError(f'Error getting all annotations: {str(e)}')
        finally:
            self.session.close()

    def get_all_by_doctor(self, doctor_id: int) -> List[AiAnnotation]:
        """Get annotations for analyses that this doctor has reviewed (patient belongs to doctor)."""
        try:
            annotation_models = (
                self.session.query(AiAnnotationModel)
                .join(DoctorReviewModel, AiAnnotationModel.analysis_id == DoctorReviewModel.analysis_id)
                .filter(DoctorReviewModel.doctor_id == doctor_id)
                .distinct()
                .all()
            )
            return [self._to_domain(model) for model in annotation_models]
        except Exception as e:
            raise ValueError(f'Error getting annotations by doctor: {str(e)}')
        finally:
            self.session.close()

    def get_all_by_doctor_with_patient(self, doctor_id: int) -> List[dict]:
        """
        Get annotations with patient_name for doctor (for API display).
        Bao gồm toàn bộ ai_annotations của các patient đã từng được bác sĩ này review
        (không chỉ những analysis đã review).
        """
        try:
            # Subquery: tất cả patient_id mà doctor này đã từng review
            patient_subq = (
                self.session.query(RetinalImageModel.patient_id)
                .join(AiAnalysisModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(DoctorReviewModel, DoctorReviewModel.analysis_id == AiAnalysisModel.analysis_id)
                .filter(DoctorReviewModel.doctor_id == doctor_id)
                .distinct()
                .subquery()
            )

            # Main query: mọi annotation của các patient đó
            rows = (
                self.session.query(
                    AiAnnotationModel.annotation_id,
                    AiAnnotationModel.analysis_id,
                    AiAnnotationModel.heatmap_url,
                    AiAnnotationModel.description,
                    PatientProfileModel.patient_name,
                )
                .join(AiAnalysisModel, AiAnnotationModel.analysis_id == AiAnalysisModel.analysis_id)
                .join(RetinalImageModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(PatientProfileModel, RetinalImageModel.patient_id == PatientProfileModel.patient_id)
                .filter(RetinalImageModel.patient_id.in_(select(patient_subq.c.patient_id)))
                .all()
            )
            return [
                {
                    'annotation_id': r.annotation_id,
                    'analysis_id': r.analysis_id,
                    'heatmap_url': r.heatmap_url,
                    'description': r.description,
                    'patient_name': r.patient_name or '-',
                }
                for r in rows
            ]
        except Exception as e:
            raise ValueError(f'Error getting annotations by doctor with patient: {str(e)}')
        finally:
            self.session.close()

    def get_all_with_patient(self) -> List[dict]:
        """Get all annotations with patient_name (for Admin API display)."""
        try:
            rows = (
                self.session.query(
                    AiAnnotationModel.annotation_id,
                    AiAnnotationModel.analysis_id,
                    AiAnnotationModel.heatmap_url,
                    AiAnnotationModel.description,
                    PatientProfileModel.patient_name,
                )
                .join(AiAnalysisModel, AiAnnotationModel.analysis_id == AiAnalysisModel.analysis_id)
                .join(RetinalImageModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(PatientProfileModel, RetinalImageModel.patient_id == PatientProfileModel.patient_id)
                .all()
            )
            return [
                {
                    'annotation_id': r.annotation_id,
                    'analysis_id': r.analysis_id,
                    'heatmap_url': r.heatmap_url,
                    'description': r.description,
                    'patient_name': r.patient_name or '-',
                }
                for r in rows
            ]
        except Exception as e:
            raise ValueError(f'Error getting all annotations with patient: {str(e)}')
        finally:
            self.session.close()
    
    def get_all_with_descriptions(self) -> List[AiAnnotation]:
        try:
            annotation_models = self.session.query(AiAnnotationModel).filter(
                AiAnnotationModel.description.isnot(None)
            ).all()
            return [self._to_domain(model) for model in annotation_models]
        except Exception as e:
            raise ValueError(f'Error getting annotations with descriptions: {str(e)}')
        finally:
            self.session.close()
    
    def update_heatmap(self, annotation_id: int, heatmap_url: str) -> Optional[AiAnnotation]:
        try:
            annotation_model = self.session.query(AiAnnotationModel).filter_by(annotation_id=annotation_id).first()
            if not annotation_model:
                return None
            annotation_model.heatmap_url = heatmap_url
            self.session.commit()
            self.session.refresh(annotation_model)
            return self._to_domain(annotation_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating heatmap: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, annotation_id: int, **kwargs) -> Optional[AiAnnotation]:
        try:
            annotation_model = self.session.query(AiAnnotationModel).filter_by(annotation_id=annotation_id).first()
            if not annotation_model:
                return None
            for key, value in kwargs.items():
                if hasattr(annotation_model, key) and key not in ['annotation_id', 'analysis_id']:
                    setattr(annotation_model, key, value)
            self.session.commit()
            self.session.refresh(annotation_model)
            return self._to_domain(annotation_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating annotation: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, annotation_id: int) -> bool:
        try:
            annotation_model = self.session.query(AiAnnotationModel).filter_by(annotation_id=annotation_id).first()
            if not annotation_model:
                return False
            self.session.delete(annotation_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting annotation: {str(e)}')
        finally:
            self.session.close()
    
    def count(self) -> int:
        try:
            return self.session.query(AiAnnotationModel).count()
        except Exception as e:
            raise ValueError(f'Error counting annotations: {str(e)}')
        finally:
            self.session.close()
