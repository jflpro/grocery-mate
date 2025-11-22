from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app import schemas, models
from app.database import get_db
from app.utils import security

# --- OAuth2 Scheme ---
# ⚠️ DOIT correspondre à /api/auth/token (avec le prefix /api du main.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


# --- CRUD Utilisateur de base ---

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Récupère un utilisateur par email."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Crée un nouvel utilisateur avec mot de passe haché."""
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
    """Vérifie les identifiants et retourne l'utilisateur si valides."""
    user = get_user_by_email(db, email=email)
    if not user or not security.verify_password(password, user.password):
        return None
    return user


# --- Dépendances FastAPI pour la validation JWT ---

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> models.User:
    """Valide le token JWT et retourne l'utilisateur."""
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
    """Retourne l'utilisateur authentifié (pas de champ is_active dans ton modèle)."""
    return current_user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.User]:
    """
    Version "soft" : si le token est invalide => retourne None au lieu de 401.
    Utile pour des routes publiques où l'utilisateur est optionnel.
    """
    try:
        return get_current_user(db=db, token=token)
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None
        raise
    except Exception:
        return None
