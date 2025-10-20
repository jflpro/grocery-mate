from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app.schemas import schemas as s

# ====================================================================
# AVERTISSEMENT : Les fonctions CRUD pour l'utilisateur (create_user, get_user_by_email, etc.) 
# devraient résider dans un fichier 'app/crud/user.py' ou similaire, 
# mais pour la simplicité, nous les laissons dans 'user.py' (implicite) ou 'auth.py' (déjà traité).
# Ces fonctions se concentrent sur la gestion de la cuisine.
# ====================================================================

# --------------------------------------------------------------------
# 1. CRUD pour les INGRÉDIENTS (Inventory)
# --------------------------------------------------------------------

def get_ingredient(db: Session, ingredient_id: int, user_id: int) -> Optional[models.Ingredient]:
    """Récupère un ingrédient spécifique appartenant à l'utilisateur donné."""
    return db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id, 
        models.Ingredient.user_id == user_id
    ).first()

def get_ingredients(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Ingredient]:
    """Récupère la liste des ingrédients d'un utilisateur, paginée."""
    return db.query(models.Ingredient).filter(
        models.Ingredient.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_ingredient(db: Session, ingredient: s.IngredientCreate, user_id: int) -> models.Ingredient:
    """Crée un nouvel ingrédient pour l'utilisateur spécifié."""
    db_ingredient = models.Ingredient(**ingredient.model_dump(), user_id=user_id)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def update_ingredient(db: Session, db_ingredient: models.Ingredient, ingredient_update: s.IngredientUpdate) -> models.Ingredient:
    """Met à jour les champs d'un ingrédient existant."""
    update_data = ingredient_update.model_dump(exclude_unset=True) # Ignore les champs None/non définis

    for key, value in update_data.items():
        setattr(db_ingredient, key, value)
    
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def delete_ingredient(db: Session, db_ingredient: models.Ingredient) -> models.Ingredient:
    """Supprime un ingrédient de la base de données."""
    db.delete(db_ingredient)
    db.commit()
    return db_ingredient


# --------------------------------------------------------------------
# 2. CRUD pour les RECETTES (Recipe)
# --------------------------------------------------------------------

def get_recipe(db: Session, recipe_id: int, user_id: int) -> Optional[models.Recipe]:
    """Récupère une recette spécifique appartenant à l'utilisateur donné."""
    return db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id, 
        models.Recipe.user_id == user_id
    ).first()

def get_recipes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Recipe]:
    """Récupère la liste des recettes d'un utilisateur, paginée."""
    return db.query(models.Recipe).filter(
        models.Recipe.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_recipe(db: Session, recipe: s.RecipeCreate, user_id: int) -> models.Recipe:
    """Crée une nouvelle recette pour l'utilisateur spécifié."""
    db_recipe = models.Recipe(**recipe.model_dump(), user_id=user_id)
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def update_recipe(db: Session, db_recipe: models.Recipe, recipe_update: s.RecipeUpdate) -> models.Recipe:
    """Met à jour les champs d'une recette existante."""
    update_data = recipe_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_recipe, key, value)
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, db_recipe: models.Recipe) -> models.Recipe:
    """Supprime une recette de la base de données."""
    db.delete(db_recipe)
    db.commit()
    return db_recipe


# --------------------------------------------------------------------
# 3. CRUD pour les LISTES DE COURSES (ShoppingList & ShoppingItem)
# --------------------------------------------------------------------

# --- ShoppingList ---

def get_shopping_list(db: Session, list_id: int, user_id: int) -> Optional[models.ShoppingList]:
    """Récupère une liste de courses spécifique appartenant à l'utilisateur."""
    # Utilise .options(joinedload(models.ShoppingList.items)) si la relation n'est pas chargée par défaut
    return db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id, 
        models.ShoppingList.user_id == user_id
    ).first()

def get_shopping_lists(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.ShoppingList]:
    """Récupère toutes les listes de courses d'un utilisateur, paginées."""
    return db.query(models.ShoppingList).filter(
        models.ShoppingList.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_shopping_list(db: Session, list_data: s.ShoppingListCreate, user_id: int) -> models.ShoppingList:
    """Crée une nouvelle liste de courses."""
    # Création de l'objet List (sans les items pour l'instant)
    db_list = models.ShoppingList(name=list_data.name, user_id=user_id)
    db.add(db_list)
    db.flush() # Force l'attribution de l'ID avant d'ajouter les items

    # Ajout des items s'ils sont fournis
    for item_data in list_data.items:
        db_item = models.ShoppingItem(**item_data.model_dump(), shopping_list_id=db_list.id)
        db.add(db_item)

    db.commit()
    db.refresh(db_list)
    return db_list

def delete_shopping_list(db: Session, db_list: models.ShoppingList) -> models.ShoppingList:
    """Supprime une liste de courses (et ses items grâce au cascade="all, delete-orphan")."""
    db.delete(db_list)
    db.commit()
    return db_list

# --- ShoppingItem ---

def get_shopping_item(db: Session, item_id: int, list_id: int) -> Optional[models.ShoppingItem]:
    """Récupère un élément de liste spécifique dans la liste donnée."""
    return db.query(models.ShoppingItem).filter(
        models.ShoppingItem.id == item_id,
        models.ShoppingItem.shopping_list_id == list_id
    ).first()

def add_shopping_item(db: Session, item_data: s.ShoppingItemCreate, list_id: int) -> models.ShoppingItem:
    """Ajoute un élément à une liste de courses existante."""
    db_item = models.ShoppingItem(**item_data.model_dump(), shopping_list_id=list_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_shopping_item(db: Session, db_item: models.ShoppingItem, update_data: s.ShoppingItemBase) -> models.ShoppingItem:
    """Met à jour un élément de liste de courses."""
    # Utilise le schéma de base pour la mise à jour des champs
    data_to_update = update_data.model_dump(exclude_unset=True)

    for key, value in data_to_update.items():
        setattr(db_item, key, value)
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def toggle_shopping_item_purchased(db: Session, db_item: models.ShoppingItem, is_purchased: bool) -> models.ShoppingItem:
    """Change l'état 'is_purchased' d'un élément."""
    db_item.is_purchased = is_purchased
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_shopping_item(db: Session, db_item: models.ShoppingItem) -> models.ShoppingItem:
    """Supprime un élément de liste de courses."""
    db.delete(db_item)
    db.commit()
    return db_item
