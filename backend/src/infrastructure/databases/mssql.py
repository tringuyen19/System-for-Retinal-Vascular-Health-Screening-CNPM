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


def _migrate_clinic_fr22():
    """FR-22: Add organization verification fields to clinics table."""
    from sqlalchemy import text
    with engine.connect() as conn:
        dialect = engine.dialect.name
        table_name = 'clinics'
        
        # Columns to add
        columns_to_add = [
            ('license_number', 'NVARCHAR(100)' if dialect != 'sqlite' else 'VARCHAR(100)'),
            ('tax_id', 'NVARCHAR(50)' if dialect != 'sqlite' else 'VARCHAR(50)'),
            ('verification_documents', 'NTEXT' if dialect != 'sqlite' else 'TEXT'),
            ('manager_email', 'NVARCHAR(255)' if dialect != 'sqlite' else 'VARCHAR(255)')
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                if dialect == 'sqlite':
                    conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}'))
                else:
                    # For MSSQL, check if column exists first
                    check_sql = f"""
                    IF NOT EXISTS (SELECT * FROM sys.columns 
                                   WHERE object_id = OBJECT_ID(N'[dbo].[{table_name}]') 
                                   AND name = '{col_name}')
                    BEGIN
                        ALTER TABLE [dbo].[{table_name}] ADD [{col_name}] {col_type} NULL;
                    END
                    """
                    conn.execute(text(check_sql))
                conn.commit()
                print(f">>> Migrated: {table_name}.{col_name}")
            except Exception as e:
                error_msg = str(e).lower()
                if 'duplicate' in error_msg or 'already exists' in error_msg or 'column name' in error_msg or 'invalid column name' in error_msg:
                    print(f">>> Column {table_name}.{col_name} already exists or error (safe to ignore): {e}")
                else:
                    print(f">>> Migration error for {table_name}.{col_name}: {e}")
        
        # Make logo_url nullable if it's not already (MSSQL only)
        try:
            if dialect != 'sqlite':
                update_sql = f"""
                IF EXISTS (SELECT * FROM sys.columns 
                          WHERE object_id = OBJECT_ID(N'[dbo].[{table_name}]') 
                          AND name = 'logo_url' AND is_nullable = 0)
                BEGIN
                    ALTER TABLE [dbo].[{table_name}] ALTER COLUMN [logo_url] NVARCHAR(255) NULL;
                END
                """
                conn.execute(text(update_sql))
                conn.commit()
                print(f">>> Updated {table_name}.logo_url to be nullable (if needed)")
        except Exception as e:
            print(f">>> Could not update logo_url nullable: {e}")


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


def _migrate_service_packages_fr34():
    """FR-34: Add package_type and is_active to service_packages table, and backfill existing rows."""
    from sqlalchemy import text
    with engine.connect() as conn:
        dialect = engine.dialect.name
        table_name = 'service_packages'
        # Add columns if missing
        try:
            if dialect == 'sqlite':
                # SQLite: best-effort add columns
                try:
                    conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN package_type VARCHAR(20)'))
                except Exception:
                    pass
                try:
                    conn.execute(text(f'ALTER TABLE {table_name} ADD COLUMN is_active INTEGER'))
                except Exception:
                    pass
                conn.commit()
            else:
                # MSSQL: conditional add
                conn.execute(text(f"""
                IF NOT EXISTS (SELECT * FROM sys.columns 
                               WHERE object_id = OBJECT_ID(N'[dbo].[{table_name}]') 
                               AND name = 'package_type')
                BEGIN
                    ALTER TABLE [dbo].[{table_name}] ADD [package_type] NVARCHAR(20) NULL;
                END
                """))
                conn.execute(text(f"""
                IF NOT EXISTS (SELECT * FROM sys.columns 
                               WHERE object_id = OBJECT_ID(N'[dbo].[{table_name}]') 
                               AND name = 'is_active')
                BEGIN
                    ALTER TABLE [dbo].[{table_name}] ADD [is_active] BIT NULL;
                END
                """))
                conn.commit()
            print(f">>> Migrated: {table_name}.package_type, {table_name}.is_active (if needed)")
        except Exception as e:
            print(f">>> Migration error for {table_name} FR-34: {e}")

        # Backfill defaults for existing rows
        try:
            if dialect == 'sqlite':
                conn.execute(text(f"UPDATE {table_name} SET is_active = 1 WHERE is_active IS NULL"))
                conn.execute(text(f"UPDATE {table_name} SET package_type = 'patient' WHERE package_type IS NULL AND package_id <= 5"))
                conn.execute(text(f"UPDATE {table_name} SET package_type = 'clinic' WHERE package_type IS NULL AND package_id > 5"))
            else:
                conn.execute(text(f"UPDATE [dbo].[{table_name}] SET is_active = 1 WHERE is_active IS NULL"))
                conn.execute(text(f"UPDATE [dbo].[{table_name}] SET package_type = 'patient' WHERE package_type IS NULL AND package_id <= 5"))
                conn.execute(text(f"UPDATE [dbo].[{table_name}] SET package_type = 'clinic' WHERE package_type IS NULL AND package_id > 5"))
            conn.commit()
            print(f">>> Backfilled: {table_name} FR-34 defaults")
        except Exception as e:
            print(f">>> Backfill skip {table_name} FR-34: {e}")


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
        _migrate_clinic_fr22()
        _migrate_service_packages_fr34()
    except Exception as e:
        print(f"!!! Error creating tables: {e}")
        raise