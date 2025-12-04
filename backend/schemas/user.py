"""
User Pydantic Schemas (Request/Response Validation)

Pydantic schemas define the structure of data coming in (requests) and going out (responses).
They provide automatic validation, serialization, and documentation for the API.

Key concepts:
- BaseModel: The base class for all Pydantic schemas
- Field: Adds validation rules and metadata to fields
- EmailStr: Validates that strings are properly formatted email addresses
- ConfigDict: Configuration for how Pydantic handles the schema

Three schema types:
1. UserCreate: What the client sends when registering (includes password)
2. UserLogin: What the client sends when logging in (email + password)
3. UserResponse: What the API returns (excludes password, includes id/timestamps)
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for user registration.

    This is what the client sends to POST /api/auth/register.
    Password will be hashed before storing in database.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="Plain text password (will be hashed)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class UserLogin(BaseModel):
    """
    Schema for user login.

    This is what the client sends to POST /api/auth/login.
    Backend will verify password hash and return JWT token.
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="Plain text password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class UserResponse(BaseModel):
    """
    Schema for user data in responses.

    This is what the API returns (never includes password).
    Used in:
    - POST /api/auth/register response
    - GET /api/users/me response
    """
    id: str = Field(..., description="User UUID")
    email: str = Field(..., description="User's email address")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    model_config = ConfigDict(
        from_attributes=True,  # Allows converting SQLAlchemy models to Pydantic
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T12:00:00Z",
                "last_login_at": "2024-01-15T08:30:00Z"
            }
        }
    )


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.

    Returned by POST /api/auth/login after successful authentication.
    The access_token is a JWT that must be included in Authorization header
    for protected endpoints.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    user: UserResponse = Field(..., description="User information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2024-01-01T12:00:00Z",
                    "last_login_at": "2024-01-15T08:30:00Z"
                }
            }
        }
    )
