from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from infrastructure.databases.mssql import session
from infrastructure.models.audit_log_model import AuditLogModel
from domain.models.audit_log import AuditLog
from domain.models.iaudit_log_repository import IAuditLogRepository


class AuditLogRepository(IAuditLogRepository):
    """Repository implementation for Audit Log - Infrastructure layer"""
    
    def __init__(self, db_session: Session = session):
        self.session = db_session
    
    def _to_domain(self, model: AuditLogModel) -> AuditLog:
        """Convert AuditLogModel (Infrastructure) to AuditLog (Domain)"""
        return AuditLog(
            audit_log_id=model.audit_log_id,
            account_id=model.account_id,
            action_type=model.action_type,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            old_values=model.old_values,
            new_values=model.new_values,
            description=model.description,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            created_at=model.created_at
        )
    
    def create_log(self, account_id: Optional[int], action_type: str, entity_type: str,
                   entity_id: Optional[int], old_values: Optional[str],
                   new_values: Optional[str], description: Optional[str],
                   ip_address: Optional[str], user_agent: Optional[str],
                   created_at: datetime) -> AuditLog:
        """Create a new audit log entry"""
        try:
            audit_log_model = AuditLogModel(
                account_id=account_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=created_at or datetime.now()
            )
            self.session.add(audit_log_model)
            self.session.commit()
            self.session.refresh(audit_log_model)
            return self._to_domain(audit_log_model)
        except Exception as e:
            self.session.rollback()
            raise ValueError(f'Error creating audit log: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_id(self, audit_log_id: int) -> Optional[AuditLog]:
        """Get audit log by ID"""
        try:
            model = self.session.query(AuditLogModel).filter_by(
                audit_log_id=audit_log_id
            ).first()
            return self._to_domain(model) if model else None
        except Exception as e:
            raise ValueError(f'Error getting audit log: {str(e)}')
        finally:
            self.session.close()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get all audit logs with optional pagination"""
        try:
            query = self.session.query(AuditLogModel).order_by(
                AuditLogModel.created_at.desc()
            )
            if limit:
                query = query.limit(limit).offset(offset)
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting all audit logs: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_account(self, account_id: int, limit: Optional[int] = None,
                   offset: int = 0) -> List[AuditLog]:
        """Get audit logs by account ID"""
        try:
            query = self.session.query(AuditLogModel).filter_by(
                account_id=account_id
            ).order_by(AuditLogModel.created_at.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting audit logs by account: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_action_type(self, action_type: str, limit: Optional[int] = None,
                          offset: int = 0) -> List[AuditLog]:
        """Get audit logs by action type"""
        try:
            query = self.session.query(AuditLogModel).filter_by(
                action_type=action_type
            ).order_by(AuditLogModel.created_at.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting audit logs by action type: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_entity_type(self, entity_type: str, limit: Optional[int] = None,
                          offset: int = 0) -> List[AuditLog]:
        """Get audit logs by entity type"""
        try:
            query = self.session.query(AuditLogModel).filter_by(
                entity_type=entity_type
            ).order_by(AuditLogModel.created_at.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting audit logs by entity type: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_entity(self, entity_type: str, entity_id: int,
                     limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get audit logs for a specific entity"""
        try:
            query = self.session.query(AuditLogModel).filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            ).order_by(AuditLogModel.created_at.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting audit logs by entity: {str(e)}')
        finally:
            self.session.close()
    
    def get_by_date_range(self, start_date: date, end_date: date,
                         limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Get audit logs within date range"""
        try:
            query = self.session.query(AuditLogModel).filter(
                and_(
                    AuditLogModel.created_at >= datetime.combine(start_date, datetime.min.time()),
                    AuditLogModel.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            ).order_by(AuditLogModel.created_at.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error getting audit logs by date range: {str(e)}')
        finally:
            self.session.close()
    
    def search(self, account_id: Optional[int] = None, action_type: Optional[str] = None,
              entity_type: Optional[str] = None, entity_id: Optional[int] = None,
              start_date: Optional[date] = None, end_date: Optional[date] = None,
              limit: Optional[int] = None, offset: int = 0) -> List[AuditLog]:
        """Search audit logs with multiple filters"""
        try:
            query = self.session.query(AuditLogModel)
            
            # Apply filters
            if account_id is not None:
                query = query.filter_by(account_id=account_id)
            if action_type:
                query = query.filter_by(action_type=action_type)
            if entity_type:
                query = query.filter_by(entity_type=entity_type)
            if entity_id is not None:
                query = query.filter_by(entity_id=entity_id)
            if start_date:
                query = query.filter(
                    AuditLogModel.created_at >= datetime.combine(start_date, datetime.min.time())
                )
            if end_date:
                query = query.filter(
                    AuditLogModel.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            
            # Order and paginate
            query = query.order_by(AuditLogModel.created_at.desc())
            if limit:
                query = query.limit(limit).offset(offset)
            
            models = query.all()
            return [self._to_domain(model) for model in models]
        except Exception as e:
            raise ValueError(f'Error searching audit logs: {str(e)}')
        finally:
            self.session.close()
    
    def count(self) -> int:
        """Get total count of audit logs"""
        try:
            return self.session.query(AuditLogModel).count()
        except Exception as e:
            raise ValueError(f'Error counting audit logs: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_action_type(self, action_type: str) -> int:
        """Count audit logs by action type"""
        try:
            return self.session.query(AuditLogModel).filter_by(action_type=action_type).count()
        except Exception as e:
            raise ValueError(f'Error counting audit logs by action type: {str(e)}')
        finally:
            self.session.close()
    
    def count_by_entity_type(self, entity_type: str) -> int:
        """Count audit logs by entity type"""
        try:
            return self.session.query(AuditLogModel).filter_by(entity_type=entity_type).count()
        except Exception as e:
            raise ValueError(f'Error counting audit logs by entity type: {str(e)}')
        finally:
            self.session.close()
    
    def get_statistics(self) -> dict:
        """Get audit log statistics"""
        try:
            total = self.count()
            
            # Count by action type
            action_types = ['create', 'update', 'delete', 'approve', 'suspend', 'login', 'logout']
            action_counts = {}
            for action in action_types:
                action_counts[action] = self.count_by_action_type(action)
            
            # Count by entity type
            entity_types = ['account', 'clinic', 'patient', 'doctor', 'ai_config', 'subscription']
            entity_counts = {}
            for entity in entity_types:
                entity_counts[entity] = self.count_by_entity_type(entity)
            
            # Get recent activity (last 7 days)
            from datetime import timedelta
            seven_days_ago = (datetime.now() - timedelta(days=7)).date()
            today = datetime.now().date()
            recent_logs = self.get_by_date_range(seven_days_ago, today)
            recent_count = len(recent_logs)
            
            return {
                'total_logs': total,
                'action_type_distribution': action_counts,
                'entity_type_distribution': entity_counts,
                'recent_activity_7_days': recent_count
            }
        except Exception as e:
            raise ValueError(f'Error getting audit log statistics: {str(e)}')
        finally:
            self.session.close()