from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.medical.medical_report_model import MedicalReportModel
from domain.models.medical_report import MedicalReport
from domain.models.imedical_report_repository import IMedicalReportRepository


class MedicalReportRepository(IMedicalReportRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: MedicalReportModel) -> MedicalReport:
        return MedicalReport(
            report_id=model.report_id, patient_id=model.patient_id, analysis_id=model.analysis_id,
            doctor_id=model.doctor_id, report_url=model.report_url, created_at=model.created_at
        )
    
    def add(self, patient_id: int, analysis_id: int, doctor_id: int, report_url: str, created_at: datetime) -> MedicalReport:
        try:
            report_model = MedicalReportModel(
                patient_id=patient_id, analysis_id=analysis_id, doctor_id=doctor_id,
                report_url=report_url, created_at=created_at
            )
            self.session.add(report_model)
            self.session.commit()
            self.session.refresh(report_model)
            return self._to_domain(report_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating medical report: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, report_id: int) -> Optional[MedicalReport]:
        try:
            report_model = self.session.query(MedicalReportModel).filter_by(report_id=report_id).first()
            return self._to_domain(report_model) if report_model else None
        except Exception as e:
            raise ValueError(f'Error getting medical report: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_analysis_id(self, analysis_id: int) -> Optional[MedicalReport]:
        try:
            report_model = self.session.query(MedicalReportModel).filter_by(analysis_id=analysis_id).first()
            return self._to_domain(report_model) if report_model else None
        except Exception as e:
            raise ValueError(f'Error getting report by analysis: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_patient(self, patient_id: int) -> List[MedicalReport]:
        try:
            report_models = self.session.query(MedicalReportModel).filter_by(patient_id=patient_id).all()
            return [self._to_domain(model) for model in report_models]
        except Exception as e:
            raise ValueError(f'Error getting reports by patient: {str(e)}')
        finally:
            self.session.close()
    
    def get_recent_by_patient(self, patient_id: int, limit: int) -> List[MedicalReport]:
        try:
            report_models = self.session.query(MedicalReportModel).filter_by(
                patient_id=patient_id
            ).order_by(MedicalReportModel.created_at.desc()).limit(limit).all()
            return [self._to_domain(model) for model in report_models]
        except Exception as e:
            raise ValueError(f'Error getting recent reports: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_doctor(self, doctor_id: int) -> List[MedicalReport]:
        try:
            report_models = self.session.query(MedicalReportModel).filter_by(doctor_id=doctor_id).all()
            return [self._to_domain(model) for model in report_models]
        except Exception as e:
            raise ValueError(f'Error getting reports by doctor: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[MedicalReport]:
        try:
            report_models = self.session.query(MedicalReportModel).all()
            return [self._to_domain(model) for model in report_models]
        except Exception as e:
            raise ValueError(f'Error getting all reports: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[MedicalReport]:
        try:
            report_models = self.session.query(MedicalReportModel).filter(
                MedicalReportModel.created_at >= start_date,
                MedicalReportModel.created_at <= end_date
            ).all()
            return [self._to_domain(model) for model in report_models]
        except Exception as e:
            raise ValueError(f'Error getting reports by date range: {str(e)}')
        finally:
            self.session.close()
    
    def update_report_url(self, report_id: int, report_url: str) -> Optional[MedicalReport]:
        try:
            report_model = self.session.query(MedicalReportModel).filter_by(report_id=report_id).first()
            if not report_model:
                return None
            report_model.report_url = report_url
            self.session.commit()
            self.session.refresh(report_model)
            return self._to_domain(report_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating report URL: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, report_id: int) -> bool:
        try:
            report_model = self.session.query(MedicalReportModel).filter_by(report_id=report_id).first()
            if not report_model:
                return False
            self.session.delete(report_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting report: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_patient(self, patient_id: int) -> int:
        try:
            return self.session.query(MedicalReportModel).filter_by(patient_id=patient_id).count()
        except Exception as e:
            raise ValueError(f'Error counting reports by patient: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_doctor(self, doctor_id: int) -> int:
        try:
            return self.session.query(MedicalReportModel).filter_by(doctor_id=doctor_id).count()
        except Exception as e:
            raise ValueError(f'Error counting reports by doctor: {str(e)}')
        finally:
            self.session.close()
