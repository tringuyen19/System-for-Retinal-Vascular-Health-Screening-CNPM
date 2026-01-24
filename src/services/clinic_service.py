"""
Clinic Service - Business Logic Layer
Handles clinic management and verification
"""

from typing import List, Optional
from datetime import datetime
from domain.models.clinic import Clinic
from domain.models.iclinic_repository import IClinicRepository


class ClinicService:
    def __init__(self, repository: IClinicRepository):
        self.repository = repository
    
    def register_clinic(self, name: str, address: str, phone: str, 
                       logo_url: str, verification_status: str = 'pending') -> Optional[Clinic]:
        """Register new clinic"""
        return self.repository.add(
            name=name,
            address=address,
            phone=phone,
            logo_url=logo_url,
            verification_status=verification_status,
            created_at=datetime.now()
        )
    
    def get_clinic_by_id(self, clinic_id: int) -> Optional[Clinic]:
        """Get clinic by ID"""
        return self.repository.get_by_id(clinic_id)
    
    def search_clinics_by_name(self, name: str) -> List[Clinic]:
        """Search clinics by name"""
        return self.repository.get_by_name(name)
    
    def list_all_clinics(self, status: Optional[str] = None) -> List[Clinic]:
        """Get all clinics (optionally filter by status)"""
        if status:
            return self.repository.get_by_status(status)
        return self.repository.get_all()
    
    def get_verified_clinics(self) -> List[Clinic]:
        """Get all verified clinics"""
        return self.repository.get_verified()
    
    def get_pending_clinics(self) -> List[Clinic]:
        """Get clinics pending verification"""
        return self.repository.get_pending()
    
    def verify_clinic(self, clinic_id: int) -> Optional[Clinic]:
        """Verify clinic (Admin only)"""
        return self.repository.verify_clinic(clinic_id)
    
    def reject_clinic(self, clinic_id: int) -> Optional[Clinic]:
        """Reject clinic verification"""
        return self.repository.reject_clinic(clinic_id)
    
    def update_clinic(self, clinic_id: int, **kwargs) -> Optional[Clinic]:
        """Update clinic information"""
        return self.repository.update(clinic_id, **kwargs)
    
    def delete_clinic(self, clinic_id: int) -> bool:
        """Delete clinic"""
        return self.repository.delete(clinic_id)
    
    def count_clinics(self, status: Optional[str] = None) -> int:
        """Count clinics by status"""
        return self.repository.count_clinics(status)
    
    def get_clinic_statistics(self) -> dict:
        """Get clinic statistics"""
        return {
            'total_clinics': self.repository.count_clinics(None),
            'verified': self.repository.count_clinics('verified'),
            'pending': self.repository.count_clinics('pending'),
            'rejected': self.repository.count_clinics('rejected')
        }
