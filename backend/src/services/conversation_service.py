"""
Conversation Service - Business Logic Layer
Handles patient-doctor conversation management
"""

from typing import List, Optional
from datetime import datetime
from domain.models.conversation import Conversation
from domain.models.iconversation_repository import IConversationRepository
from domain.exceptions import NotFoundException, ValidationException


class ConversationService:
    def __init__(self, repository: IConversationRepository):
        self.repository = repository
    
    def start_conversation(self, patient_id: int, doctor_id: int) -> Conversation:
        """
        Start or get existing conversation between patient and doctor (FR-10)
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
            
        Returns:
            Conversation: Conversation domain model
            
        Raises:
            ValidationException: If patient_id or doctor_id is invalid
        """
        if patient_id <= 0 or doctor_id <= 0:
            raise ValidationException("Invalid patient_id or doctor_id")
        
        conversation = self.repository.get_or_create_conversation(patient_id, doctor_id)
        if not conversation:
            raise ValueError("Failed to create conversation")
        
        return conversation
    
    def create_conversation(self, patient_id: int, doctor_id: int, 
                           status: str = 'active') -> Conversation:
        """
        Create new conversation
        
        Args:
            patient_id: Patient ID
            doctor_id: Doctor ID
            status: Conversation status (default: 'active')
            
        Returns:
            Conversation: Created conversation domain model
        """
        if patient_id <= 0 or doctor_id <= 0:
            raise ValidationException("Invalid patient_id or doctor_id")
        
        conversation = self.repository.add(
            patient_id=patient_id,
            doctor_id=doctor_id,
            created_at=datetime.now(),
            status=status
        )
        
        if not conversation:
            raise ValueError("Failed to create conversation")
        
        return conversation
    
    def get_conversation_by_id(self, conversation_id: int) -> Conversation:
        """
        Get conversation by ID
        
        Raises:
            NotFoundException: If conversation not found
        """
        conversation = self.repository.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation {conversation_id} not found")
        return conversation
    
    def get_conversations_by_patient(self, patient_id: int) -> List[Conversation]:
        """Get all conversations for a patient"""
        return self.repository.get_by_patient(patient_id)
    
    def get_conversations_by_doctor(self, doctor_id: int) -> List[Conversation]:
        """Get all conversations for a doctor"""
        return self.repository.get_by_doctor(doctor_id)
    
    def get_active_conversations_by_patient(self, patient_id: int) -> List[Conversation]:
        """Get active conversations for a patient"""
        return self.repository.get_active_by_patient(patient_id)
    
    def get_active_conversations_by_doctor(self, doctor_id: int) -> List[Conversation]:
        """Get active conversations for a doctor"""
        return self.repository.get_active_by_doctor(doctor_id)
    
    def close_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Close conversation"""
        return self.repository.close_conversation(conversation_id)
    
    def reopen_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """Reopen closed conversation"""
        return self.repository.reopen_conversation(conversation_id)
    
    def update_conversation(self, conversation_id: int, **kwargs) -> Optional[Conversation]:
        """Update conversation"""
        return self.repository.update(conversation_id, **kwargs)
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete conversation"""
        return self.repository.delete(conversation_id)
    
    def count_by_patient(self, patient_id: int) -> int:
        """Count conversations by patient"""
        return self.repository.count_by_patient(patient_id)
    
    def count_by_doctor(self, doctor_id: int) -> int:
        """Count conversations by doctor"""
        return self.repository.count_by_doctor(doctor_id)
    
    def count_active_conversations(self) -> int:
        """Count active conversations"""
        return self.repository.count_active()
    
    def get_conversation_statistics(self) -> dict:
        """Get conversation statistics"""
        all_conversations = self.repository.get_all()
        return {
            'total_conversations': len(all_conversations),
            'active': self.repository.count_active(),
            'closed': len([c for c in all_conversations if c.status == 'closed'])
        }
