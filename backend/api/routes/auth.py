"""
Authentication API Routes

Handles user registration, login, and token management.

Endpoints:
- POST /api/auth/register - Create new user account
- POST /api/auth/login - Authenticate and get JWT token
- GET /api/auth/me - Get current user info (requires auth)

Security:
- Passwords are hashed with bcrypt before storage
- JWT tokens expire after JWT_EXPIRATION_HOURS (from settings)
- Tokens include user ID in "sub" claim
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from backend.api.dependencies import get_db, get_current_user
from backend.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from backend.models import User
from backend.config import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: User UUID

    Returns:
        JWT token string

    Token payload:
        - sub: User ID
        - exp: Expiration timestamp
        - iat: Issued at timestamp
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user with hashed password and returns JWT token.
    Email must be unique (not already registered).

    Request body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }

    Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "user": {
                "id": "550e8400-...",
                "email": "user@example.com",
                "is_active": true,
                "is_verified": false,
                "created_at": "2024-01-01T12:00:00Z",
                "last_login_at": null
            }
        }

    Raises:
        409 Conflict: If email is already registered
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(new_user.id)

    # Return token and user info
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and get JWT token.

    Validates email/password and returns JWT token if valid.
    Updates last_login_at timestamp on successful login.

    Request body:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }

    Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "user": {
                "id": "550e8400-...",
                "email": "user@example.com",
                "is_active": true,
                "is_verified": false,
                "created_at": "2024-01-01T12:00:00Z",
                "last_login_at": "2024-01-15T08:30:00Z"
            }
        }

    Raises:
        401 Unauthorized: If email not found or password is incorrect
        403 Forbidden: If user account is inactive
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Generate JWT token
    access_token = create_access_token(user.id)

    # Return token and user info
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.

    Headers:
        Authorization: Bearer <token>

    Response:
        {
            "id": "550e8400-...",
            "email": "user@example.com",
            "is_active": true,
            "is_verified": false,
            "created_at": "2024-01-01T12:00:00Z",
            "last_login_at": "2024-01-15T08:30:00Z"
        }

    Raises:
        401 Unauthorized: If token is missing or invalid
    """
    return UserResponse.model_validate(user)
