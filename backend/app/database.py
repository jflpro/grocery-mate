# ------------------------------------------------------------
# 📁 Fichier : app/database.py
# 🎯 Objectif : Configuration de la base de données PostgreSQL
# ------------------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# --- Configuration de la Base de Données (PostgreSQL) ---

# 🔧 On tente d'abord de récupérer l'URL depuis les variables d'environnement
# Sinon, on utilise une valeur par défaut (utile en développement local)
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    # FIX: La valeur par défaut est mise à jour pour correspondre aux identifiants du Docker Compose
    "postgresql://grocery_user:grocery_pass@localhost:5432/grocery_db" 
)

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
    # Importation locale pour éviter l'erreur d'importation circulaire
    # Assurez-vous d'avoir un fichier `models.py` dans ce répertoire.
    # L'importation doit être faite ici pour s'assurer que tous les modèles 
    # sont enregistrés dans Base.metadata avant d'appeler create_all/drop_all.
    from . import models 

    print("WARNING: Dropping all tables and recreating schema...")
    # 1. Supprime toutes les tables (DROP)
    Base.metadata.drop_all(bind=engine)
    # 2. Crée toutes les tables (CREATE)
    Base.metadata.create_all(bind=engine)
    print("Database schema synchronization complete.")

# --------------------------------------------------------------------------------------
# LIGNE À DÉCOMMENTER POUR L'EXÉCUTION UNIQUE
# Cette ligne est DÉCOMMENTÉE pour créer vos tables !
# --------------------------------------------------------------------------------------
# create_db_tables_and_sync_schema()
