from sqlalchemy.orm import Session
from sqlalchemy import select, delete, func, and_
from typing import List, Optional

from . import models, schemas
from .utils import get_password_hash

# --- CRUDS GÉNÉRAUX ---

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Récupère un utilisateur par son adresse e-mail."""
    return db.scalars(select(models.User).filter(models.User.email == email)).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Récupère un utilisateur par son nom d'utilisateur."""
    return db.scalars(select(models.User).filter(models.User.username == username)).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Crée un nouvel utilisateur en hachant le mot de passe."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- CRUD INGRÉDIENTS (INVENTAIRE PERSONNEL) ---

def create_user_ingredient(db: Session, ingredient: schemas.IngredientCreate, user_id: int) -> models.Ingredient:
    """Ajoute un ingrédient à l'inventaire d'un utilisateur."""
    db_ingredient = models.Ingredient(**ingredient.model_dump(), owner_id=user_id)
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def get_user_ingredients(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Ingredient]:
    """Récupère tous les ingrédients d'un utilisateur."""
    return db.scalars(
        select(models.Ingredient)
        .filter(models.Ingredient.owner_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()

def get_user_ingredient(db: Session, ingredient_id: int, user_id: int) -> Optional[models.Ingredient]:
    """Récupère un ingrédient spécifique d'un utilisateur."""
    return db.scalars(
        select(models.Ingredient)
        .filter(models.Ingredient.id == ingredient_id, models.Ingredient.owner_id == user_id)
    ).first()

def update_user_ingredient(db: Session, db_ingredient: models.Ingredient, ingredient: schemas.IngredientUpdate) -> models.Ingredient:
    """Met à jour un ingrédient existant."""
    update_data = ingredient.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)
    
    db_ingredient.updated_at = func.now() # Met à jour le timestamp
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

def delete_user_ingredient(db: Session, db_ingredient: models.Ingredient):
    """Supprime un ingrédient de l'inventaire."""
    db.delete(db_ingredient)
    db.commit()

# --- CRUD RECETTES ---

def create_user_recipe(db: Session, recipe: schemas.RecipeCreate, user_id: int) -> models.Recipe:
    """Crée une nouvelle recette (et ses ingrédients requis) pour un utilisateur."""
    
    # 1. Créer la recette de base
    recipe_data = recipe.model_dump(exclude={"required_ingredients"})
    db_recipe = models.Recipe(**recipe_data, owner_id=user_id)
    db.add(db_recipe)
    db.flush() # Flush pour obtenir l'ID de la recette avant de créer les ingrédients associés

    # 2. Créer les ingrédients requis pour cette recette
    for req_ing in recipe.required_ingredients:
        db_req_ing = models.RecipeIngredient(**req_ing.model_dump(), recipe_id=db_recipe.id)
        db.add(db_req_ing)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[models.Recipe]:
    """Récupère une recette par son ID."""
    return db.scalars(select(models.Recipe).filter(models.Recipe.id == recipe_id)).first()

def get_public_and_owner_recipes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Recipe]:
    """Récupère les recettes publiques ET les recettes privées de l'utilisateur."""
    return db.scalars(
        select(models.Recipe)
        .filter(models.Recipe.is_public == True or models.Recipe.owner_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(models.Recipe.created_at.desc())
    ).all()

def update_recipe(db: Session, db_recipe: models.Recipe, recipe: schemas.RecipeUpdate) -> models.Recipe:
    """Met à jour une recette existante."""
    update_data = recipe.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_recipe, key, value)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, db_recipe: models.Recipe):
    """Supprime une recette (les ingrédients requis associés sont supprimés en cascade)."""
    db.delete(db_recipe)
    db.commit()


# --- CRUD LISTES DE COURSES ---

def create_shopping_list(db: Session, list_data: schemas.ShoppingListCreate, user_id: int) -> models.ShoppingList:
    """Crée une nouvelle liste de courses."""
    db_list = models.ShoppingList(**list_data.model_dump(), owner_id=user_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

def get_user_shopping_lists(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.ShoppingList]:
    """Récupère toutes les listes de courses d'un utilisateur."""
    return db.scalars(
        select(models.ShoppingList)
        .filter(models.ShoppingList.owner_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()

def get_shopping_list_by_id(db: Session, list_id: int, user_id: int) -> Optional[models.ShoppingList]:
    """Récupère une liste de courses spécifique par ID et utilisateur."""
    return db.scalars(
        select(models.ShoppingList)
        .filter(models.ShoppingList.id == list_id, models.ShoppingList.owner_id == user_id)
    ).first()

def delete_shopping_list(db: Session, db_list: models.ShoppingList):
    """Supprime une liste de courses (et ses items en cascade)."""
    db.delete(db_list)
    db.commit()

# --- CRUD ITEMS DE LISTE DE COURSES ---

def create_shopping_item(db: Session, item: schemas.ShoppingItemCreate, list_id: int) -> models.ShoppingItem:
    """Ajoute un item à une liste de courses."""
    db_item = models.ShoppingItem(**item.model_dump(), shopping_list_id=list_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_shopping_item_by_id(db: Session, item_id: int) -> Optional[models.ShoppingItem]:
    """Récupère un item de liste de courses par son ID."""
    return db.scalars(select(models.ShoppingItem).filter(models.ShoppingItem.id == item_id)).first()

def update_shopping_item(db: Session, db_item: models.ShoppingItem, update_data: schemas.ShoppingItemUpdate) -> models.ShoppingItem:
    """Met à jour un item de liste de courses."""
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_shopping_item(db: Session, db_item: models.ShoppingItem):
    """Supprime un item d'une liste de courses."""
    db.delete(db_item)
    db.commit()


# --- LOGIQUE D'INVENTAIRE SPÉCIFIQUE (Le cœur de l'application) ---

def check_inventory_for_recipe(db: Session, recipe_id: int, user_id: int) -> schemas.InventoryCheckResponse:
    """
    Vérifie l'inventaire de l'utilisateur contre les ingrédients requis par une recette.
    Retourne la liste des ingrédients manquants et disponibles.
    """
    
    # 1. Récupérer les ingrédients requis par la recette
    required_ingredients = db.scalars(
        select(models.RecipeIngredient).filter(models.RecipeIngredient.recipe_id == recipe_id)
    ).all()

    # 2. Récupérer l'inventaire de l'utilisateur
    user_inventory = db.scalars(
        select(models.Ingredient).filter(models.Ingredient.owner_id == user_id)
    ).all()

    # Mappe l'inventaire par (nom, unité) pour un accès facile
    inventory_map = {}
    for item in user_inventory:
        key = (item.name.lower(), item.unit.lower())
        inventory_map[key] = inventory_map.get(key, 0) + item.quantity

    missing_items = []
    available_items = []
    can_make = True

    # 3. Comparer les requis avec l'inventaire
    for required in required_ingredients:
        req_key = (required.name.lower(), required.unit.lower())
        
        # NOTE: Cette logique simplifiée suppose que les unités sont directement comparables (pas de conversion d'unités).
        
        available_quantity = inventory_map.get(req_key, 0)
        required_quantity = required.quantity
        
        if available_quantity < required_quantity:
            can_make = False
            missing_items.append({
                "name": required.name,
                "required": required_quantity,
                "available": available_quantity,
                "unit": required.unit
            })
        else:
            available_items.append({
                "name": required.name,
                "needed": required_quantity,
                "available": available_quantity,
                "unit": required.unit
            })

    # 4. Construire et retourner la réponse
    return schemas.InventoryCheckResponse(
        recipe_id=recipe_id,
        can_make=can_make,
        missing_items=missing_items,
        available_items=available_items
    )
