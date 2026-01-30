"""
Patient Profile Service - Business Logic Layer
Handles patient profile management
"""

from typing import List, Optional
from datetime import date
from domain.models.patient_profile import PatientProfile
from domain.models.ipatient_profile_repository import IPatientProfileRepository
from domain.exceptions import NotFoundException, ValidationException
from domain.validators import PatientValidator


class PatientProfileService:
    def __init__(self, repository: IPatientProfileRepository):
        self.repository = repository
    
    def create_patient(self, account_id: int, patient_name: str, 
                      date_of_birth: Optional[date] = None, 
                      gender: Optional[str] = None,
                      medical_history: Optional[str] = None) -> PatientProfile:
        """
        Create patient profile with validation (FR-8)
        
        Args:
            account_id: Account ID
            patient_name: Patient full name
            date_of_birth: Optional date of birth
            gender: Optional gender ('male', 'female', 'other', 'prefer_not_to_say')
            medical_history: Optional medical history
            
        Returns:
            PatientProfile: Created patient domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate using domain validators
        PatientValidator.validate_patient_name(patient_name)
        if date_of_birth:
            PatientValidator.validate_date_of_birth(date_of_birth)
        if gender:
            PatientValidator.validate_gender(gender)
        
        patient = self.repository.add(
            account_id=account_id,
            patient_name=patient_name,
            date_of_birth=date_of_birth,
            gender=gender,
            medical_history=medical_history
        )
        
        if not patient:
            raise ValueError("Failed to create patient profile")
        
        return patient
    
    def get_patient_by_id(self, patient_id: int) -> PatientProfile:
        """
        Get patient by ID
        
        Raises:
            NotFoundException: If patient not found
        """
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(f"Patient {patient_id} not found")
        return patient
    
    def get_patient_by_account(self, account_id: int) -> Optional[PatientProfile]:
        """Get patient by account ID"""
        return self.repository.get_by_account_id(account_id)
    
    def search_patients_by_name(self, patient_name: str) -> List[PatientProfile]:
        """Search patients by name"""
        return self.repository.get_by_name(patient_name)
    
    def list_all_patients(self) -> List[PatientProfile]:
        """Get all patients"""
        return self.repository.get_all()
    
    def update_patient(self, patient_id: int, **kwargs) -> PatientProfile:
        """
        Update patient profile with validation
        
        Args:
            patient_id: Patient ID
            **kwargs: Fields to update (patient_name, date_of_birth, gender, medical_history)
            
        Returns:
            PatientProfile: Updated patient domain model
            
        Raises:
            NotFoundException: If patient not found
            ValidationException: If validation fails
        """
        # Get existing patient
        patient = self.get_patient_by_id(patient_id)
        
        # Validate updated fields
        if 'patient_name' in kwargs:
            PatientValidator.validate_patient_name(kwargs['patient_name'])
        if 'date_of_birth' in kwargs:
            PatientValidator.validate_date_of_birth(kwargs['date_of_birth'])
        if 'gender' in kwargs:
            PatientValidator.validate_gender(kwargs['gender'])
        
        updated = self.repository.update(patient_id, **kwargs)
        if not updated:
            raise NotFoundException(f"Patient {patient_id} not found")
        
        return updated
    
    def update_medical_history(self, patient_id: int, medical_history: str) -> Optional[PatientProfile]:
        """Update patient medical history"""
        return self.repository.update_medical_history(patient_id, medical_history)
    
    def delete_patient(self, patient_id: int) -> bool:
        """Delete patient"""
        return self.repository.delete(patient_id)
    
    def count_patients(self) -> int:
        """Count total patients"""
        return self.repository.count_patients()
    
    def get_patient_statistics(self) -> dict:
        """Get patient statistics"""
        return {
            'total_patients': self.repository.count_patients(),
            'male_count': len([p for p in self.repository.get_all() if p.gender == 'male']),
            'female_count': len([p for p in self.repository.get_all() if p.gender == 'female'])
        }
    
    def get_assigned_patients_by_clinic(self, clinic_id: int) -> List[PatientProfile]:
        """
        Get patients assigned to a clinic (FR-13)
        Patients are assigned via their account's clinic_id
        
        Args:
            clinic_id: Clinic ID
            
        Returns:
            List[PatientProfile]: List of patients in the clinic
        """
        return self.repository.get_by_clinic_id(clinic_id)
    
    def search_patients(self, name: Optional[str] = None, clinic_id: Optional[int] = None, 
                       risk_level: Optional[str] = None) -> List[PatientProfile]:
        """
        Search and filter patients (FR-18)
        
        Args:
            name: Patient name (partial match)
            clinic_id: Filter by clinic
            risk_level: Filter by risk level (requires join with AI results)
            
        Returns:
            List[PatientProfile]: Filtered list of patients
        """
        # If only name search, use existing method
        if name and not clinic_id and not risk_level:
            return self.search_patients_by_name(name)
        
        # If name + clinic, use new method
        if name and clinic_id:
            return self.repository.search_by_name_and_clinic(name, clinic_id)
        
        # If clinic only
        if clinic_id and not name:
            return self.get_assigned_patients_by_clinic(clinic_id)
        
        # If risk_level filter, need to join with AI results
        # This is more complex and requires repository method
        if risk_level:
            return self._get_patients_by_risk_level(risk_level, clinic_id, name)
        
        # Default: return all
        return self.list_all_patients()
    
    def _get_patients_by_risk_level(self, risk_level: str, clinic_id: Optional[int] = None, 
                                   name: Optional[str] = None) -> List[PatientProfile]:
        """
        Get patients by risk level (FR-18)
        Uses optimized JOIN query in repository
        """
        # Validate risk level
        valid_levels = ['low', 'medium', 'high', 'critical']
        if risk_level.lower() not in valid_levels:
            raise ValidationException(f"Invalid risk level. Must be one of: {valid_levels}")
        
        return self.repository.get_by_risk_level(
            risk_level=risk_level.lower(),
            clinic_id=clinic_id,
            patient_name=name
        )
