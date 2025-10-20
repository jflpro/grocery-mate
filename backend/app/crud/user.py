from sqlalchemy.orm import Session
from app import models
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

# NOTE: Ce fichier suppose que votre modèle SQLAlchemy 'User' est dans app.models.

def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Récupère un utilisateur par son adresse e-mail."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Récupère un utilisateur par son nom d'utilisateur (pour la connexion)."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """Récupère un utilisateur par son ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: UserCreate) -> models.User:
    """
    Crée un nouvel utilisateur dans la base de données.
    
    Hache le mot de passe avant l'enregistrement.
    """
    # 1. Hachage du mot de passe
    hashed_password = get_password_hash(user.password)
    
    # 2. Création de l'objet modèle SQLAlchemy
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        # Les autres champs (id, created_at) devraient être gérés automatiquement par la BDD ou le modèle.
    )
    
    # 3. Ajout et persistance
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
