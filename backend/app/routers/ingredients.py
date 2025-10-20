from fastapi import APIRouter, Depends, HTTPException, status # Ajout de 'status' pour plus de clarté
from sqlalchemy.orm import Session
from typing import List, Optional # Optional est mieux pour les paramètres optionnels
from datetime import datetime, timedelta

# Importation de la fonction d'authentification
from ..auth import get_current_user
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.get("/", response_model=List[schemas.Ingredient])
def get_ingredients(
    location: Optional[str] = None, # Utilisation de Optional pour le type hint
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère tous les ingrédients appartenant à l'utilisateur actuellement connecté."""
    
    # --- ISOLATION: FILTRER PAR USER ID ---
    query = db.query(models.Ingredient).filter(
        models.Ingredient.user_id == current_user.id
    )
    
    if location:
        query = query.filter(models.Ingredient.location == location)
        
    return query.all()

@router.get("/{ingredient_id}", response_model=schemas.Ingredient)
def get_ingredient(
    ingredient_id: int, 
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère un ingrédient spécifique, uniquement s'il appartient à l'utilisateur."""
    # --- ISOLATION: FILTRER PAR USER ID ---
    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.user_id == current_user.id
    ).first()
    
    if not ingredient:
        # 404 si non trouvé OU s'il appartient à un autre utilisateur
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found or does not belong to user")
    return ingredient

@router.post("/", response_model=schemas.Ingredient)
def create_ingredient(
    ingredient: schemas.IngredientCreate, 
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crée un nouvel ingrédient et l'associe à l'utilisateur actuel."""
    # Note: On laisse le check d'existence car il est basé sur le nom, mais on pourrait le rendre spécifique à l'utilisateur.
    
    db_ingredient = models.Ingredient(
        **ingredient.model_dump(),
        # --- ISOLATION: ASSIGNER LE USER ID ---
        user_id=current_user.id 
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.put("/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(
    ingredient_id: int, 
    ingredient: schemas.IngredientUpdate, 
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Met à jour un ingrédient, uniquement s'il appartient à l'utilisateur."""
    # --- ISOLATION: FILTRER PAR USER ID ---
    db_ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.user_id == current_user.id
    ).first()
    
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found or does not belong to user")
    
    update_data = ingredient.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)
    
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient

@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT) # Utilisation d'un code de succès standard pour DELETE
def delete_ingredient(
    ingredient_id: int, 
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Supprime un ingrédient, uniquement s'il appartient à l'utilisateur."""
    # --- ISOLATION: FILTRER PAR USER ID ---
    db_ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.user_id == current_user.id
    ).first()
    
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found or does not belong to user")
    
    db.delete(db_ingredient)
    db.commit()
    return

@router.get("/expiring/soon", response_model=List[schemas.Ingredient])
def get_expiring_soon(
    days: int = 7, 
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Récupère les ingrédients de l'utilisateur qui expirent bientôt."""
    expiry_threshold = datetime.now().date() + timedelta(days=days)
    
    # --- ISOLATION: FILTRER PAR USER ID ---
    ingredients = db.query(models.Ingredient).filter(
        models.Ingredient.user_id == current_user.id,
        models.Ingredient.expiry_date.isnot(None),
        models.Ingredient.expiry_date <= expiry_threshold
    ).all()
    return ingredients

@router.post(
    "/seed-sample", 
    # CORRECTION APPLIQUÉE ICI : Utiliser le modèle Pydantic
    response_model=schemas.MessageResponse 
)
def seed_ingredients(
    # --- AUTH: AJOUTER LA DEPENDANCE UTILISATEUR ---
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ajoute des échantillons d'ingrédients, associés à l'utilisateur actuel."""
    sample_ingredients = [
        # Note: L'ajout des champs 'category', 'unit', etc. est essentiel si votre modèle SQL le nécessite.
        # J'ai mis des valeurs par défaut pour les champs manquants dans votre exemple de liste (à ajuster selon votre schéma SQL exact).
        {"name": "Chicken Breast", "location": "Fridge", "quantity": 2.0, "unit": "kg", "category": "Meat"},
        {"name": "Lettuce", "location": "Fridge", "quantity": 1.0, "unit": "pcs", "category": "Produce"},
        {"name": "Tomato", "location": "Fridge", "quantity": 5.0, "unit": "pcs", "category": "Produce"},
        {"name": "Olive Oil", "location": "Pantry", "quantity": 1.0, "unit": "liter", "category": "Oil"},
    ]
    
    for item in sample_ingredients:
        # --- ISOLATION: ASSIGNER LE USER ID ---
        db_item = models.Ingredient(**item, user_id=current_user.id)
        db.add(db_item)
    db.commit()
    return {"message": "Sample ingredients seeded successfully for user " + str(current_user.id)}
