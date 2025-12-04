"""
Database Configuration and Session Management

This file sets up the connection to the database (SQLite or PostgreSQL).
It uses SQLAlchemy, which is a tool that lets Python talk to databases.

Key components:
- engine: The connection to the database
- SessionLocal: Creates database sessions (like opening/closing a file)
- Base: The parent class for all database models (tables)
- get_db(): A function that gives each API request its own database session

Think of this as the "phone line" between our Python code and the database.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """
    Database session dependency for FastAPI routes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
