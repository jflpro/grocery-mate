from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict

# Assurez-vous d'avoir installé 'passlib[bcrypt]' ou 'passlib[argon2]' et 'python-jose[cryptography]'
from passlib.context import CryptContext
from jose import jwt, JWTError

# --- Configuration (à adapter ou à externaliser) ---
# Schéma de hachage par défaut. Argon2 est plus robuste que bcrypt.
PWD_CONTEXT = CryptContext(schemes=["argon2"], deprecated="auto")

# Clé secrète et algorithme pour les tokens JWT
# IMPORTANT: Remplacez cette clé par une chaîne très longue et aléatoire dans une variable d'environnement
SECRET_KEY = "VOTRE_SECRET_TRES_FORT_ET_ALÉATOIRE_ICI_NE_PAS_UTILISER_EN_PROD"
ALGORITHM = "HS256"
# Durée de validité du token d'accès (ex: 30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30 
# Durée de validité du token de rafraîchissement (non utilisé ici, mais bonne pratique)
# REFRESH_TOKEN_EXPIRE_DAYS = 7 


# --- Fonctions de Hachage de Mot de Passe ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe clair correspond au hachage stocké."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hache un mot de passe pour le stockage dans la base de données."""
    return PWD_CONTEXT.hash(password)


# --- Fonctions de Token JWT ---

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT d'accès."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Valeur par défaut si non spécifiée
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajoute les claims standard 'exp' (expiration) et 'sub' (subject - ici l'ID utilisateur)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Remarque: Les fonctions de vérification et de décodage sont souvent dans auth.py, 
# mais la création du token est la responsabilité du module de sécurité.
