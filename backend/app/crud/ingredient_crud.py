from sqlalchemy.orm import Session
from .. import models, schemas
from typing import List, Optional

# --- Fonctions de Lecture (READ) ---

def get_user_ingredients(db: Session, user_id: int) -> List[models.Ingredient]:
    """
    Récupère la liste de tous les ingrédients d'un utilisateur donné.
    """
    return db.query(models.Ingredient)\
             .filter(models.Ingredient.user_id == user_id)\
             .order_by(models.Ingredient.expiration_date.asc())\
             .all()

def get_ingredient(db: Session, ingredient_id: int, user_id: int) -> Optional[models.Ingredient]:
    """
    Récupère un ingrédient spécifique par ID, en s'assurant qu'il appartient à l'utilisateur.
    """
    return db.query(models.Ingredient)\
             .filter(models.Ingredient.id == ingredient_id, models.Ingredient.user_id == user_id)\
             .first()

# --- Fonctions de Création (CREATE) ---

def create_ingredient(db: Session, ingredient: schemas.IngredientCreate, user_id: int) -> models.Ingredient:
    """
    Crée un nouvel ingrédient pour l'utilisateur spécifié.
    """
    db_ingredient = models.Ingredient(
        user_id=user_id,
        name=ingredient.name,
        quantity=ingredient.quantity,
        unit=ingredient.unit,
        expiration_date=ingredient.expiration_date,
        is_fresh=ingredient.is_fresh
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

# --- Fonctions de Mise à Jour (UPDATE) ---

def update_ingredient(db: Session, db_ingredient: models.Ingredient, ingredient_update: schemas.IngredientUpdate) -> models.Ingredient:
    """
    Met à jour les attributs d'un ingrédient existant.
    'db_ingredient' doit déjà être une instance de models.Ingredient récupérée et vérifiée.
    """
    update_data = ingredient_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)
        
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

# --- Fonctions de Suppression (DELETE) ---

def delete_ingredient(db: Session, db_ingredient: models.Ingredient):
    """
    Supprime un ingrédient de la base de données.
    'db_ingredient' doit déjà être une instance de models.Ingredient récupérée et vérifiée.
    """
    db.delete(db_ingredient)
    db.commit()
    return {"message": "Ingredient deleted successfully"}
