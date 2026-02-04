from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func
from infrastructure.databases.mssql import session
from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
from infrastructure.models.medical.doctor_review_model import DoctorReviewModel
from domain.models.ai_analysis import AiAnalysis
from domain.models.iai_analysis_repository import IAiAnalysisRepository


class AiAnalysisRepository(IAiAnalysisRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: AiAnalysisModel) -> AiAnalysis:
        return AiAnalysis(
            analysis_id=model.analysis_id, image_id=model.image_id,
            ai_model_version_id=model.ai_model_version_id, analysis_time=model.analysis_time,
            processing_time=model.processing_time, status=model.status
        )
    
    def add(self, image_id: int, ai_model_version_id: int, analysis_time: datetime, status: str, processing_time: Optional[int] = None) -> AiAnalysis:
        try:
            analysis_model = AiAnalysisModel(
                image_id=image_id, ai_model_version_id=ai_model_version_id,
                analysis_time=analysis_time, status=status, processing_time=processing_time
            )
            self.session.add(analysis_model)
            self.session.commit()
            self.session.refresh(analysis_model)
            return self._to_domain(analysis_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating AI analysis: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, analysis_id: int) -> Optional[AiAnalysis]:
        try:
            analysis_model = self.session.query(AiAnalysisModel).filter_by(analysis_id=analysis_id).first()
            return self._to_domain(analysis_model) if analysis_model else None
        except Exception as e:
            raise ValueError(f'Error getting AI analysis: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_image_id(self, image_id: int) -> Optional[AiAnalysis]:
        try:
            analysis_model = self.session.query(AiAnalysisModel).filter_by(image_id=image_id).first()
            return self._to_domain(analysis_model) if analysis_model else None
        except Exception as e:
            raise ValueError(f'Error getting analysis by image: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[AiAnalysis]:
        try:
            analysis_models = self.session.query(AiAnalysisModel).all()
            return [self._to_domain(model) for model in analysis_models]
        except Exception as e:
            raise ValueError(f'Error getting all analyses: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_status(self, status: str) -> List[AiAnalysis]:
        try:
            analysis_models = self.session.query(AiAnalysisModel).filter_by(status=status).all()
            return [self._to_domain(model) for model in analysis_models]
        except Exception as e:
            raise ValueError(f'Error getting analyses by status: {str(e)}')
        finally:
            self.session.close()
    
    def get_pending(self) -> List[AiAnalysis]:
        return self.get_by_status('pending')
    
    def get_processing(self) -> List[AiAnalysis]:
        return self.get_by_status('processing')
    
    def get_completed(self) -> List[AiAnalysis]:
        return self.get_by_status('completed')
    
    def mark_as_processing(self, analysis_id: int) -> Optional[AiAnalysis]:
        try:
            analysis_model = self.session.query(AiAnalysisModel).filter_by(analysis_id=analysis_id).first()
            if not analysis_model:
                return None
            analysis_model.status = 'processing'
            self.session.commit()
            self.session.refresh(analysis_model)
            return self._to_domain(analysis_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as processing: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_completed(self, analysis_id: int, processing_time: int) -> Optional[AiAnalysis]:
        try:
            analysis_model = self.session.query(AiAnalysisModel).filter_by(analysis_id=analysis_id).first()
            if not analysis_model:
                return None
            analysis_model.status = 'completed'
            analysis_model.processing_time = processing_time
            self.session.commit()
            self.session.refresh(analysis_model)
            return self._to_domain(analysis_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as completed: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_failed(self, analysis_id: int) -> Optional[AiAnalysis]:
        try:
            analysis_model = self.session.query(AiAnalysisModel).filter_by(analysis_id=analysis_id).first()
            if not analysis_model:
                return None
            analysis_model.status = 'failed'
            self.session.commit()
            self.session.refresh(analysis_model)
            return self._to_domain(analysis_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as failed: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, analysis_id: int) -> bool:
        try:
            analysis_model = self.session.query(AiAnalysisModel).filter_by(analysis_id=analysis_id).first()
            if not analysis_model:
                return False
            self.session.delete(analysis_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting analysis: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_status(self, status: str) -> int:
        try:
            return self.session.query(AiAnalysisModel).filter_by(status=status).count()
        except Exception as e:
            raise ValueError(f'Error counting analyses by status: {str(e)}')
        finally:
            self.session.close()
    
    def get_average_processing_time(self) -> float:
        try:
            avg_time = self.session.query(func.avg(AiAnalysisModel.processing_time)).filter(
                AiAnalysisModel.processing_time.isnot(None)
            ).scalar()
            return float(avg_time) if avg_time else 0.0
        except Exception as e:
            raise ValueError(f'Error calculating average processing time: {str(e)}')
        finally:
            self.session.close()
    
    def get_completed_without_review(self) -> List[AiAnalysis]:
        """
        Get completed analyses that do NOT have any doctor review yet.
        This is used for FR-15 pending review list (bác sĩ cần duyệt kết quả AI).
        """
        try:
            # LEFT JOIN ai_analysis with doctor_reviews and keep rows where there is no review
            query = (
                self.session.query(AiAnalysisModel)
                .outerjoin(DoctorReviewModel, AiAnalysisModel.analysis_id == DoctorReviewModel.analysis_id)
                .filter(AiAnalysisModel.status == 'completed')
                .filter(DoctorReviewModel.analysis_id.is_(None))
            )
            analysis_models = query.all()
            return [self._to_domain(model) for model in analysis_models]
        except Exception as e:
            raise ValueError(f'Error getting completed analyses without review: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_patient_id(self, patient_id: int, limit: int = 50, offset: int = 0,
                          start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[AiAnalysis]:
        """
        Get analyses for a patient with pagination and date filtering (optimized with JOIN)
        """
        try:
            from infrastructure.models.imaging.retinal_image_model import RetinalImageModel
            from datetime import datetime as dt
            
            # JOIN with retinal_images to filter by patient_id
            query = self.session.query(AiAnalysisModel).join(
                RetinalImageModel, AiAnalysisModel.image_id == RetinalImageModel.image_id
            ).filter(RetinalImageModel.patient_id == patient_id)
            
            # Apply date filters
            if start_date:
                query = query.filter(AiAnalysisModel.analysis_time >= dt.combine(start_date, dt.min.time()))
            if end_date:
                query = query.filter(AiAnalysisModel.analysis_time <= dt.combine(end_date, dt.max.time()))
            
            # Order by date (newest first) and apply pagination
            query = query.order_by(AiAnalysisModel.analysis_time.desc())
            query = query.offset(offset).limit(limit)
            
            analysis_models = query.all()
            return [self._to_domain(model) for model in analysis_models]
        except Exception as e:
            raise ValueError(f'Error getting analyses by patient: {str(e)}')
        finally:
            self.session.close()

    def get_error_rate_analytics(self, days: Optional[int] = 30) -> Dict[str, Any]:
        """
        FR-36: Error rate analytics over a period.
        - days: None or 0 => all time
        Returns:
          {
            period_days, period_label,
            total_analyses, failed_analyses, error_rate,
            status_breakdown,
            daily_failure_trend: [{date, total, failed, error_rate}]
          }
        """
        try:
            from datetime import timedelta

            end_dt = datetime.now()
            start_dt = None
            if days not in (None, 0):
                start_dt = end_dt - timedelta(days=int(days))

            q = self.session.query(AiAnalysisModel.analysis_time, AiAnalysisModel.status)
            if start_dt is not None:
                q = q.filter(AiAnalysisModel.analysis_time >= start_dt).filter(AiAnalysisModel.analysis_time <= end_dt)

            rows = q.all()

            status_breakdown: Dict[str, int] = {}
            daily_total: Dict[str, int] = {}
            daily_failed: Dict[str, int] = {}

            for analysis_time, status in rows:
                st = (status or 'unknown').strip().lower()
                status_breakdown[st] = status_breakdown.get(st, 0) + 1

                if analysis_time:
                    dk = analysis_time.date().isoformat()
                    daily_total[dk] = daily_total.get(dk, 0) + 1
                    if st == 'failed':
                        daily_failed[dk] = daily_failed.get(dk, 0) + 1

            total = len(rows)
            failed = status_breakdown.get('failed', 0)
            completed = status_breakdown.get('completed', 0)
            terminal_total = failed + completed
            # Prefer "terminal" error rate: failed / (failed + completed)
            error_rate = (failed / terminal_total * 100.0) if terminal_total > 0 else 0.0
            # Also provide all-status error rate for context (includes pending/processing)
            error_rate_all = (failed / total * 100.0) if total > 0 else 0.0

            all_dates = sorted(set(list(daily_total.keys()) + list(daily_failed.keys())))
            daily_failure_trend = []
            for d in all_dates:
                t = daily_total.get(d, 0)
                f = daily_failed.get(d, 0)
                daily_failure_trend.append({
                    'date': d,
                    'total': t,
                    'failed': f,
                    'error_rate_all': round((f / t * 100.0), 2) if t > 0 else 0.0
                })

            period_label = 'Tất cả thời gian' if days in (None, 0) else f'Trong {int(days)} ngày gần đây'
            return {
                'period_days': None if days in (None, 0) else int(days),
                'period_label': period_label,
                'total_analyses': total,
                'failed_analyses': failed,
                'completed_analyses': completed,
                'terminal_total': terminal_total,
                'error_rate': round(error_rate, 2),
                'error_rate_all': round(error_rate_all, 2),
                'status_breakdown': status_breakdown,
                'daily_failure_trend': daily_failure_trend,
                'has_data': total > 0
            }
        except Exception as e:
            raise ValueError(f'Error getting error rate analytics: {str(e)}')
        finally:
            self.session.close()