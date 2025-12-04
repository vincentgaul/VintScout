"""
User Model

This model represents users in the system. Each user can create multiple alerts
and receive notifications when items matching their criteria appear on Vinted.

Key features:
- Email-based authentication
- Password hashing with bcrypt for security
- Optional for self-hosted mode (can run single-user without auth)
- Tracks when user was created and last active
- Relationships to alerts (one user has many alerts)
"""

from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.database import Base


class User(Base):
    """
    User account model for authentication and alert ownership.

    In self-hosted mode, users are optional (can run without authentication).
    In cloud mode, users are required for multi-tenancy.
    """
    __tablename__ = "users"

    # Primary key - UUID for better security (no sequential IDs)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # Email verification

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    # One user can have many alerts
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
