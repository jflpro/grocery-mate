from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import os

# Librairies à installer : passlib[argon2], python-jose[cryptography]
from passlib.context import CryptContext
from jose import jwt, JWTError

# --- Configuration Sécurité ---

# Hachage mot de passe : Argon2
PWD_CONTEXT = CryptContext(schemes=["argon2"], deprecated="auto")

# Clé secrète et algorithme JWT
# ✅ IMPORTANT : Stocker la clé en variable d'environnement pour la prod
SECRET_KEY = os.getenv("SECRET_KEY", "VOTRE_SECRET_TRES_FORT_DEVELOPPEMENT") 
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Durée du token d'accès en minutes
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


# --- Fonctions de Hachage ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe fourni correspond au haché stocké."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache un mot de passe pour le stockage en base."""
    return PWD_CONTEXT.hash(password)


# --- Fonctions JWT ---

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT d'accès avec expiration."""
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Claims standard : exp (expiration), iat (issued at)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> Dict[str, Any]:
    """Décode un token JWT et retourne les données. Lève JWTError si invalide."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise e  # À gérer côté auth.py pour lever HTTPException 401
