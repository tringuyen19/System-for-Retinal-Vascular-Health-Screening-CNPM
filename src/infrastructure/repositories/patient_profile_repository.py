from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.profiles.patient_profile_model import PatientProfileModel
from domain.models.patient_profile import PatientProfile
from domain.models.ipatient_profile_repository import IPatientProfileRepository


class PatientProfileRepository(IPatientProfileRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: PatientProfileModel) -> PatientProfile:
        """Convert PatientProfileModel (Infrastructure) to PatientProfile (Domain)"""
        return PatientProfile(
            patient_id=model.patient_id,
            account_id=model.account_id,
            patient_name=model.patient_name,
            date_of_birth=model.date_of_birth,
            gender=model.gender,
            medical_history=model.medical_history
        )
    
    def add(self, account_id: int, patient_name: str, 
            date_of_birth: Optional[date] = None,
            gender: Optional[str] = None,
            medical_history: Optional[str] = None) -> PatientProfile:
        """Create a new patient profile"""
        try:
            patient_model = PatientProfileModel(
                account_id=account_id,
                patient_name=patient_name,
                date_of_birth=date_of_birth,
                gender=gender,
                medical_history=medical_history
            )
            self.session.add(patient_model)
            self.session.commit()
            self.session.refresh(patient_model)
            return self._to_domain(patient_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating patient profile: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, patient_id: int) -> Optional[PatientProfile]:
        """Get patient profile by patient_id"""
        try:
            patient_model = self.session.query(PatientProfileModel).filter_by(patient_id=patient_id).first()
            return self._to_domain(patient_model) if patient_model else None
        except Exception as e:
            raise ValueError(f'Error getting patient profile: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_account_id(self, account_id: int) -> Optional[PatientProfile]:
        """Get patient profile by account_id"""
        try:
            patient_model = self.session.query(PatientProfileModel).filter_by(account_id=account_id).first()
            return self._to_domain(patient_model) if patient_model else None
        except Exception as e:
            raise ValueError(f'Error getting patient by account_id: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_name(self, patient_name: str) -> List[PatientProfile]:
        """Search patients by name (partial match)"""
        try:
            patient_models = self.session.query(PatientProfileModel).filter(
                PatientProfileModel.patient_name.like(f'%{patient_name}%')
            ).all()
            return [self._to_domain(model) for model in patient_models]
        except Exception as e:
            raise ValueError(f'Error searching patients by name: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[PatientProfile]:
        """Get all patient profiles"""
        try:
            patient_models = self.session.query(PatientProfileModel).all()
            return [self._to_domain(model) for model in patient_models]
        except Exception as e:
            raise ValueError(f'Error getting all patients: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, patient_id: int, **kwargs) -> Optional[PatientProfile]:
        """Update patient profile fields"""
        try:
            patient_model = self.session.query(PatientProfileModel).filter_by(patient_id=patient_id).first()
            if not patient_model:
                return None
            
            # Update only provided fields
            for key, value in kwargs.items():
                if hasattr(patient_model, key) and key != 'patient_id' and key != 'account_id':
                    setattr(patient_model, key, value)
            
            self.session.commit()
            self.session.refresh(patient_model)
            return self._to_domain(patient_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating patient profile: {str(e)}')
        finally:
            self.session.close()
    
    def update_medical_history(self, patient_id: int, medical_history: str) -> Optional[PatientProfile]:
        """Update patient medical history"""
        try:
            patient_model = self.session.query(PatientProfileModel).filter_by(patient_id=patient_id).first()
            if not patient_model:
                return None
            
            patient_model.medical_history = medical_history
            self.session.commit()
            self.session.refresh(patient_model)
            return self._to_domain(patient_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating medical history: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, patient_id: int) -> bool:
        """Delete patient profile"""
        try:
            patient_model = self.session.query(PatientProfileModel).filter_by(patient_id=patient_id).first()
            if not patient_model:
                return False
            
            self.session.delete(patient_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting patient profile: {str(e)}')
        finally:
            self.session.close()
    
    def count_patients(self) -> int:
        """Count total number of patients"""
        try:
            count = self.session.query(PatientProfileModel).count()
            return count
        except Exception as e:
            raise ValueError(f'Error counting patients: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_clinic_id(self, clinic_id: int) -> List[PatientProfile]:
        """
        Get patients assigned to a clinic (FR-13)
        Patients are assigned via their account's clinic_id
        """
        try:
            from infrastructure.models.account_model import AccountModel
            # Join with accounts table to filter by clinic_id
            patient_models = self.session.query(PatientProfileModel).join(
                AccountModel, PatientProfileModel.account_id == AccountModel.account_id
            ).filter(AccountModel.clinic_id == clinic_id).all()
            return [self._to_domain(model) for model in patient_models]
        except Exception as e:
            raise ValueError(f'Error getting patients by clinic: {str(e)}')
        finally:
            self.session.close()
    
    def search_by_name_and_clinic(self, patient_name: str, clinic_id: Optional[int] = None) -> List[PatientProfile]:
        """
        Search patients by name, optionally filtered by clinic (FR-18)
        """
        try:
            from infrastructure.models.account_model import AccountModel
            query = self.session.query(PatientProfileModel).join(
                AccountModel, PatientProfileModel.account_id == AccountModel.account_id
            ).filter(PatientProfileModel.patient_name.like(f'%{patient_name}%'))
            
            if clinic_id:
                query = query.filter(AccountModel.clinic_id == clinic_id)
            
            patient_models = query.all()
            return [self._to_domain(model) for model in patient_models]
        except Exception as e:
            raise ValueError(f'Error searching patients: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_risk_level(self, risk_level: str, clinic_id: Optional[int] = None, 
                          patient_name: Optional[str] = None) -> List[PatientProfile]:
        """
        Get patients by risk level with optional filters (FR-18)
        Uses JOIN: patient_profiles -> retinal_images -> ai_analysis -> ai_results
        """
        try:
            from infrastructure.models.account_model import AccountModel
            from infrastructure.models.imaging.retinal_image_model import RetinalImageModel
            from infrastructure.models.ai.ai_analysis_model import AiAnalysisModel
            from infrastructure.models.ai.ai_result_model import AiResultModel
            
            # Complex JOIN query to filter by risk_level
            query = self.session.query(PatientProfileModel).distinct().join(
                AccountModel, PatientProfileModel.account_id == AccountModel.account_id
            ).join(
                RetinalImageModel, PatientProfileModel.account_id == RetinalImageModel.patient_id
            ).join(
                AiAnalysisModel, RetinalImageModel.image_id == AiAnalysisModel.image_id
            ).join(
                AiResultModel, AiAnalysisModel.analysis_id == AiResultModel.analysis_id
            ).filter(AiResultModel.risk_level == risk_level)
            
            # Apply optional filters
            if clinic_id:
                query = query.filter(AccountModel.clinic_id == clinic_id)
            if patient_name:
                query = query.filter(PatientProfileModel.patient_name.like(f'%{patient_name}%'))
            
            patient_models = query.all()
            return [self._to_domain(model) for model in patient_models]
        except Exception as e:
            raise ValueError(f'Error getting patients by risk level: {str(e)}')
        finally:
            self.session.close()