# ------------------------------------------------------------
# 📁 Fichier : app/routers/ingredients.py
# 🎯 Objectif : Gestion des ingrédients avec isolation stricte des données utilisateur.
# ------------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

# Importations (corrigées en imports relatifs pour la structure du projet)
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_active_user # Dépendance d'authentification active.

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.get("/", response_model=List[schemas.Ingredient])
def get_ingredients(
    location: Optional[str] = None, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère tous les ingrédients appartenant à l'utilisateur actuellement connecté."""
    
    # --- ISOLATION CORRIGÉE: FILTRER PAR OWNER_ID ---
    query = db.query(models.Ingredient).filter(
        models.Ingredient.owner_id == current_user.id
    )
    
    if location:
        query = query.filter(models.Ingredient.location == location)
        
    return query.all()

@router.get("/{ingredient_id}", response_model=schemas.Ingredient)
def get_ingredient(
    ingredient_id: int, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère un ingrédient spécifique, uniquement s'il appartient à l'utilisateur."""
    # --- ISOLATION CORRIGÉE: FILTRER PAR OWNER_ID ---
    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.owner_id == current_user.id
    ).first()
    
    if not ingredient:
        # 404 si non trouvé OU s'il appartient à un autre utilisateur
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found or does not belong to user")
    return ingredient

@router.post("/", response_model=schemas.Ingredient, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    ingredient: schemas.IngredientCreate, 
    # TEMPORAIRE : Commenté pour les tests de base de données.
    # Réactivez cette ligne pour la production : 
    # current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Crée un nouvel ingrédient et l'associe à un utilisateur de test temporaire."""
    
    # ATTENTION : Si vous avez commenté 'current_user' ci-dessus,
    # vous DEVEZ fournir un owner_id statique pour les tests :
    test_user_id = 1  # Utilisez 1, car c'est souvent le premier ID généré par PostgreSQL
    
    db_ingredient = models.Ingredient(
        **ingredient.model_dump(),
        # --- ASSIGNER L'OWNER_ID STATIQUE POUR LES TESTS ---
        owner_id=test_user_id 
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.put("/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(
    ingredient_id: int, 
    ingredient: schemas.IngredientUpdate, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Met à jour un ingrédient, uniquement s'il appartient à l'utilisateur."""
    
    # --- ISOLATION CORRIGÉE: FILTRER PAR OWNER_ID ---
    ingredient_query = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.owner_id == current_user.id
    )
    db_ingredient = ingredient_query.first()
    
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found or does not belong to user")
    
    update_data = ingredient.model_dump(exclude_unset=True)
    ingredient_query.update(update_data, synchronize_session=False)
    
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Supprime un ingrédient, uniquement s'il appartient à l'utilisateur."""
    
    # --- ISOLATION CORRIGÉE: FILTRER PAR OWNER_ID ---
    db_ingredient_query = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.owner_id == current_user.id
    )
    
    if not db_ingredient_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found or does not belong to user")
    
    db_ingredient_query.delete(synchronize_session=False)
    db.commit()
    return

@router.get("/expiring/soon", response_model=List[schemas.Ingredient])
def get_expiring_soon(
    days: int = 7, 
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère les ingrédients de l'utilisateur qui expirent bientôt."""
    expiry_threshold = datetime.now().date() + timedelta(days=days)
    
    # --- ISOLATION CORRIGÉE: FILTRER PAR OWNER_ID ---
    ingredients = db.query(models.Ingredient).filter(
        models.Ingredient.owner_id == current_user.id,
        models.Ingredient.expiry_date.isnot(None),
        models.Ingredient.expiry_date <= expiry_threshold
    ).all()
    return ingredients

@router.post(
    "/seed-sample", 
    response_model=schemas.MessageResponse 
)
def seed_ingredients(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ajoute des échantillons d'ingrédients, associés à l'utilisateur actuel."""
    sample_ingredients = [
        {"name": "Chicken Breast", "location": "Fridge", "quantity": 2.0, "unit": "kg", "category": "Meat"},
        {"name": "Lettuce", "location": "Fridge", "quantity": 1.0, "unit": "pcs", "category": "Produce"},
        {"name": "Tomato", "location": "Fridge", "quantity": 5.0, "unit": "pcs", "category": "Produce"},
        {"name": "Olive Oil", "location": "Pantry", "quantity": 1.0, "unit": "liter", "category": "Oil"},
    ]
    
    for item in sample_ingredients:
        # --- ISOLATION CORRIGÉE: ASSIGNER L'OWNER_ID ---
        db_item = models.Ingredient(**item, owner_id=current_user.id)
        db.add(db_item)
    db.commit()
    return {"message": "Sample ingredients seeded successfully for user " + str(current_user.id)}
