from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.messaging.conversation_model import ConversationModel
from domain.models.conversation import Conversation
from domain.models.iconversation_repository import IConversationRepository


class ConversationRepository(IConversationRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: ConversationModel) -> Conversation:
        return Conversation(
            conversation_id=model.conversation_id, patient_id=model.patient_id,
            doctor_id=model.doctor_id, created_at=model.created_at, status=model.status
        )
    
    def add(self, patient_id: int, doctor_id: int, created_at: datetime, status: str) -> Conversation:
        try:
            conv_model = ConversationModel(
                patient_id=patient_id, doctor_id=doctor_id, created_at=created_at, status=status
            )
            self.session.add(conv_model)
            self.session.commit()
            self.session.refresh(conv_model)
            return self._to_domain(conv_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating conversation: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        try:
            conv_model = self.session.query(ConversationModel).filter_by(conversation_id=conversation_id).first()
            return self._to_domain(conv_model) if conv_model else None
        except Exception as e:
            raise ValueError(f'Error getting conversation: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_patient(self, patient_id: int) -> List[Conversation]:
        try:
            conv_models = self.session.query(ConversationModel).filter_by(patient_id=patient_id).all()
            return [self._to_domain(model) for model in conv_models]
        except Exception as e:
            raise ValueError(f'Error getting conversations by patient: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_doctor(self, doctor_id: int) -> List[Conversation]:
        try:
            conv_models = self.session.query(ConversationModel).filter_by(doctor_id=doctor_id).all()
            return [self._to_domain(model) for model in conv_models]
        except Exception as e:
            raise ValueError(f'Error getting conversations by doctor: {str(e)}')
        finally:
            self.session.close()
    
    def get_active_by_patient(self, patient_id: int) -> List[Conversation]:
        try:
            conv_models = self.session.query(ConversationModel).filter_by(patient_id=patient_id, status='active').all()
            return [self._to_domain(model) for model in conv_models]
        except Exception as e:
            raise ValueError(f'Error getting active conversations by patient: {str(e)}')
        finally:
            self.session.close()
    
    def get_active_by_doctor(self, doctor_id: int) -> List[Conversation]:
        try:
            conv_models = self.session.query(ConversationModel).filter_by(doctor_id=doctor_id, status='active').all()
            return [self._to_domain(model) for model in conv_models]
        except Exception as e:
            raise ValueError(f'Error getting active conversations by doctor: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self) -> List[Conversation]:
        try:
            conv_models = self.session.query(ConversationModel).all()
            return [self._to_domain(model) for model in conv_models]
        except Exception as e:
            raise ValueError(f'Error getting all conversations: {str(e)}')
        finally:
            self.session.close()
    
    def get_or_create_conversation(self, patient_id: int, doctor_id: int) -> Conversation:
        try:
            conv_model = self.session.query(ConversationModel).filter_by(
                patient_id=patient_id, doctor_id=doctor_id
            ).first()
            if conv_model:
                return self._to_domain(conv_model)
            conv_model = ConversationModel(
                patient_id=patient_id, doctor_id=doctor_id, created_at=datetime.now(), status='active'
            )
            self.session.add(conv_model)
            self.session.commit()
            self.session.refresh(conv_model)
            return self._to_domain(conv_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error getting or creating conversation: {str(e)}')
        finally:
            self.session.close()
    
    def close_conversation(self, conversation_id: int) -> Optional[Conversation]:
        try:
            conv_model = self.session.query(ConversationModel).filter_by(conversation_id=conversation_id).first()
            if not conv_model:
                return None
            conv_model.status = 'closed'
            self.session.commit()
            self.session.refresh(conv_model)
            return self._to_domain(conv_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error closing conversation: {str(e)}')
        finally:
            self.session.close()
    
    def reopen_conversation(self, conversation_id: int) -> Optional[Conversation]:
        try:
            conv_model = self.session.query(ConversationModel).filter_by(conversation_id=conversation_id).first()
            if not conv_model:
                return None
            conv_model.status = 'active'
            self.session.commit()
            self.session.refresh(conv_model)
            return self._to_domain(conv_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error reopening conversation: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, conversation_id: int, **kwargs) -> Optional[Conversation]:
        try:
            conv_model = self.session.query(ConversationModel).filter_by(conversation_id=conversation_id).first()
            if not conv_model:
                return None
            for key, value in kwargs.items():
                if hasattr(conv_model, key) and key not in ['conversation_id', 'created_at']:
                    setattr(conv_model, key, value)
            self.session.commit()
            self.session.refresh(conv_model)
            return self._to_domain(conv_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating conversation: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, conversation_id: int) -> bool:
        try:
            conv_model = self.session.query(ConversationModel).filter_by(conversation_id=conversation_id).first()
            if not conv_model:
                return False
            self.session.delete(conv_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting conversation: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_patient(self, patient_id: int) -> int:
        try:
            return self.session.query(ConversationModel).filter_by(patient_id=patient_id).count()
        except Exception as e:
            raise ValueError(f'Error counting conversations by patient: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_doctor(self, doctor_id: int) -> int:
        try:
            return self.session.query(ConversationModel).filter_by(doctor_id=doctor_id).count()
        except Exception as e:
            raise ValueError(f'Error counting conversations by doctor: {str(e)}')
        finally:
            self.session.close()
    
    def count_active(self) -> int:
        try:
            return self.session.query(ConversationModel).filter_by(status='active').count()
        except Exception as e:
            raise ValueError(f'Error counting active conversations: {str(e)}')
        finally:
            self.session.close()
