from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.clinic_model import ClinicModel
from domain.models.clinic import Clinic
from domain.models.iclinic_repository import IClinicRepository


class ClinicRepository(IClinicRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: ClinicModel) -> Clinic:
        return Clinic(
            clinic_id=model.clinic_id,
            name=model.name,
            address=model.address,
            phone=model.phone,
            logo_url=model.logo_url,
            verification_status=model.verification_status,
            created_at=model.created_at
        )
    
    def add(self, name: str, address: str, phone: str, logo_url: str,
            verification_status: str, created_at: datetime) -> Clinic:
        try:
            clinic_model = ClinicModel(
                name=name, address=address, phone=phone, logo_url=logo_url,
                verification_status=verification_status, created_at=created_at
            )
            self.session.add(clinic_model)
            self.session.commit()
            self.session.refresh(clinic_model)
            return self._to_domain(clinic_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating clinic: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, clinic_id: int) -> Optional[Clinic]:
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            return self._to_domain(clinic_model) if clinic_model else None
        except Exception as e:
            raise ValueError(f'Error getting clinic: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_name(self, name: str) -> List[Clinic]:
        try:
            clinic_models = self.session.query(ClinicModel).filter(
                ClinicModel.name.like(f'%{name}%')
            ).all()
            return [self._to_domain(model) for model in clinic_models]
        except Exception as e:
            raise ValueError(f'Error searching clinics by name: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[Clinic]:
        try:
            clinic_models = self.session.query(ClinicModel).all()
            return [self._to_domain(model) for model in clinic_models]
        except Exception as e:
            raise ValueError(f'Error getting all clinics: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_status(self, status: str) -> List[Clinic]:
        try:
            clinic_models = self.session.query(ClinicModel).filter_by(verification_status=status).all()
            return [self._to_domain(model) for model in clinic_models]
        except Exception as e:
            raise ValueError(f'Error getting clinics by status: {str(e)}')
        finally:
            self.session.close()
    
    def get_verified(self) -> List[Clinic]:
        return self.get_by_status('verified')
    
    def get_pending(self) -> List[Clinic]:
        return self.get_by_status('pending')
    
    def verify_clinic(self, clinic_id: int) -> Optional[Clinic]:
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            if not clinic_model:
                return None
            clinic_model.verification_status = 'verified'
            self.session.commit()
            self.session.refresh(clinic_model)
            return self._to_domain(clinic_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error verifying clinic: {str(e)}')
        finally:
            self.session.close()
    
    def reject_clinic(self, clinic_id: int) -> Optional[Clinic]:
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            if not clinic_model:
                return None
            clinic_model.verification_status = 'rejected'
            self.session.commit()
            self.session.refresh(clinic_model)
            return self._to_domain(clinic_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error rejecting clinic: {str(e)}')
        finally:
            self.session.close()
    
    def suspend_clinic(self, clinic_id: int) -> Optional[Clinic]:
        """Suspend a clinic (FR-38) - Can suspend verified clinics"""
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            if not clinic_model:
                return None
            clinic_model.verification_status = 'suspended'
            self.session.commit()
            self.session.refresh(clinic_model)
            return self._to_domain(clinic_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error suspending clinic: {str(e)}')
        finally:
            self.session.close()
    
    def approve_clinic(self, clinic_id: int) -> Optional[Clinic]:
        """Approve a clinic (FR-38) - Alias for verify_clinic, but can also unsuspend"""
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            if not clinic_model:
                return None
            # Can approve from pending or unsuspend from suspended
            if clinic_model.verification_status in ['pending', 'suspended']:
                clinic_model.verification_status = 'verified'
                self.session.commit()
                self.session.refresh(clinic_model)
                return self._to_domain(clinic_model)
            return self._to_domain(clinic_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error approving clinic: {str(e)}')
        finally:
            self.session.close()

    def update(self, clinic_id: int, **kwargs) -> Optional[Clinic]:
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            if not clinic_model:
                return None
            for key, value in kwargs.items():
                if hasattr(clinic_model, key) and key not in ['clinic_id', 'created_at']:
                    setattr(clinic_model, key, value)
            self.session.commit()
            self.session.refresh(clinic_model)
            return self._to_domain(clinic_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating clinic: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, clinic_id: int) -> bool:
        try:
            clinic_model = self.session.query(ClinicModel).filter_by(clinic_id=clinic_id).first()
            if not clinic_model:
                return False
            self.session.delete(clinic_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting clinic: {str(e)}')
        finally:
            self.session.close()
    
    def count_clinics(self, status: Optional[str] = None) -> int:
        try:
            query = self.session.query(ClinicModel)
            if status:
                query = query.filter_by(verification_status=status)
            return query.count()
        except Exception as e:
            raise ValueError(f'Error counting clinics: {str(e)}')
        finally:
            self.session.close()
