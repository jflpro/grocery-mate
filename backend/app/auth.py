from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# CORRECTION CLÉ : Changé les imports relatifs (..database, ..models)
# en imports absolus (app.database, app.models) pour la robustesse.
from app.database import get_db
from app import models

# --- Configuration de Sécurité ---
# Pour un projet réel, ces variables devraient être chargées depuis des variables d'environnement.
SECRET_KEY = "super-secret-key-that-should-be-in-env-vars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token expire dans 7 jours

# Contexte pour le hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schéma OAuth2 pour extraire le token du header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# --- Fonctions de Hachage et de Vérification ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe clair correspond au mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache un mot de passe."""
    return pwd_context.hash(password)

# --- Fonctions de Token ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crée un jeton d'accès JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Fonctions de Dépendance d'Authentification ---

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Décode le token et retourne l'ID utilisateur, lève une erreur si le token est invalide."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return user_id

async def get_current_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> models.User:
    """Récupère l'objet User à partir du token (authentification obligatoire)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_user_optional(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Optional[models.User]:
    """
    Récupère l'objet User à partir du token.
    Si le token est manquant ou invalide, retourne None (authentification optionnelle).
    """
    try:
        # Tente de décoder le token comme dans get_current_user_id
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            return None # Pas d'ID utilisateur valide dans le payload
            
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
        
    except (JWTError, AttributeError):
        # JWTError: Token invalide, expiré, ou mal formé
        # AttributeError: Peut survenir si 'token' est None ou vide si l'utilisateur ne fournit pas de header d'auth
        return None
