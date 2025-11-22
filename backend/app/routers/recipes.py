from typing import List, Optional, Dict, Any
import json
import copy

from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from .. import models, schemas, auth
from ..database import get_db
# Direct import of the function from the submodule
from ..crud.recipe_generator import generate_recipe_from_ingredients

# Router initialization
router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

# --- Helper function ---


def get_recipe_or_404(db: Session, recipe_id: int) -> models.Recipe:
    """Retrieve a recipe by ID or raise a 404 exception."""
    recipe = db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found.",
        )
    return recipe


# --- CRUD endpoints ---


@router.get("/", response_model=List[schemas.RecipeOut])
def get_all_recipes(
    db: Session = Depends(get_db),
    limit: int = 100,
    skip: int = 0,
    search: Optional[str] = "",
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional),
):
    """
    Retrieve recipes. Show public recipes AND the private recipes of the logged-in user.
    """

    query = db.query(models.Recipe)

    # --- Security / visibility logic ---
    if current_user:
        # Show recipes owned by the user AND public recipes
        query = query.filter(
            or_(
                models.Recipe.owner_id == current_user.id,
                models.Recipe.is_public == True,
            )
        )
    else:
        # Only public recipes for unauthenticated users
        query = query.filter(models.Recipe.is_public == True)

    # Filtering by search term
    if search:
        query = query.filter(models.Recipe.title.ilike(f"%{search}%"))

    recipes = query.limit(limit).offset(skip).all()

    return recipes


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RecipeOut)
def create_recipe(
    recipe: schemas.RecipeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """Create a new recipe. Also handles insertion of required ingredients."""
    # 1. Prepare main recipe data (exclude the list of required ingredients)
    recipe_data = recipe.model_dump(exclude={"required_ingredients"}, exclude_none=True)
    new_recipe = models.Recipe(
        owner_id=current_user.id,  # Correct foreign key
        **recipe_data,
    )

    try:
        db.add(new_recipe)
        db.flush()  # Needed to obtain the ID of the newly created recipe

        # 2. Add associated RecipeIngredient entries for the new recipe
        for req_ing_data in recipe.required_ingredients:
            req_ing = models.RecipeIngredient(
                recipe_id=new_recipe.id,
                **req_ing_data.model_dump(exclude_none=True),
            )
            db.add(req_ing)

        db.commit()
        db.refresh(new_recipe)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Please check required fields.",
        )

    return new_recipe


@router.get("/{recipe_id}", response_model=schemas.RecipeOut)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional),
):
    """Retrieve a specific recipe by ID."""
    recipe = get_recipe_or_404(db, recipe_id)

    # --- Security / visibility logic ---
    # If the recipe is not public AND the user is not the owner
    if not recipe.is_public and (not current_user or recipe.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or not authorized.",
        )

    return recipe


@router.put("/{recipe_id}", response_model=schemas.RecipeOut)
def update_recipe(
    recipe_id: int,
    updated_recipe: schemas.RecipeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """Update an existing recipe. Only the owner can modify it."""

    recipe_query = (
        db.query(models.Recipe)
        .filter(
            models.Recipe.id == recipe_id,
            models.Recipe.owner_id == current_user.id,  # Authorization check
        )
    )
    recipe = recipe_query.first()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found or not authorized.",
        )

    # 1. Update main recipe fields (only fields that are set will be updated)
    recipe_data = updated_recipe.model_dump(exclude_unset=True)

    recipe_query.update(recipe_data, synchronize_session=False)
    db.commit()
    return recipe_query.first()


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """Delete a recipe. Only the owner can delete it."""

    recipe_query = (
        db.query(models.Recipe)
        .filter(
            models.Recipe.id == recipe_id,
            models.Recipe.owner_id == current_user.id,  # Authorization check
        )
    )

    if not recipe_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found or not authorized.",
        )

    recipe_query.delete(synchronize_session=False)
    db.commit()

    return


# --------------------------------------------------------------------
# ENDPOINT: RECIPE GENERATION (GEMINI API)
# --------------------------------------------------------------------


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_recipe(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
) -> Dict[str, Any]:
    """
    Generate a structured recipe based on the user's inventory via the Gemini API.
    """
    user_id = current_user.id

    # 1. Retrieve all ingredients owned by the user (inventory)
    # INTEGRITY FIX: Use 'owner_id' instead of 'user_id'
    user_ingredients = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.owner_id == user_id)
        .all()
    )

    # 2. Call the asynchronous recipe generation function
    try:
        recipe_data = await generate_recipe_from_ingredients(user_ingredients)

        return {
            "status": "success",
            "recipe": recipe_data,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during recipe generation: {str(e)}",
        )


# --------------------------------------------------------------------
# ADVANCED LOGIC: INVENTORY CHECK
# --------------------------------------------------------------------


@router.get(
    "/check-inventory",
    response_model=List[schemas.InventoryCheckResponse],
    summary="Identify which recipes can be made with the current inventory",
)
def check_recipes_feasibility(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    """
    Check which recipes are feasible for the user given their current inventory.
    """

    # 1. Retrieve the user's inventory
    # INTEGRITY FIX: Use 'owner_id' instead of 'user_id'
    inventory = (
        db.query(models.Ingredient)
        .filter(models.Ingredient.owner_id == current_user.id)
        .all()
    )

    inventory_map = {ing.name.lower(): ing for ing in inventory}

    # 2. Retrieve all accessible recipes
    recipes = (
        db.query(models.Recipe)
        .filter(
            or_(
                models.Recipe.owner_id == current_user.id,
                models.Recipe.is_public == True,
            )
        )
        .all()
    )

    results = []

    for recipe in recipes:
        can_make = True
        missing_items = []
        available_items = []

        # 3. Check each required ingredient
        for req_ing in recipe.required_ingredients:
            req_name = req_ing.name.lower()
            inv_item = inventory_map.get(req_name)

            # Context for the required ingredient (dict format for the response schema)
            req_data = {
                "name": req_ing.name,
                "quantity": req_ing.quantity,
                "unit": req_ing.unit,
            }

            if not inv_item:
                # Required ingredient not found
                can_make = False
                missing_items.append({**req_data, "reason": "Missing entirely"})
                continue

            # Ingredient is present
            inv_quantity = inv_item.quantity
            inv_unit = inv_item.unit

            # 4. Check quantity and unit
            # Simple logic: must match both unit AND have sufficient quantity
            if (
                inv_unit.lower() == req_ing.unit.lower()
                and inv_quantity >= req_ing.quantity
            ):
                # Sufficient quantity and same unit
                available_items.append(
                    {
                        "name": inv_item.name,
                        "quantity": inv_quantity,
                        "unit": inv_unit,
                    }
                )
                continue
            else:
                # Different unit OR insufficient quantity
                can_make = False

                # Add to missing items with detailed reason
                missing_items.append(
                    {
                        **req_data,
                        "available_quantity": inv_quantity,
                        "available_unit": inv_unit,
                        "reason": "Insufficient quantity or unit mismatch",
                    }
                )

        # 5. Append the result
        results.append(
            schemas.InventoryCheckResponse(
                recipe_id=recipe.id,
                can_make=can_make,
                missing_items=missing_items,
                available_items=available_items,
            )
        )

    return results
