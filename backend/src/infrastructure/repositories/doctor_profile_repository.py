from typing import List, Optional
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.profiles.doctor_profile_model import DoctorProfileModel
from domain.models.doctor_profile import DoctorProfile
from domain.models.idoctor_profile_repository import IDoctorProfileRepository


class DoctorProfileRepository(IDoctorProfileRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: DoctorProfileModel) -> DoctorProfile:
        """Convert DoctorProfileModel to DoctorProfile (Domain)"""
        return DoctorProfile(
            doctor_id=model.doctor_id,
            account_id=model.account_id,
            doctor_name=model.doctor_name,
            specialization=model.specialization,
            license_number=model.license_number
        )
    
    def add(self, account_id: int, doctor_name: str, specialization: str, 
            license_number: str) -> DoctorProfile:
        """Create a new doctor profile"""
        try:
            doctor_model = DoctorProfileModel(
                account_id=account_id,
                doctor_name=doctor_name,
                specialization=specialization,
                license_number=license_number
            )
            self.session.add(doctor_model)
            self.session.commit()
            self.session.refresh(doctor_model)
            return self._to_domain(doctor_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating doctor profile: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, doctor_id: int) -> Optional[DoctorProfile]:
        """Get doctor profile by doctor_id"""
        try:
            doctor_model = self.session.query(DoctorProfileModel).filter_by(doctor_id=doctor_id).first()
            return self._to_domain(doctor_model) if doctor_model else None
        except Exception as e:
            raise ValueError(f'Error getting doctor profile: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_account_id(self, account_id: int) -> Optional[DoctorProfile]:
        """Get doctor profile by account_id"""
        try:
            doctor_model = self.session.query(DoctorProfileModel).filter_by(account_id=account_id).first()
            return self._to_domain(doctor_model) if doctor_model else None
        except Exception as e:
            raise ValueError(f'Error getting doctor by account_id: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_license_number(self, license_number: str) -> Optional[DoctorProfile]:
        """Get doctor by license number"""
        try:
            doctor_model = self.session.query(DoctorProfileModel).filter_by(license_number=license_number).first()
            return self._to_domain(doctor_model) if doctor_model else None
        except Exception as e:
            raise ValueError(f'Error getting doctor by license: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_specialization(self, specialization: str) -> List[DoctorProfile]:
        """Get doctors by specialization"""
        try:
            doctor_models = self.session.query(DoctorProfileModel).filter_by(specialization=specialization).all()
            return [self._to_domain(model) for model in doctor_models]
        except Exception as e:
            raise ValueError(f'Error getting doctors by specialization: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_name(self, doctor_name: str) -> List[DoctorProfile]:
        """Search doctors by name (partial match)"""
        try:
            doctor_models = self.session.query(DoctorProfileModel).filter(
                DoctorProfileModel.doctor_name.like(f'%{doctor_name}%')
            ).all()
            return [self._to_domain(model) for model in doctor_models]
        except Exception as e:
            raise ValueError(f'Error searching doctors by name: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[DoctorProfile]:
        """Get all doctor profiles"""
        try:
            doctor_models = self.session.query(DoctorProfileModel).all()
            return [self._to_domain(model) for model in doctor_models]
        except Exception as e:
            raise ValueError(f'Error getting all doctors: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, doctor_id: int, **kwargs) -> Optional[DoctorProfile]:
        """Update doctor profile fields"""
        try:
            doctor_model = self.session.query(DoctorProfileModel).filter_by(doctor_id=doctor_id).first()
            if not doctor_model:
                return None
            
            for key, value in kwargs.items():
                if hasattr(doctor_model, key) and key != 'doctor_id' and key != 'account_id':
                    setattr(doctor_model, key, value)
            
            self.session.commit()
            self.session.refresh(doctor_model)
            return self._to_domain(doctor_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating doctor profile: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, doctor_id: int) -> bool:
        """Delete doctor profile"""
        try:
            doctor_model = self.session.query(DoctorProfileModel).filter_by(doctor_id=doctor_id).first()
            if not doctor_model:
                return False
            
            self.session.delete(doctor_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting doctor profile: {str(e)}')
        finally:
            self.session.close()
    
    def count_doctors(self) -> int:
        """Count total doctors"""
        try:
            return self.session.query(DoctorProfileModel).count()
        except Exception as e:
            raise ValueError(f'Error counting doctors: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_specialization(self, specialization: str) -> int:
        """Count doctors by specialization"""
        try:
            return self.session.query(DoctorProfileModel).filter_by(specialization=specialization).count()
        except Exception as e:
            raise ValueError(f'Error counting doctors by specialization: {str(e)}')
        finally:
            self.session.close()
    
    def check_license_exists(self, license_number: str) -> bool:
        """Check if license number exists"""
        try:
            doctor_model = self.session.query(DoctorProfileModel).filter_by(license_number=license_number).first()
            return doctor_model is not None
        except Exception as e:
            raise ValueError(f'Error checking license existence: {str(e)}')
        finally:
            self.session.close()
