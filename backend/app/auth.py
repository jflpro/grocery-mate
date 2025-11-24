from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app import schemas, models
from app.database import get_db
from app.utils import security

# --- OAuth2 Scheme ---
# MUST match /api/auth/token (with the /api prefix added in main.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# -------------------------------------------------------------------
# Basic user CRUD helpers
# -------------------------------------------------------------------


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Return a user by email, or None if not found."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user with a hashed password."""
    db_user = models.User(
        email=user.email,
        username=user.username,
        password=security.get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """
    Verify credentials and return the user if valid, otherwise None.

    NOTE:
        This function only checks email + password.
        Business rules like is_active are enforced at the router level.
    """
    user = get_user_by_email(db, email=email)
    if not user or not security.verify_password(password, user.password):
        return None
    return user


# -------------------------------------------------------------------
# FastAPI dependencies for JWT validation
# -------------------------------------------------------------------


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """
    Validate the JWT access token and return the associated User.

    Raises:
        HTTPException(401) if the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = security.decode_access_token(token)
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Return the currently authenticated user, only if the account is active.

    Raises:
        HTTPException(403) if the user account is deactivated.
    """
    # We now use the is_active field added to the User model
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user


def get_current_admin_user(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    """
    Return the currently authenticated user, only if they are an admin.

    Raises:
        HTTPException(403) if the user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required.",
        )
    return current_user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    """
    "Soft" version of get_current_user.

    If the token is invalid or missing, returns None instead of 401.
    Useful for public endpoints where the user is optional.
    """
    try:
        return get_current_user(db=db, token=token)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise
    except Exception:
        return None
