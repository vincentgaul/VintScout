"""
API Dependencies (Shared Across All Endpoints)

Dependencies are FastAPI's way of injecting common functionality into routes.
Think of them as reusable components that run before your endpoint logic.

Key dependencies:
- get_db(): Provides database session to endpoints
- get_current_user(): Verifies JWT token and returns authenticated user
- get_optional_user(): Same but doesn't fail if no token (for self-hosted mode)

Usage in routes:
    @router.get("/alerts")
    def get_alerts(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
        # db and user are automatically injected
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from backend.database import SessionLocal
from backend.config import settings
from backend.models import User


# Security scheme for JWT (appears in API docs)
security = HTTPBearer(auto_error=False)


def get_db():
    """
    Database session dependency.

    Provides a SQLAlchemy session to endpoints and ensures it's closed after use.
    This is called for every request that needs database access.

    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get authenticated user from JWT token.

    Extracts and validates JWT from Authorization header.
    Returns the authenticated User object or raises 401 Unauthorized.

    Usage:
        @router.get("/profile")
        def get_profile(user: User = Depends(get_current_user)):
            return {"email": user.email}

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 404: If user in token doesn't exist in database
    """
    # Check if authentication is disabled (self-hosted mode)
    if not settings.REQUIRE_AUTH:
        # In self-hosted mode, return a mock user or None
        # For now, we'll require at least one user exists
        return db.query(User).first()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get authenticated user if token is provided, otherwise return None.

    This is useful for endpoints that work differently for authenticated vs anonymous users,
    but don't strictly require authentication.

    Usage:
        @router.get("/public-data")
        def get_data(user: Optional[User] = Depends(get_optional_user)):
            if user:
                # Return personalized data
            else:
                # Return public data

    Returns:
        User object if valid token provided, None otherwise
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
