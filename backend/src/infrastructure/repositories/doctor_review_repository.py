from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.medical.doctor_review_model import DoctorReviewModel
from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
from infrastructure.models.imaging.retinal_image_model import RetinalImageModel
from infrastructure.models.profiles.doctor_profile_model import DoctorProfileModel
from infrastructure.models.profiles.patient_profile_model import PatientProfileModel
from domain.models.doctor_review import DoctorReview
from domain.models.idoctor_review_repository import IDoctorReviewRepository


class DoctorReviewRepository(IDoctorReviewRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: DoctorReviewModel) -> DoctorReview:
        return DoctorReview(
            review_id=model.review_id, analysis_id=model.analysis_id, doctor_id=model.doctor_id,
            validation_status=model.validation_status, comment=model.comment, reviewed_at=model.reviewed_at,
            ai_accuracy_feedback=getattr(model, 'ai_accuracy_feedback', None)
        )
    
    def add(self, analysis_id: int, doctor_id: int, validation_status: str,
            comment: Optional[str], reviewed_at: datetime,
            ai_accuracy_feedback: Optional[str] = None) -> DoctorReview:
        try:
            review_model = DoctorReviewModel(
                analysis_id=analysis_id, doctor_id=doctor_id, validation_status=validation_status,
                comment=comment, reviewed_at=reviewed_at,
                ai_accuracy_feedback=ai_accuracy_feedback or None
            )
            self.session.add(review_model)
            self.session.commit()
            self.session.refresh(review_model)
            return self._to_domain(review_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating doctor review: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, review_id: int) -> Optional[DoctorReview]:
        try:
            review_model = self.session.query(DoctorReviewModel).filter_by(review_id=review_id).first()
            return self._to_domain(review_model) if review_model else None
        except Exception as e:
            raise ValueError(f'Error getting review: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_analysis_id(self, analysis_id: int) -> Optional[DoctorReview]:
        try:
            review_model = self.session.query(DoctorReviewModel).filter_by(analysis_id=analysis_id).first()
            return self._to_domain(review_model) if review_model else None
        except Exception as e:
            raise ValueError(f'Error getting review by analysis: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_doctor(self, doctor_id: int) -> List[DoctorReview]:
        try:
            review_models = self.session.query(DoctorReviewModel).filter_by(doctor_id=doctor_id).all()
            return [self._to_domain(model) for model in review_models]
        except Exception as e:
            raise ValueError(f'Error getting reviews by doctor: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_status(self, validation_status: str) -> List[DoctorReview]:
        try:
            review_models = self.session.query(DoctorReviewModel).filter_by(validation_status=validation_status).all()
            return [self._to_domain(model) for model in review_models]
        except Exception as e:
            raise ValueError(f'Error getting reviews by status: {str(e)}')
        finally:
            self.session.close()

    def get_where_status_in(self, statuses: List[str]) -> List[DoctorReview]:
        try:
            if not statuses:
                return []
            review_models = self.session.query(DoctorReviewModel).filter(
                DoctorReviewModel.validation_status.in_(statuses)
            ).all()
            return [self._to_domain(model) for model in review_models]
        except Exception as e:
            raise ValueError(f'Error getting reviews by statuses: {str(e)}')
        finally:
            self.session.close()

    def get_pending_reviews(self) -> List[DoctorReview]:
        return self.get_by_status('pending')
    
    def get_all(self) -> List[DoctorReview]:
        try:
            review_models = self.session.query(DoctorReviewModel).all()
            return [self._to_domain(model) for model in review_models]
        except Exception as e:
            raise ValueError(f'Error getting all reviews: {str(e)}')
        finally:
            self.session.close()
    
    def approve(self, review_id: int, comment: Optional[str], ai_accuracy_feedback: Optional[str] = None) -> Optional[DoctorReview]:
        try:
            review_model = self.session.query(DoctorReviewModel).filter_by(review_id=review_id).first()
            if not review_model:
                return None
            review_model.validation_status = 'approved'
            if comment is not None:
                review_model.comment = comment
            if ai_accuracy_feedback is not None and hasattr(review_model, 'ai_accuracy_feedback'):
                review_model.ai_accuracy_feedback = ai_accuracy_feedback
            self.session.commit()
            self.session.refresh(review_model)
            return self._to_domain(review_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error approving review: {str(e)}')
        finally:
            self.session.close()
    
    def reject(self, review_id: int, comment: str, ai_accuracy_feedback: Optional[str] = None) -> Optional[DoctorReview]:
        try:
            review_model = self.session.query(DoctorReviewModel).filter_by(review_id=review_id).first()
            if not review_model:
                return None
            review_model.validation_status = 'rejected'
            review_model.comment = comment
            if ai_accuracy_feedback is not None and hasattr(review_model, 'ai_accuracy_feedback'):
                review_model.ai_accuracy_feedback = ai_accuracy_feedback
            self.session.commit()
            self.session.refresh(review_model)
            return self._to_domain(review_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error rejecting review: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, review_id: int, **kwargs) -> Optional[DoctorReview]:
        try:
            review_model = self.session.query(DoctorReviewModel).filter_by(review_id=review_id).first()
            if not review_model:
                return None
            for key, value in kwargs.items():
                if hasattr(review_model, key) and key != 'review_id':
                    setattr(review_model, key, value)
            self.session.commit()
            self.session.refresh(review_model)
            return self._to_domain(review_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating review: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, review_id: int) -> bool:
        try:
            review_model = self.session.query(DoctorReviewModel).filter_by(review_id=review_id).first()
            if not review_model:
                return False
            self.session.delete(review_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting review: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_doctor(self, doctor_id: int) -> int:
        try:
            return self.session.query(DoctorReviewModel).filter_by(doctor_id=doctor_id).count()
        except Exception as e:
            raise ValueError(f'Error counting reviews by doctor: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_status(self, validation_status: str) -> int:
        try:
            return self.session.query(DoctorReviewModel).filter_by(validation_status=validation_status).count()
        except Exception as e:
            raise ValueError(f'Error counting reviews by status: {str(e)}')
        finally:
            self.session.close()

    def get_doctors_by_patient(self, patient_id: int) -> List[dict]:
        """Get distinct doctors who reviewed this patient's analyses (FR-10: patient chat with assigned doctor)."""
        try:
            rows = (
                self.session.query(DoctorProfileModel.doctor_id, DoctorProfileModel.doctor_name)
                .join(DoctorReviewModel, DoctorReviewModel.doctor_id == DoctorProfileModel.doctor_id)
                .join(AiAnalysisModel, AiAnalysisModel.analysis_id == DoctorReviewModel.analysis_id)
                .join(RetinalImageModel, RetinalImageModel.image_id == AiAnalysisModel.image_id)
                .filter(RetinalImageModel.patient_id == patient_id)
                .distinct()
                .all()
            )
            return [{"doctor_id": r.doctor_id, "doctor_name": r.doctor_name} for r in rows]
        except Exception as e:
            raise ValueError(f'Error getting doctors by patient: {str(e)}')
        finally:
            self.session.close()

    def get_patients_by_doctor(self, doctor_id: int) -> List[dict]:
        """
        Get distinct patients of this doctor via flow: DoctorReview -> AiAnalysis -> RetinalImage -> patient_id.
        Patient uploads image -> AI analyzes -> doctor reviews analysis -> these are the doctor's patients.
        """
        try:
            rows = (
                self.session.query(RetinalImageModel.patient_id, PatientProfileModel.patient_name)
                .join(AiAnalysisModel, AiAnalysisModel.image_id == RetinalImageModel.image_id)
                .join(DoctorReviewModel, DoctorReviewModel.analysis_id == AiAnalysisModel.analysis_id)
                .join(PatientProfileModel, PatientProfileModel.patient_id == RetinalImageModel.patient_id)
                .filter(DoctorReviewModel.doctor_id == doctor_id)
                .group_by(RetinalImageModel.patient_id, PatientProfileModel.patient_name)
                .all()
            )
            return [{"patient_id": r.patient_id, "patient_name": r.patient_name or ""} for r in rows]
        except Exception as e:
            raise ValueError(f'Error getting patients by doctor: {str(e)}')
        finally:
            self.session.close()
