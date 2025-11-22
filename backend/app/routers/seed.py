# 📁 app/routers/seed.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, auth
from ..database import get_db
from ..seed_data import (
    create_service_user,
    seed_ingredients,
    seed_recipes,
    seed_shopping_lists,
    run_seed_for_user,
)

router = APIRouter(
    prefix="/seed",
    tags=["seed"],
)


@router.post("/")
def seed_for_service_user(db: Session = Depends(get_db)):
    """
    Seed global de démo pour l'utilisateur seed_user (ID = 1).
    Utilisé surtout pour les tests / scripts.
    """
    service_user: models.User = create_service_user(db)
    owner_id = service_user.id

    seed_ingredients(db, owner_id)
    seed_recipes(db, owner_id)
    seed_shopping_lists(db, owner_id)

    return {
        "message": f"All sample data seeded successfully for seed_user (ID {owner_id})"
    }


@router.post("/me")
def seed_for_current_user(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Seed les données d'exemple pour l'utilisateur actuellement connecté.
    """
    # Utilise la fonction utilitaire qui ouvre sa propre SessionLocal
    run_seed_for_user(current_user.id)

    return {
        "message": f"Sample data seeded successfully for current user (ID {current_user.id})"
    }
