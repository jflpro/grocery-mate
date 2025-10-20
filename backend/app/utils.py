import os
from datetime import datetime, timedelta
from typing import Optional, Any

from passlib.context import CryptContext
from jose import jwt, JWTError

# --- Configuration de Sécurité ---

# Clé secrète utilisée pour signer les tokens JWT.
# IMPORTANT: DOIT ÊTRE une chaîne aléatoire et longue stockée dans les variables d'environnement en production.
SECRET_KEY = os.environ.get("SECRET_KEY", "your-super-secret-key-that-should-be-kept-secret") 
ALGORITHM = "HS256" # Algorithme de hachage standard pour JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token valide pendant 7 jours

# Contexte pour le hachage des mots de passe (utilisant bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Gestion des Mots de Passe ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si le mot de passe clair correspond au mot de passe haché.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hache un mot de passe clair.
    """
    return pwd_context.hash(password)


# --- Gestion des Tokens JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT d'accès.
    
    Args:
        data: Les données à encoder dans le payload (par exemple, {'sub': 'user_id'}).
        expires_delta: La durée de validité du token.
    
    Returns:
        Le token JWT encodé sous forme de chaîne.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """
    Décode et valide un token JWT.
    
    Args:
        token: Le token JWT à décoder.
        
    Returns:
        Le payload décodé sous forme de dictionnaire, ou None en cas d'erreur.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # En cas d'erreur (signature invalide, token expiré, etc.)
        print(f"Erreur de décodage JWT: {e}")
        return None
