# ------------------------------------------------------------
# 📁 Fichier : app/utils/security.py
# 🎯 Objectif : Fonctions de sécurité, hachage, JWT et dépendances d'authentification
# ------------------------------------------------------------

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Importations absolues pour la robustesse (comme vous l'avez corrigé)
from app.database import get_db
from app import models, schemas # Assurez-vous d'importer schemas

# --- Configuration de Sécurité ---
SECRET_KEY = "super-secret-key-that-should-be-in-env-vars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token expire dans 7 jours

# CHANGEMENT CRITIQUE ICI : Passage de 'bcrypt' à 'pbkdf2_sha256' 
# pour contourner l'AttributeError/ValueError sur votre système Windows.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Schéma OAuth2 pour extraire le token du header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ==========================================================
# 1. FONCTIONS DE HACHAGE ET VÉRIFICATION
# ==========================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe clair correspond au mot de passe haché."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache un mot de passe."""
    return pwd_context.hash(password)

# ==========================================================
# 2. FONCTIONS CRUD DE BASE
# ==========================================================

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Récupère un utilisateur par son email."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Crée un nouvel utilisateur dans la base de données."""
    # Le mot de passe haché doit déjà être défini dans le routeur avant d'appeler cette fonction
    # Le préfixe '$2b$' (bcrypt) ne s'applique plus; on s'assure juste du hachage.
    
    # ⚠️ NOTE IMPORTANTE: Normalement, le hachage doit être fait UNE seule fois dans le routeur 
    # pour éviter de hacher plusieurs fois. Ici, on s'assure que le hachage est fait
    # au cas où la fonction serait appelée directement avec un mot de passe non haché.
    if user.password and not user.password.startswith("$pbkdf2-sha256$"):
        hashed_password = get_password_hash(user.password)
    else:
        # Si le mot de passe semble déjà haché (ou est None)
        hashed_password = user.password

    db_user = models.User(
        email=user.email,
        username=user.username,
        password=hashed_password # Le champ dans le modèle est 'password', qui stocke le hachage
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    """Tente d'authentifier un utilisateur par email et mot de passe."""
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.password):
        return None
    return user

# ==========================================================
# 3. FONCTIONS DE TOKEN JWT
# ==========================================================

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

# ==========================================================
# 4. FONCTIONS DE DÉPENDANCE (AJUSTÉES)
# ==========================================================

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

# Renommée à la convention 'get_current_active_user' pour le routeur /me
def get_current_active_user(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)) -> models.User:
    """Récupère l'objet User à partir du token (authentification obligatoire)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_user_optional(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Optional[models.User]:
    """
    Récupère l'objet User à partir du token.
    Si le token est manquant ou invalide, retourne None (authentification optionnelle).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            return None 
            
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
        
    except (JWTError, AttributeError, HTTPException):
        # On attrape JWTError, AttributeError et HTTPException (levée par Depends(oauth2_scheme)
        # si aucun token n'est fourni) et on retourne None pour l'optionnel.
        return None
