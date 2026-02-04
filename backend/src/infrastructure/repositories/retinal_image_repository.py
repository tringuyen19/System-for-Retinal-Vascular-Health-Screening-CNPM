from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from infrastructure.databases.mssql import session
from infrastructure.models.imaging.retinal_image_model import RetinalImageModel
from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
from domain.models.retinal_image import RetinalImage
from domain.models.iretinal_image_repository import IRetinalImageRepository


class RetinalImageRepository(IRetinalImageRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: RetinalImageModel) -> RetinalImage:
        return RetinalImage(
            image_id=model.image_id, patient_id=model.patient_id, clinic_id=model.clinic_id,
            uploaded_by=model.uploaded_by, image_type=model.image_type, eye_side=model.eye_side,
            image_url=model.image_url, upload_time=model.upload_time, status=model.status
        )
    
    def add(self, patient_id: int, clinic_id: int, uploaded_by: int, image_type: str,
            eye_side: str, image_url: str, upload_time: datetime, status: str) -> RetinalImage:
        try:
            image_model = RetinalImageModel(
                patient_id=patient_id, clinic_id=clinic_id, uploaded_by=uploaded_by,
                image_type=image_type, eye_side=eye_side, image_url=image_url,
                upload_time=upload_time, status=status
            )
            self.session.add(image_model)
            self.session.commit()
            self.session.refresh(image_model)
            return self._to_domain(image_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating retinal image: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, image_id: int) -> Optional[RetinalImage]:
        try:
            image_model = self.session.query(RetinalImageModel).filter_by(image_id=image_id).first()
            return self._to_domain(image_model) if image_model else None
        except Exception as e:
            raise ValueError(f'Error getting retinal image: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_patient(self, patient_id: int) -> List[RetinalImage]:
        try:
            image_models = self.session.query(RetinalImageModel).filter_by(patient_id=patient_id).all()
            return [self._to_domain(model) for model in image_models]
        except Exception as e:
            raise ValueError(f'Error getting images by patient: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_clinic(self, clinic_id: int) -> List[RetinalImage]:
        try:
            image_models = self.session.query(RetinalImageModel).filter_by(clinic_id=clinic_id).all()
            return [self._to_domain(model) for model in image_models]
        except Exception as e:
            raise ValueError(f'Error getting images by clinic: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[RetinalImage]:
        try:
            image_models = self.session.query(RetinalImageModel).all()
            return [self._to_domain(model) for model in image_models]
        except Exception as e:
            raise ValueError(f'Error getting all images: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_status(self, status: str) -> List[RetinalImage]:
        try:
            image_models = self.session.query(RetinalImageModel).filter_by(status=status).all()
            return [self._to_domain(model) for model in image_models]
        except Exception as e:
            raise ValueError(f'Error getting images by status: {str(e)}')
        finally:
            self.session.close()
    
    def get_pending_analysis(self) -> List[RetinalImage]:
        """
        Get images that don't have AI analysis yet (pending analysis)
        Uses LEFT JOIN to find images without corresponding analysis records
        """
        try:
            # Query images that don't have an AI analysis record
            # Using LEFT JOIN and filtering where analysis is NULL
            image_models = self.session.query(RetinalImageModel).outerjoin(
                AiAnalysisModel, RetinalImageModel.image_id == AiAnalysisModel.image_id
            ).filter(AiAnalysisModel.image_id.is_(None)).all()
            
            return [self._to_domain(model) for model in image_models]
        except Exception as e:
            raise ValueError(f'Error getting pending analysis images: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_processing(self, image_id: int) -> Optional[RetinalImage]:
        try:
            image_model = self.session.query(RetinalImageModel).filter_by(image_id=image_id).first()
            if not image_model:
                return None
            image_model.status = 'processing'
            self.session.commit()
            self.session.refresh(image_model)
            return self._to_domain(image_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as processing: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_analyzed(self, image_id: int) -> Optional[RetinalImage]:
        try:
            image_model = self.session.query(RetinalImageModel).filter_by(image_id=image_id).first()
            if not image_model:
                return None
            image_model.status = 'analyzed'
            self.session.commit()
            self.session.refresh(image_model)
            return self._to_domain(image_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as analyzed: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_error(self, image_id: int) -> Optional[RetinalImage]:
        try:
            image_model = self.session.query(RetinalImageModel).filter_by(image_id=image_id).first()
            if not image_model:
                return None
            image_model.status = 'error'
            self.session.commit()
            self.session.refresh(image_model)
            return self._to_domain(image_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as error: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, image_id: int, **kwargs) -> Optional[RetinalImage]:
        try:
            image_model = self.session.query(RetinalImageModel).filter_by(image_id=image_id).first()
            if not image_model:
                return None
            for key, value in kwargs.items():
                if hasattr(image_model, key) and key not in ['image_id', 'upload_time']:
                    setattr(image_model, key, value)
            self.session.commit()
            self.session.refresh(image_model)
            return self._to_domain(image_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating image: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, image_id: int) -> bool:
        try:
            image_model = self.session.query(RetinalImageModel).filter_by(image_id=image_id).first()
            if not image_model:
                return False
            self.session.delete(image_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting image: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_status(self, status: str) -> int:
        try:
            return self.session.query(RetinalImageModel).filter_by(status=status).count()
        except Exception as e:
            raise ValueError(f'Error counting images by status: {str(e)}')
        finally:
            self.session.close()

    def get_image_analytics(self, days: Optional[int] = 30) -> Dict[str, Any]:
        """
        FR-36: Image analytics over a period.
        - days: None or 0 => all time
        Returns:
          {
            period_days, period_label, total_images,
            type_distribution, status_distribution,
            daily_upload_trend: [{date, count}]
          }
        """
        try:
            from datetime import timedelta

            end_dt = datetime.now()
            start_dt = None
            if days not in (None, 0):
                start_dt = end_dt - timedelta(days=int(days))

            q = self.session.query(
                RetinalImageModel.upload_time,
                RetinalImageModel.image_type,
                RetinalImageModel.status,
            )
            if start_dt is not None:
                q = q.filter(RetinalImageModel.upload_time >= start_dt).filter(RetinalImageModel.upload_time <= end_dt)

            rows = q.all()

            type_distribution: Dict[str, int] = {}
            status_distribution: Dict[str, int] = {}
            daily: Dict[str, int] = {}

            for upload_time, image_type, status in rows:
                it = (image_type or 'unknown').strip().lower()
                st = (status or 'unknown').strip().lower()
                type_distribution[it] = type_distribution.get(it, 0) + 1
                status_distribution[st] = status_distribution.get(st, 0) + 1

                if upload_time:
                    dk = upload_time.date().isoformat()
                    daily[dk] = daily.get(dk, 0) + 1

            daily_upload_trend = [{'date': d, 'count': daily[d]} for d in sorted(daily.keys())]

            period_label = 'Tất cả thời gian' if days in (None, 0) else f'Trong {int(days)} ngày gần đây'
            return {
                'period_days': None if days in (None, 0) else int(days),
                'period_label': period_label,
                'total_images': len(rows),
                'type_distribution': type_distribution,
                'status_distribution': status_distribution,
                'daily_upload_trend': daily_upload_trend,
                'has_data': len(rows) > 0
            }
        except Exception as e:
            raise ValueError(f'Error getting image analytics: {str(e)}')
        finally:
            self.session.close()
