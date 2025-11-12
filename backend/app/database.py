# ------------------------------------------------------------
# 📁 Fichier : app/database.py
# 🎯 Objectif : Configuration de la base de données PostgreSQL
# ------------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# --- Configuration de la Base de Données (PostgreSQL) ---
DB_USER = os.environ.get("DB_USER", "postgres")          # Nom d'utilisateur PostgreSQL
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")  # Mot de passe défini dans docker-compose
DB_NAME = os.environ.get("DB_NAME", "grocery_db")        # Nom de la base
DB_HOST = os.environ.get("DB_HOST", "localhost")         # "localhost" pour venv Windows, "postgres" dans Docker
DB_PORT = os.environ.get("DB_PORT", "5432")              # Port exposé par le container PostgreSQL

# --- Construction de l'URL SQLAlchemy ---
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Création de l'engine SQLAlchemy ---
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# --- Création d'une session pour interagir avec la base ---
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Base de départ pour tous les modèles SQLAlchemy ---
Base = declarative_base()

# --- Dépendance pour FastAPI (get_db) ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FONCTION DE CRÉATION SÉCURISÉE DES TABLES ---
def create_db_tables_if_not_exists():
    """
    Crée toutes les tables qui n'existent pas déjà dans la base.
    NE SUPPRIME PAS les données existantes.
    """
    from . import models  # Import local pour éviter l'import circulaire
    Base.metadata.create_all(bind=engine)
