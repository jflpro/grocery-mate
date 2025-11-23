from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, auth, schemas_admin
from ..database import get_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def _get_user_or_404(user_id: int, db: Session) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


# --------------------------------------------------------------------
# Admin-protected endpoints
# --------------------------------------------------------------------


@router.get("/users", response_model=List[schemas_admin.UserAdmin])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Get all users (admin only).
    """
    users = (
        db.query(models.User)
        .order_by(models.User.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return users


@router.get("/users/stats", response_model=schemas_admin.UserStats)
def get_user_stats(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Get aggregated statistics about users (admin only).
    """
    total = db.query(func.count(models.User.id)).scalar() or 0
    active = (
        db.query(func.count(models.User.id))
        .filter(models.User.is_active.is_(True))
        .scalar()
        or 0
    )
    admins = (
        db.query(func.count(models.User.id))
        .filter(models.User.is_admin.is_(True))
        .scalar()
        or 0
    )

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users = (
        db.query(func.count(models.User.id))
        .filter(models.User.created_at >= thirty_days_ago)
        .scalar()
        or 0
    )

    return schemas_admin.UserStats(
        total_users=total,
        active_users=active,
        admin_users=admins,
        new_users_this_month=new_users,
    )


@router.get("/users/{user_id}", response_model=schemas_admin.UserAdmin)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Get a specific user by ID (admin only).
    """
    user = _get_user_or_404(user_id=user_id, db=db)
    return user


@router.patch("/users/{user_id}", response_model=schemas_admin.UserAdmin)
def update_user(
    user_id: int,
    user_update: schemas_admin.UserUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Update user's admin / active status (admin only).
    Prevents admin from deactivating their own account.
    """
    user = _get_user_or_404(user_id=user_id, db=db)

    # Prevent admin from deactivating themselves
    if user.id == current_admin.id and user_update.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    data = user_update.model_dump(exclude_unset=True)

    if "is_active" in data:
        user.is_active = data["is_active"]
    if "is_admin" in data:
        user.is_admin = data["is_admin"]

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Delete a user (admin only).
    Prevents admin from deleting themselves.
    Also removes all data owned by this user to satisfy FK constraints.
    """
    user = _get_user_or_404(user_id=user_id, db=db)

    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # 1) Supprimer les objets liés au user (adapte si tu as d'autres modèles)
    db.query(models.Ingredient).filter(
        models.Ingredient.owner_id == user.id
    ).delete(synchronize_session=False)

    # TODO si tu as d'autres tables avec owner_id :
    # db.query(models.Recipe).filter(
    #     models.Recipe.owner_id == user.id
    # ).delete(synchronize_session=False)
    #
    # db.query(models.ShoppingListItem).filter(
    #     models.ShoppingListItem.owner_id == user.id
    # ).delete(synchronize_session=False)
    #
    # db.query(models.ShoppingList).filter(
    #     models.ShoppingList.owner_id == user.id
    # ).delete(synchronize_session=False)

    # 2) Supprimer l'utilisateur
    db.delete(user)
    db.commit()

    # 3) Réponse vide 204 (le frontend s'en fiche du body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
