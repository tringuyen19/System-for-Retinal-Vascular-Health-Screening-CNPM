"""
Message Service - Business Logic Layer
Handles message management in conversations
"""

from typing import List, Optional
from datetime import datetime
from domain.models.message import Message
from domain.models.imessage_repository import IMessageRepository
from domain.exceptions import NotFoundException, ValidationException


class MessageService:
    def __init__(self, repository: IMessageRepository):
        self.repository = repository
    
    def send_message(self, conversation_id: int, sender_type: str, 
                    sender_name: str, content: str, 
                    message_type: str = 'text') -> Message:
        """
        Send message in conversation (FR-10)
        
        Args:
            conversation_id: Conversation ID
            sender_type: Sender type ('patient' or 'doctor')
            sender_name: Sender name
            content: Message content
            message_type: Message type ('text', 'image', 'file')
            
        Returns:
            Message: Created message domain model
            
        Raises:
            ValidationException: If validation fails
        """
        # Validate sender type
        valid_sender_types = ['patient', 'doctor']
        if sender_type.lower() not in valid_sender_types:
            raise ValidationException(f"Invalid sender type. Must be one of: {valid_sender_types}")
        
        # Validate message type
        valid_message_types = ['text', 'image', 'file']
        if message_type.lower() not in valid_message_types:
            raise ValidationException(f"Invalid message type. Must be one of: {valid_message_types}")
        
        # Validate content
        if not content or not content.strip():
            raise ValidationException("Message content is required")
        
        message = self.repository.add(
            conversation_id=conversation_id,
            sender_type=sender_type.lower(),
            sender_name=sender_name,
            content=content,
            message_type=message_type.lower(),
            sent_at=datetime.now()
        )
        
        if not message:
            raise ValueError("Failed to send message")
        
        return message
    
    def send_batch_messages(self, conversation_ids: List[int], sender_type: str,
                           sender_name: str, content: str) -> List[Message]:
        """Send message to multiple conversations"""
        messages = []
        for conv_id in conversation_ids:
            message = self.send_message(conv_id, sender_type, sender_name, content)
            if message:
                messages.append(message)
        return messages
    
    def get_message_by_id(self, message_id: int) -> Message:
        """
        Get message by ID
        
        Raises:
            NotFoundException: If message not found
        """
        message = self.repository.get_by_id(message_id)
        if not message:
            raise NotFoundException(f"Message {message_id} not found")
        return message
    
    def get_messages_by_conversation(self, conversation_id: int) -> List[Message]:
        """Get all messages in a conversation"""
        return self.repository.get_by_conversation(conversation_id)
    
    def get_last_message(self, conversation_id: int) -> Optional[Message]:
        """Get last message in conversation"""
        return self.repository.get_last_message(conversation_id)
    
    def get_messages_by_sender(self, conversation_id: int, sender_type: str) -> List[Message]:
        """Get messages by sender type"""
        return self.repository.get_by_sender(conversation_id, sender_type)
    
    def search_messages(self, conversation_id: int, search_term: str) -> List[Message]:
        """Search messages in conversation"""
        return self.repository.search_messages(conversation_id, search_term)
    
    def update_message(self, message_id: int, **kwargs) -> Optional[Message]:
        """Update message"""
        return self.repository.update(message_id, **kwargs)
    
    def delete_message(self, message_id: int) -> bool:
        """Delete message"""
        return self.repository.delete(message_id)
    
    def delete_all_by_conversation(self, conversation_id: int) -> bool:
        """Delete all messages in a conversation"""
        return self.repository.delete_all_by_conversation(conversation_id)
    
    def count_messages(self, conversation_id: int) -> int:
        """Count messages in conversation"""
        return self.repository.count_by_conversation(conversation_id)
    
    def count_by_sender(self, conversation_id: int, sender_type: str) -> int:
        """Count messages by sender"""
        return self.repository.count_by_sender(conversation_id, sender_type)
    
    def get_message_statistics(self, conversation_id: int) -> dict:
        """Get message statistics for a conversation"""
        all_messages = self.repository.get_by_conversation(conversation_id)
        return {
            'total_messages': len(all_messages),
            'patient_messages': self.repository.count_by_sender(conversation_id, 'patient'),
            'doctor_messages': self.repository.count_by_sender(conversation_id, 'doctor'),
            'text_messages': len([m for m in all_messages if m.message_type == 'text']),
            'image_messages': len([m for m in all_messages if m.message_type == 'image']),
            'file_messages': len([m for m in all_messages if m.message_type == 'file'])
        }
