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

def init_mssql(app):
    try:
        print(f">>> Starting table creation...")
        print(f">>> Found {len(Base.metadata.tables)} tables to create:")
        for table_name in Base.metadata.tables.keys():
            print(f"    - {table_name}")
        
        Base.metadata.create_all(bind=engine)
        print(f">>> Tables created successfully!")
    except Exception as e:
        print(f"!!! Error creating tables: {e}")
        raise