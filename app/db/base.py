"""
Database models initialization
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config.config import Config

# Create SQLAlchemy engine
engine = create_engine(Config.DATABASE_URL)

# Create session factory
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Create declarative base
Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables"""
    # Import all models to ensure they are registered with the Base
    from app.models.user import User
    from app.models.session import Session
    from app.models.attendance import Attendance
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
