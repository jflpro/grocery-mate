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
    "postgresql://postgres:test1234@localhost:5432/grocery_db"  # ✅ Base grocery_db (et non fridgeapp)
)

# --- Création de l'engine SQLAlchemy ---
# pool_pre_ping=True permet de vérifier que la connexion est toujours active avant chaque requête
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)

# --- Création d'une session pour interagir avec la base ---
# autocommit=False → les changements ne sont validés qu'après un commit()
# autoflush=False → évite d'envoyer automatiquement les changements avant les requêtes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Base de départ pour tous les modèles SQLAlchemy ---
Base = declarative_base()

# --- Dépendance pour FastAPI (get_db) ---
def get_db():
    """
    Fonction utilitaire pour injecter une session de base de données dans les routes FastAPI.
    Elle ouvre une session au début et la ferme automatiquement à la fin de la requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
