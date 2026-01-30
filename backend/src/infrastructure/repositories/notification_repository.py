from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.databases.mssql import session
from infrastructure.models.notification_model import NotificationModel
from domain.models.notification import Notification
from domain.models.inotification_repository import INotificationRepository


class NotificationRepository(INotificationRepository):
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: NotificationModel) -> Notification:
        return Notification(
            notification_id=model.notification_id,
            account_id=model.account_id,
            notification_type=model.type,
            content=model.content,
            is_read=model.is_read,
            created_at=model.created_at
        )
    
    def send_notification(self, account_id: int, notification_type: str, content: str,
                         created_at: datetime) -> Notification:
        try:
            notif_model = NotificationModel(
                account_id=account_id,
                type=notification_type,
                content=content,
                is_read=False,
                created_at=created_at
            )
            self.session.add(notif_model)
            self.session.commit()
            self.session.refresh(notif_model)
            return self._to_domain(notif_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating notification: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, notification_id: int) -> Optional[Notification]:
        try:
            notif_model = self.session.query(NotificationModel).filter_by(notification_id=notification_id).first()
            return self._to_domain(notif_model) if notif_model else None
        except Exception as e:
            raise ValueError(f'Error getting notification: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_account(self, account_id: int) -> List[Notification]:
        try:
            notif_models = self.session.query(NotificationModel).filter_by(
                account_id=account_id
            ).order_by(NotificationModel.created_at.desc()).all()
            return [self._to_domain(model) for model in notif_models]
        except Exception as e:
            raise ValueError(f'Error getting notifications by account: {str(e)}')
        finally:
            self.session.close()
    
    def get_unread_by_account(self, account_id: int) -> List[Notification]:
        try:
            notif_models = self.session.query(NotificationModel).filter_by(
                account_id=account_id, is_read=False
            ).order_by(NotificationModel.created_at.desc()).all()
            return [self._to_domain(model) for model in notif_models]
        except Exception as e:
            raise ValueError(f'Error getting unread notifications: {str(e)}')
        finally:
            self.session.close()
    
    def get_recent_by_account(self, account_id: int, limit: int) -> List[Notification]:
        try:
            notif_models = self.session.query(NotificationModel).filter_by(
                account_id=account_id
            ).order_by(NotificationModel.created_at.desc()).limit(limit).all()
            return [self._to_domain(model) for model in notif_models]
        except Exception as e:
            raise ValueError(f'Error getting recent notifications: {str(e)}')
        finally:
            self.session.close()
    
    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        try:
            notif_model = self.session.query(NotificationModel).filter_by(notification_id=notification_id).first()
            if not notif_model:
                return None
            notif_model.is_read = True
            self.session.commit()
            self.session.refresh(notif_model)
            return self._to_domain(notif_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking as read: {str(e)}')
        finally:
            self.session.close()
    
    def mark_all_as_read(self, account_id: int) -> bool:
        try:
            self.session.query(NotificationModel).filter_by(
                account_id=account_id, is_read=False
            ).update({NotificationModel.is_read: True})
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error marking all as read: {str(e)}')
        finally:
            self.session.close()
    
    def delete(self, notification_id: int) -> bool:
        try:
            notif_model = self.session.query(NotificationModel).filter_by(notification_id=notification_id).first()
            if not notif_model:
                return False
            self.session.delete(notif_model)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting notification: {str(e)}')
        finally:
            self.session.close()
    
    def delete_all_by_account(self, account_id: int) -> bool:
        try:
            self.session.query(NotificationModel).filter_by(account_id=account_id).delete()
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error deleting all notifications: {str(e)}')
        finally:
            self.session.close()
    
    def count_unread(self, account_id: int) -> int:
        try:
            return self.session.query(NotificationModel).filter_by(account_id=account_id, is_read=False).count()
        except Exception as e:
            raise ValueError(f'Error counting unread notifications: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_type(self, account_id: int, notification_type: str) -> int:
        try:
            return self.session.query(NotificationModel).filter_by(account_id=account_id, type=notification_type).count()
        except Exception as e:
            raise ValueError(f'Error counting notifications by type: {str(e)}')
        finally:
            self.session.close()
