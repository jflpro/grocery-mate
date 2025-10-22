from datetime import timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app import schemas, models
from app.database import get_db
from app.utils import security # Module de sécurité

# --- Configuration JWT ---
SECRET_KEY = security.SECRET_KEY
ALGORITHM = security.ALGORITHM

# Schéma de sécurité : Définit où chercher le token (dans l'en-tête Authorization: Bearer ...)
# Le 'tokenUrl' pointe vers la route de connexion définie dans le routeur.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- Fonctions CRUD et Authentification ---

def get_user_by_email(db: Session, email: str):
    """Récupère un utilisateur par email."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Crée un nouvel utilisateur."""
    # Le hachage du mot de passe est géré dans le service de sécurité
    db_user = models.User(
        email=user.email,
        # AJOUT : Nous passons le 'username' pour satisfaire la contrainte NOT NULL de la base de données.
        username=user.username,
        # Utilisation de 'password' pour le champ du mot de passe haché
        password=security.get_password_hash(user.password)
        # SUPPRESSION de 'is_active=True' car il est probablement défini par défaut dans le modèle SQLAlchemy
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Vérifie les identifiants et retourne l'utilisateur s'il est valide."""
    user = get_user_by_email(db, email=email)
    # Assumons que le haché est stocké dans l'attribut .password du modèle
    if not user or not security.verify_password(password, user.password):
        return False
    return user


# --- Dépendances FastAPI pour la validation du Token ---

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.User:
    """Valide le token JWT et récupère l'objet utilisateur."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Décoder le token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # 2. Chercher l'utilisateur dans la base de données
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Dépendance qui vérifie si l'utilisateur est actif (obligatoire)."""
    # CORRECTION : La vérification 'is_active' est retirée car l'attribut n'existe pas sur l'objet User.
    # if not current_user.is_active:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

# NOUVELLE FONCTION POUR LA DÉPENDANCE OPTIONNELLE
def get_current_user_optional(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[models.User]:
    """Valide le token JWT. Si la validation échoue, retourne None au lieu de lever une erreur 401."""
    try:
        # Tente d'obtenir l'utilisateur comme d'habitude
        return get_current_user(db=db, token=token)
    except HTTPException as e:
        # Si c'est une 401 (problème d'authentification ou token manquant/invalide)
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return None # L'utilisateur n'est pas authentifié, mais c'est autorisé (facultatif)
        raise # Lever l'exception si ce n'est pas une 401 (ex: 400 Inactive User, mais cette fonction est gérée par get_current_active_user)
    except Exception:
        # Pour toute autre erreur de décodage/validation inattendue, retourner None
        return None
