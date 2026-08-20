"""
Database configuration for AI Revenue Recovery Agent.
Uses SQLite for easy local setup (no external DB server needed).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./revenue_recovery.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a DB session per request and closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
