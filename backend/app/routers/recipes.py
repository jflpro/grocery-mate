from typing import List, Optional, Dict, Any 
import json 
import copy 

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_ 

from .. import models, schemas, auth 
from ..database import get_db
# Importation directe de la fonction depuis le sous-module
from ..crud.recipe_generator import generate_recipe_from_ingredients 

# Initialisation du routeur
router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

# --- Fonction Utile ---

def get_recipe_or_404(db: Session, recipe_id: int) -> models.Recipe:
    """Récupère une recette par ID ou lève une exception 404."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recette avec l'ID {recipe_id} non trouvée.")
    return recipe

# --- Endpoints CRUD ---

@router.get("/", response_model=List[schemas.RecipeOut])
def get_all_recipes(
    db: Session = Depends(get_db), 
    limit: int = 100, 
    skip: int = 0,
    search: Optional[str] = "",
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional) 
):
    """
    Récupère les recettes. Affiche les recettes publiques ET les recettes privées de l'utilisateur connecté.
    """
    
    query = db.query(models.Recipe)
    
    # --- LOGIQUE DE SÉCURITÉ/VISIBILITÉ ---
    if current_user:
        # Afficher les recettes de l'utilisateur ET les recettes publiques
        query = query.filter(or_(
            models.Recipe.owner_id == current_user.id,
            models.Recipe.is_public == True
        ))
    else:
        # Seulement les recettes publiques pour les utilisateurs non authentifiés
        query = query.filter(models.Recipe.is_public == True)
        
    # Filtrage par recherche
    if search:
        query = query.filter(models.Recipe.title.ilike(f"%{search}%"))
        
    recipes = query.limit(limit).offset(skip).all()
    
    return recipes

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RecipeOut)
def create_recipe(
    recipe: schemas.RecipeCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user) 
):
    """Crée une nouvelle recette. Doit gérer l'insertion des ingrédients requis."""
    
    # 1. Préparer les données de la recette principale (exclure la liste d'ingrédients)
    recipe_data = recipe.model_dump(exclude={"required_ingredients"}, exclude_none=True)
    new_recipe = models.Recipe(
        owner_id=current_user.id, # Clé étrangère correcte
        **recipe_data
    )
    
    try:
        db.add(new_recipe)
        db.flush() # Nécessaire pour obtenir l'ID de la nouvelle recette
        
        # 2. Ajouter les RecipeIngredient associés à la nouvelle recette
        for req_ing_data in recipe.required_ingredients:
            req_ing = models.RecipeIngredient(
                recipe_id=new_recipe.id,
                **req_ing_data.model_dump(exclude_none=True)
            )
            db.add(req_ing)
            
        db.commit()
        db.refresh(new_recipe)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur d'intégrité de la base de données. Vérifiez les champs obligatoires."
        )
    
    return new_recipe

@router.get("/{recipe_id}", response_model=schemas.RecipeOut)
def get_recipe(
    recipe_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    """Récupère une recette spécifique par ID."""
    recipe = get_recipe_or_404(db, recipe_id)
    
    # --- LOGIQUE DE SÉCURITÉ/VISIBILITÉ ---
    # Si la recette n'est pas publique ET que l'utilisateur n'est pas l'owner
    if not recipe.is_public and (not current_user or recipe.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Recette non trouvée ou non autorisée."
        )
        
    return recipe

@router.put("/{recipe_id}", response_model=schemas.RecipeOut)
def update_recipe(
    recipe_id: int, 
    updated_recipe: schemas.RecipeUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Met à jour une recette existante. Seul le propriétaire peut modifier."""
    
    recipe_query = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.owner_id == current_user.id # Vérification d'autorisation
    )
    recipe = recipe_query.first()
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Recette avec l'ID {recipe_id} non trouvée ou non autorisée."
        )
    
    # 1. Mise à jour des champs de la recette principale (seuls les champs définis sont mis à jour)
    recipe_data = updated_recipe.model_dump(exclude_unset=True) 
    
    recipe_query.update(recipe_data, synchronize_session=False)
    db.commit()
    return recipe_query.first()

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Supprime une recette. Seul le propriétaire peut supprimer."""
    
    recipe_query = db.query(models.Recipe).filter(
        models.Recipe.id == recipe_id,
        models.Recipe.owner_id == current_user.id # Vérification d'autorisation
    )
    
    if not recipe_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Recette non trouvée ou non autorisée."
        )

    recipe_query.delete(synchronize_session=False)
    db.commit()
    
    return 

# --------------------------------------------------------------------
# ENDPOINT : GÉNÉRATION DE RECETTES (API GEMINI)
# --------------------------------------------------------------------

@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_recipe(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_active_user)
) -> Dict[str, Any]:
    """
    Génère une recette structurée à partir de l'inventaire de l'utilisateur via l'API Gemini.
    """
    user_id = current_user.id
    
    # 1. Récupérer tous les ingrédients de l'utilisateur (l'inventaire)
    # CORRECTION D'INTÉGRITÉ: Utilisation de 'owner_id' au lieu de 'user_id'
    user_ingredients = db.query(models.Ingredient).filter(models.Ingredient.owner_id == user_id).all()
    
    # 2. Appeler la fonction de génération de recette asynchrone
    try:
        recipe_data = await generate_recipe_from_ingredients(user_ingredients)
        
        return {
            "status": "success",
            "recipe": recipe_data
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur inattendue s'est produite lors de la génération: {str(e)}"
        )

