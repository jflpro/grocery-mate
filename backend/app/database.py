# ------------------------------------------------------------
# 📁 Fichier : app/database.py
# 🎯 Objectif : Configuration de la base de données PostgreSQL
# ------------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# --- Configuration de la Base de Données (PostgreSQL) ---

# 🔧 Récupération des variables d'environnement si disponibles
DB_USER = os.environ.get("DB_USER", "grocery_user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "grocery_pass")
DB_NAME = os.environ.get("DB_NAME", "grocery_db")
DB_HOST = os.environ.get("DB_HOST", "postgres")  # "localhost" pour venv, "postgres" dans Docker
DB_PORT = os.environ.get("DB_PORT", "5432")

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
    """
    Fonction utilitaire pour injecter une session de base de données dans les routes FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FONCTION DE CRÉATION DE TABLES (À EXÉCUTER UNE FOIS SEULEMENT) ---
def create_db_tables_and_sync_schema():
    """
    Supprime toutes les tables puis les recrée.

    ATTENTION : Cette fonction EFFACE toutes vos données existantes.
    """
    from . import models  # Import local pour éviter l'import circulaire

    print("WARNING: Dropping all tables and recreating schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database schema synchronization complete.")

# --------------------------------------------------------------------------------------
# DÉCOMMENTER POUR CRÉER LES TABLES (une seule fois)
# --------------------------------------------------------------------------------------
# create_db_tables_and_sync_schema()
