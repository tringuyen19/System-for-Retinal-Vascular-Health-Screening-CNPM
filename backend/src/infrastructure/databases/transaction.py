"""
Transaction Management for Database Operations
Provides context manager for handling database transactions
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


@contextmanager
def transaction(session: Session) -> Generator[Session, None, None]:
    """
    Context manager for database transactions.
    
    Usage:
        with transaction(session):
            # Perform database operations
            repository.add(...)
            repository.update(...)
        # Transaction is automatically committed on success
        # Or rolled back on exception
    
    Args:
        session: SQLAlchemy database session
        
    Yields:
        Session: The same session for use in the context
        
    Raises:
        Exception: Any exception raised in the context will trigger rollback
    """
    try:
        logger.debug("Starting database transaction")
        yield session
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {str(e)}", exc_info=True)
        raise


@contextmanager
def nested_transaction(session: Session) -> Generator[Session, None, None]:
    """
    Context manager for nested transactions (savepoints).
    
    Usage:
        with transaction(session):
            # Outer transaction
            with nested_transaction(session):
                # Inner transaction (savepoint)
                # Can rollback independently
                pass
    
    Args:
        session: SQLAlchemy database session
        
    Yields:
        Session: The same session for use in the context
    """
    try:
        savepoint = session.begin_nested()
        logger.debug("Starting nested transaction (savepoint)")
        yield session
        savepoint.commit()
        logger.debug("Nested transaction committed successfully")
    except Exception as e:
        savepoint.rollback()
        logger.error(f"Nested transaction rolled back due to error: {str(e)}", exc_info=True)
        raise

