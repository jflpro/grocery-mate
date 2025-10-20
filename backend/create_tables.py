# create_tables.py
# Script pour créer toutes les tables manquantes de Grocery-Mate
# Backend original + relations avec User
# Compatible avec SQLAlchemy et PostgreSQL
# A exécuter dans le dossier backend avec l'environnement virtuel activé

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

# -----------------------------
# Configuration de la connexion
# -----------------------------
# DATABASE_URL pour se connecter à PostgreSQL via Docker
# postgres: utilisateur
# test1234: mot de passe défini pour ton DB
# localhost: machine locale
# 5432: port exposé par le container
# grocery_db: nom de la base
DATABASE_URL = "postgresql://postgres:test1234@localhost:5432/grocery_db"

# Création de l'engine SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)  # echo=True pour afficher le SQL généré

# Session pour manipuler la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour déclarer les modèles
Base = declarative_base()

# -----------------------------
# Modèles (tables)
# -----------------------------

# Table Users
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations avec les autres tables
    ingredients = relationship("Ingredient", back_populates="owner")
    shopping_lists = relationship("ShoppingList", back_populates="owner")
    recipes = relationship("Recipe", back_populates="owner")


# Table Ingredients
class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Float, default=0.0)
    unit = Column(String, default="")
    location = Column(String, default="")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="ingredients")


# Table Shopping Lists
class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="shopping_lists")


# Table Recipes
class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="recipes")


# -----------------------------
# Création des tables
# -----------------------------
def create_all_tables():
    print("Création des tables dans la base PostgreSQL...")
    Base.metadata.create_all(bind=engine)  # Crée toutes les tables si elles n'existent pas
    print("✅ Toutes les tables ont été créées !")


# -----------------------------
# Exécution
# -----------------------------
if __name__ == "__main__":
    create_all_tables()
