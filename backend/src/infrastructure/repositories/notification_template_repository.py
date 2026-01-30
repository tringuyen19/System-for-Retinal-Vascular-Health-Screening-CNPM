from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from infrastructure.databases.mssql import session
from infrastructure.models.notification_template_model import NotificationTemplateModel
from domain.models.notification_template import NotificationTemplate
from domain.models.inotification_template_repository import INotificationTemplateRepository


class NotificationTemplateRepository(INotificationTemplateRepository):
    """Repository implementation for Notification Template - Infrastructure layer"""
    
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: NotificationTemplateModel) -> NotificationTemplate:
        """Convert NotificationTemplateModel (Infrastructure) to NotificationTemplate (Domain)"""
        return NotificationTemplate(
            template_id=model.template_id,
            template_name=model.template_name,
            template_type=model.template_type,
            subject=model.subject,
            content_template=model.content_template,
            variables_schema=model.variables_schema,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def create_template(self, template_name: str, template_type: str,
                       subject: Optional[str], content_template: str,
                       variables_schema: Optional[str], is_active: bool,
                       created_at: datetime, updated_at: datetime) -> NotificationTemplate:
        """Create a new notification template"""
        try:
            template_model = NotificationTemplateModel(
                template_name=template_name,
                template_type=template_type,
                subject=subject,
                content_template=content_template,
                variables_schema=variables_schema,
                is_active=is_active,
                created_at=created_at or datetime.now(),
                updated_at=updated_at or datetime.now()
            )
            self.session.add(template_model)
            self.session.commit()
            self.session.refresh(template_model)
            return self._to_domain(template_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating notification template: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, template_id: int) -> Optional[NotificationTemplate]:
        """Get template by ID"""
        try:
            model = self.session.query(NotificationTemplateModel).filter_by(
                template_id=template_id
            ).first()
            return self._to_domain(model) if model else None
        except Exception as e:
            raise ValueError(f'Error getting notification template: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_type(self, template_type: str) -> List[NotificationTemplate]:
        """Get templates by type"""
        try:
            models = self.session.query(NotificationTemplateModel).filter_by(
                template_type=template_type
            ).order_by(NotificationTemplateModel.created_at.desc()).all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting notification templates by type: {str(e)}')
        finally:
            self.session.close()
    
    def get_active_by_type(self, template_type: str) -> Optional[NotificationTemplate]:
        """Get active template by type (only one active per type)"""
        try:
            model = self.session.query(NotificationTemplateModel).filter_by(
                template_type=template_type,
                is_active=True
            ).first()
            return self._to_domain(model) if model else None
        except Exception as e:
            raise ValueError(f'Error getting active notification template by type: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self, include_inactive: bool = False) -> List[NotificationTemplate]:
        """Get all templates"""
        try:
            query = self.session.query(NotificationTemplateModel)
            if not include_inactive:
                query = query.filter_by(is_active=True)
            models = query.order_by(NotificationTemplateModel.created_at.desc()).all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting all notification templates: {str(e)}')
        finally:
            self.session.close()
    
    def update_template(self, template_id: int, template_name: Optional[str] = None,
                       subject: Optional[str] = None, content_template: Optional[str] = None,
                       variables_schema: Optional[str] = None,
                       updated_at: datetime = None) -> Optional[NotificationTemplate]:
        """Update template"""
        try:
            model = self.session.query(NotificationTemplateModel).filter_by(
                template_id=template_id
            ).first()
            if not model:
                return None
            
            if template_name is not None:
                model.template_name = template_name
            if subject is not None:
                model.subject = subject
            if content_template is not None:
                model.content_template = content_template
            if variables_schema is not None:
                model.variables_schema = variables_schema
            
            model.updated_at = updated_at or datetime.now()
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error updating notification template: {str(e)}')
        finally:
            self.session.close()
    
    def activate_template(self, template_id: int, updated_at: datetime) -> Optional[NotificationTemplate]:
        """Activate template (deactivate others of same type)"""
        try:
            model = self.session.query(NotificationTemplateModel).filter_by(
                template_id=template_id
            ).first()
            if not model:
                return None
            
            # Deactivate all other templates of the same type
            self.session.query(NotificationTemplateModel).filter_by(
                template_type=model.template_type
            ).filter(NotificationTemplateModel.template_id != template_id).update(
                {NotificationTemplateModel.is_active: False}
            )
            
            # Activate this template
            model.is_active = True
            model.updated_at = updated_at or datetime.now()
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error activating notification template: {str(e)}')
        finally:
            self.session.close()
    
    def deactivate_template(self, template_id: int, updated_at: datetime) -> Optional[NotificationTemplate]:
        """Deactivate template"""
        try:
            model = self.session.query(NotificationTemplateModel).filter_by(
                template_id=template_id
            ).first()
            if not model:
                return None
            
            model.is_active = False
            model.updated_at = updated_at or datetime.now()
            
            self.session.commit()
            self.session.refresh(model)
            return self._to_domain(model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deactivating notification template: {str(e)}')
        finally:
            self.session.close()
    
    def delete_template(self, template_id: int) -> bool:
        """Delete template"""
        try:
            model = self.session.query(NotificationTemplateModel).filter_by(
                template_id=template_id
            ).first()
            if not model:
                return False
            
            self.session.delete(model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting notification template: {str(e)}')
        finally:
            self.session.close()