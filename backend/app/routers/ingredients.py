# ------------------------------------------------------------
# 📁 File: app/routers/ingredients.py
# 🎯 Goal: Ingredient management with strict per-user isolation
# ------------------------------------------------------------

from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_active_user  # authentication dependency

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


# ------------------------------------------------------------
# LIST INGREDIENTS FOR CURRENT USER
# ------------------------------------------------------------
@router.get("/", response_model=List[schemas.Ingredient])
def get_ingredients(
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Return all ingredients belonging to the current user.
    Optional filter by location.
    """
    query = db.query(models.Ingredient).filter(
        models.Ingredient.owner_id == current_user.id
    )

    if location:
        query = query.filter(models.Ingredient.location == location)

    return query.order_by(models.Ingredient.name.asc()).all()


# ------------------------------------------------------------
# GET INGREDIENTS EXPIRING SOON (PER USER)
# ------------------------------------------------------------
@router.get("/expiring/soon", response_model=List[schemas.Ingredient])
def get_expiring_soon(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Return ingredients for the current user that will expire
    in the next `days` days.
    """
    expiry_threshold = datetime.now().date() + timedelta(days=days)

    ingredients = (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.owner_id == current_user.id,
            models.Ingredient.expiry_date.isnot(None),
            models.Ingredient.expiry_date <= expiry_threshold,
        )
        .order_by(models.Ingredient.expiry_date.asc())
        .all()
    )
    return ingredients


# ------------------------------------------------------------
# SEED SAMPLE INGREDIENTS FOR CURRENT USER (OPTIONAL)
# ------------------------------------------------------------
@router.post("/seed-sample", response_model=schemas.MessageResponse)
def seed_ingredients(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Seed a few sample ingredients for the current user.
    You can keep this for manual testing, or ignore it in prod.
    """
    sample_ingredients = [
        {
            "name": "Chicken Breast",
            "location": "Fridge",
            "quantity": 2.0,
            "unit": "kg",
            "category": "Meat",
        },
        {
            "name": "Lettuce",
            "location": "Fridge",
            "quantity": 1.0,
            "unit": "pcs",
            "category": "Produce",
        },
        {
            "name": "Tomato",
            "location": "Fridge",
            "quantity": 5.0,
            "unit": "pcs",
            "category": "Produce",
        },
        {
            "name": "Olive Oil",
            "location": "Pantry",
            "quantity": 1.0,
            "unit": "liter",
            "category": "Oil",
        },
    ]

    for item in sample_ingredients:
        db_item = models.Ingredient(**item, owner_id=current_user.id)
        db.add(db_item)

    db.commit()
    return {"message": f"Sample ingredients seeded successfully for user {current_user.id}"}


# ------------------------------------------------------------
# GET SINGLE INGREDIENT (PER USER)
# ------------------------------------------------------------
@router.get("/{ingredient_id}", response_model=schemas.Ingredient)
def get_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get a single ingredient if (and only if) it belongs to the current user.
    """
    ingredient = (
        db.query(models.Ingredient)
        .filter(
            models.Ingredient.id == ingredient_id,
            models.Ingredient.owner_id == current_user.id,
        )
        .first()
    )

    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found or does not belong to user",
        )

    return ingredient


# ------------------------------------------------------------
# CREATE INGREDIENT FOR CURRENT USER
# ------------------------------------------------------------
@router.post(
    "/", response_model=schemas.Ingredient, status_code=status.HTTP_201_CREATED
)
def create_ingredient(
    ingredient: schemas.IngredientCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Create a new ingredient and attach it to the current user.
    """
    db_ingredient = models.Ingredient(
        **ingredient.model_dump(),
        owner_id=current_user.id,
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


# ------------------------------------------------------------
# UPDATE INGREDIENT (PER USER)
# ------------------------------------------------------------
@router.put("/{ingredient_id}", response_model=schemas.Ingredient)
def update_ingredient(
    ingredient_id: int,
    ingredient: schemas.IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Update an ingredient if it belongs to the current user.
    """
    ingredient_query = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.owner_id == current_user.id,
    )
    db_ingredient = ingredient_query.first()

    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found or does not belong to user",
        )

    update_data = ingredient.model_dump(exclude_unset=True)
    ingredient_query.update(update_data, synchronize_session=False)

    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


# ------------------------------------------------------------
# DELETE INGREDIENT (PER USER)
# ------------------------------------------------------------
@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Delete an ingredient if it belongs to the current user.
    """
    ingredient_query = db.query(models.Ingredient).filter(
        models.Ingredient.id == ingredient_id,
        models.Ingredient.owner_id == current_user.id,
    )

    if not ingredient_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingredient not found or does not belong to user",
        )

    ingredient_query.delete(synchronize_session=False)
    db.commit()
    return
