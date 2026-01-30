from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.messaging.message_model import MessageModel
from domain.models.message import Message
from domain.models.imessage_repository import IMessageRepository


class MessageRepository(IMessageRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: MessageModel) -> Message:
        return Message(
            message_id=model.message_id, conversation_id=model.conversation_id,
            sender_type=model.sender_type, sender_name=model.sender_name,
            content=model.content, message_type=model.message_type, sent_at=model.sent_at
        )
    
    def add(self, conversation_id: int, sender_type: str, sender_name: str,
            content: str, message_type: str, sent_at: datetime) -> Message:
        try:
            msg_model = MessageModel(
                conversation_id=conversation_id, sender_type=sender_type, sender_name=sender_name,
                content=content, message_type=message_type, sent_at=sent_at
            )
            self.session.add(msg_model)
            self.session.commit()
            self.session.refresh(msg_model)
            return self._to_domain(msg_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating message: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, message_id: int) -> Optional[Message]:
        try:
            msg_model = self.session.query(MessageModel).filter_by(message_id=message_id).first()
            return self._to_domain(msg_model) if msg_model else None
        except Exception as e:
            raise ValueError(f'Error getting message: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_conversation(self, conversation_id: int) -> List[Message]:
        try:
            msg_models = self.session.query(MessageModel).filter_by(
                conversation_id=conversation_id
            ).order_by(MessageModel.sent_at.asc()).all()
            return [self._to_domain(model) for model in msg_models]
        except Exception as e:
            raise ValueError(f'Error getting messages by conversation: {str(e)}')
        finally:
            self.session.close()
    
    def get_last_message(self, conversation_id: int) -> Optional[Message]:
        try:
            msg_model = self.session.query(MessageModel).filter_by(
                conversation_id=conversation_id
            ).order_by(MessageModel.sent_at.desc()).first()
            return self._to_domain(msg_model) if msg_model else None
        except Exception as e:
            raise ValueError(f'Error getting last message: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_sender(self, conversation_id: int, sender_type: str) -> List[Message]:
        try:
            msg_models = self.session.query(MessageModel).filter_by(
                conversation_id=conversation_id, sender_type=sender_type
            ).all()
            return [self._to_domain(model) for model in msg_models]
        except Exception as e:
            raise ValueError(f'Error getting messages by sender: {str(e)}')
        finally:
            self.session.close()
    
    def search_messages(self, conversation_id: int, search_term: str) -> List[Message]:
        try:
            msg_models = self.session.query(MessageModel).filter(
                MessageModel.conversation_id == conversation_id,
                MessageModel.content.like(f'%{search_term}%')
            ).all()
            return [self._to_domain(model) for model in msg_models]
        except Exception as e:
            raise ValueError(f'Error searching messages: {str(e)}')
        finally:
            self.session.close()
    
    def update(self, message_id: int, **kwargs) -> Optional[Message]:
        try:
            msg_model = self.session.query(MessageModel).filter_by(message_id=message_id).first()
            if not msg_model:
                return None
            for key, value in kwargs.items():
                if hasattr(msg_model, key) and key not in ['message_id', 'sent_at']:
                    setattr(msg_model, key, value)
            self.session.commit()
            self.session.refresh(msg_model)
            return self._to_domain(msg_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating message: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, message_id: int) -> bool:
        try:
            msg_model = self.session.query(MessageModel).filter_by(message_id=message_id).first()
            if not msg_model:
                return False
            self.session.delete(msg_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting message: {str(e)}')
        finally:
            self.session.close()
    
    def delete_all_by_conversation(self, conversation_id: int) -> bool:
        try:
            self.session.query(MessageModel).filter_by(conversation_id=conversation_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting all messages: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_conversation(self, conversation_id: int) -> int:
        try:
            return self.session.query(MessageModel).filter_by(conversation_id=conversation_id).count()
        except Exception as e:
            raise ValueError(f'Error counting messages: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_sender(self, conversation_id: int, sender_type: str) -> int:
        try:
            return self.session.query(MessageModel).filter_by(
                conversation_id=conversation_id, sender_type=sender_type
            ).count()
        except Exception as e:
            raise ValueError(f'Error counting messages by sender: {str(e)}')
        finally:
            self.session.close()
