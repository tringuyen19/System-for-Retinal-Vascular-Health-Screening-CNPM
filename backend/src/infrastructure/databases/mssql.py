from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config
from infrastructure.databases.base import Base

# Database configuration
DATABASE_URI = Config.DATABASE_URI
print(f">>> Connecting to database: {DATABASE_URI}")

engine = create_engine(DATABASE_URI, echo=True)  # echo=True để xem SQL queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# IMPORTANT: use scoped_session to avoid sharing one Session across threads/requests
# Many repositories import `session` from here. Using scoped_session makes it thread-local.
session = scoped_session(SessionLocal)

def _migrate_doctor_review_fr19():
    """FR-19: Add ai_accuracy_feedback to doctor_reviews for AI improvement feedback."""
    from sqlalchemy import text
    with engine.connect() as conn:
        dialect = engine.dialect.name
        table_name = 'doctor_reviews'
        col_name = 'ai_accuracy_feedback'
        col_type = 'VARCHAR(30)' if dialect == 'sqlite' else 'NVARCHAR(30)'
        try:
            if dialect == 'sqlite':
                conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}'))
            else:
                conn.execute(text(f'ALTER TABLE {table_name} ADD {col_name} {col_type} NULL'))
            conn.commit()
            print(f">>> Migrated: {table_name}.{col_name}")
        except Exception as e:
            if 'duplicate' in str(e).lower() or 'already exists' in str(e).lower():
                pass
            else:
                print(f">>> Migration skip {table_name}.{col_name}: {e}")


def _migrate_medical_report_fr16():
    """FR-16: Add medical_notes, diagnosis, treatment_recommendations to medical_reports if missing."""
    from sqlalchemy import text
    with engine.connect() as conn:
        # Detect dialect (sqlite vs mssql)
        dialect = engine.dialect.name
        table_name = 'medical_reports'
        columns_to_add = [
            ('medical_notes', 'TEXT' if dialect == 'sqlite' else 'NVARCHAR(MAX)'),
            ('diagnosis', 'TEXT' if dialect == 'sqlite' else 'NVARCHAR(MAX)'),
            ('treatment_recommendations', 'TEXT' if dialect == 'sqlite' else 'NVARCHAR(MAX)'),
        ]
        for col_name, col_type in columns_to_add:
            try:
                if dialect == 'sqlite':
                    conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}'))
                else:
                    conn.execute(text(f'ALTER TABLE {table_name} ADD {col_name} {col_type} NULL'))
                conn.commit()
                print(f">>> Migrated: {table_name}.{col_name}")
            except Exception as e:
                if 'duplicate' in str(e).lower() or 'already exists' in str(e).lower():
                    pass  # column already exists
                else:
                    print(f">>> Migration skip {table_name}.{col_name}: {e}")


def init_mssql(app):
    try:
        print(f">>> Starting table creation...")
        print(f">>> Found {len(Base.metadata.tables)} tables to create:")
        for table_name in Base.metadata.tables.keys():
            print(f"    - {table_name}")
        
        Base.metadata.create_all(bind=engine)
        print(f">>> Tables created successfully!")
        _migrate_medical_report_fr16()
        _migrate_doctor_review_fr19()
    except Exception as e:
        print(f"!!! Error creating tables: {e}")
        raise