# --------------------------------------------------------------------
# LOGIQUE AVANCÉE : VÉRIFICATION DE L'INVENTAIRE
# --------------------------------------------------------------------

@router.get(
    "/check-inventory", 
    response_model=List[schemas.InventoryCheckResponse], 
    summary="Identifier les recettes faisables avec l'inventaire actuel"
)
def check_recipes_feasibility(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user) 
):
    """
    Vérifie les recettes accessibles à l'utilisateur contre son inventaire.
    """
    
    # 1. Récupère l'inventaire de l'utilisateur
    # CORRECTION D'INTÉGRITÉ: Utilisation de 'owner_id' au lieu de 'user_id'
    inventory = db.query(models.Ingredient).filter(
        models.Ingredient.owner_id == current_user.id
    ).all()
    
    inventory_map = {ing.name.lower(): ing for ing in inventory}
    
    # 2. Récupère toutes les recettes accessibles
    recipes = db.query(models.Recipe).filter(or_(
        models.Recipe.owner_id == current_user.id,
        models.Recipe.is_public == True
    )).all()
    
    results = []
    
    for recipe in recipes:
        can_make = True
        missing_items = []
        available_items = [] 
        
        # 3. Vérifie chaque ingrédient requis
        for req_ing in recipe.required_ingredients:
            req_name = req_ing.name.lower()
            inv_item = inventory_map.get(req_name)
            
            # Contexte pour l'ingrédient requis (format dict pour le schéma de réponse)
            req_data = {
                "name": req_ing.name,
                "quantity": req_ing.quantity,
                "unit": req_ing.unit,
            }
            
            if not inv_item:
                # Ingrédient requis non trouvé
                can_make = False
                missing_items.append({**req_data, "reason": "Missing entirely"})
                continue
            
            # L'ingrédient est présent
            inv_quantity = inv_item.quantity
            inv_unit = inv_item.unit
            
            # 4. Vérifie la quantité et l'unité
            # Logique simple: doit correspondre en unité ET en quantité
            if inv_unit.lower() == req_ing.unit.lower() and inv_quantity >= req_ing.quantity:
                # Quantité suffisante et même unité
                available_items.append({
                    "name": inv_item.name,
                    "quantity": inv_quantity,
                    "unit": inv_unit,
                })
                continue
            else:
                # Unité différente OU quantité insuffisante
                can_make = False
                
                # Ajout aux manquants avec la raison détaillée
                missing_items.append({
                    **req_data,
                    "available_quantity": inv_quantity,
                    "available_unit": inv_unit,
                    "reason": "Insufficient quantity or unit mismatch"
                })

        # 5. Ajoute le résultat
        results.append(schemas.InventoryCheckResponse(
            recipe_id=recipe.id, 
            can_make=can_make,
            missing_items=missing_items,
            available_items=available_items 
        ))
        
    return results
