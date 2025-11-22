from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas, auth
from ..database import get_db
from ..auth import get_current_active_user  # Auth dependency (required)

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])

# --- Shopping Lists (CRUD) ---


@router.get("/", response_model=List[schemas.ShoppingList])
def get_shopping_lists(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get all shopping lists for the current authenticated user.
    """
    # ISOLATION: filter by owner_id (data isolation)
    return (
        db.query(models.ShoppingList)
        .filter(models.ShoppingList.owner_id == current_user.id)
        .order_by(models.ShoppingList.created_at.desc())
        .all()
    )


@router.get("/{list_id}", response_model=schemas.ShoppingList)
def get_shopping_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get a specific shopping list for the current authenticated user.
    """
    shopping_list = (
        db.query(models.ShoppingList)
        .filter(
            models.ShoppingList.id == list_id,
            # ISOLATION: check ownership
            models.ShoppingList.owner_id == current_user.id,
        )
        .first()
    )

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
        )
    return shopping_list


@router.post("/", response_model=schemas.ShoppingList, status_code=status.HTTP_201_CREATED)
def create_shopping_list(
    shopping_list: schemas.ShoppingListCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Create a new shopping list for the current authenticated user.
    """
    list_data = shopping_list.model_dump()

    # ASSIGNMENT: attach owner_id (data integrity)
    db_list = models.ShoppingList(**list_data, owner_id=current_user.id)

    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Delete a shopping list and all its items (via cascade='all, delete-orphan').
    """
    db_list = db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id,
        # ISOLATION: check ownership before deletion
        models.ShoppingList.owner_id == current_user.id,
    )

    if not db_list.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
        )

    db_list.delete(synchronize_session=False)
    db.commit()
    return


# --- Shopping Items (actions on list items) ---
# Note: these endpoints use joins to verify ownership via the parent list,
# which guarantees security.


@router.post("/{list_id}/items", response_model=schemas.ShoppingItem, status_code=status.HTTP_201_CREATED)
def add_item_to_list(
    list_id: int,
    item: schemas.ShoppingItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Add an item to a shopping list owned by the current user.
    """
    # Check existence + ownership of the parent list
    shopping_list = (
        db.query(models.ShoppingList)
        .filter(
            models.ShoppingList.id == list_id,
            # ISOLATION: verify list ownership
            models.ShoppingList.owner_id == current_user.id,
        )
        .first()
    )

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
        )

    db_item = models.ShoppingItem(**item.model_dump(), shopping_list_id=list_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/items/{item_id}", response_model=schemas.ShoppingItem)
def update_shopping_item(
    item_id: int,
    item_update: schemas.ShoppingItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Update a shopping item (name / quantity / unit / is_purchased),
    while checking that it belongs to the current user via the parent list.
    """
    # JOIN: ShoppingItem + ShoppingList to verify ownership through the parent list
    db_item = (
        db.query(models.ShoppingItem)
        .join(models.ShoppingList)
        .filter(
            models.ShoppingItem.id == item_id,
            # Ownership check on parent list
            models.ShoppingList.owner_id == current_user.id,
        )
        .first()
    )

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping item not found or access denied",
        )

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Delete a shopping item, verifying ownership via the parent list.
    """
    # JOIN: ShoppingItem + ShoppingList to verify ownership
    db_item_query = (
        db.query(models.ShoppingItem)
        .join(models.ShoppingList)
        .filter(
            models.ShoppingItem.id == item_id,
            # Ownership check on parent list
            models.ShoppingList.owner_id == current_user.id,
        )
    )

    if not db_item_query.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping item not found or access denied",
        )

    db_item_query.delete(synchronize_session=False)
    db.commit()
    return


@router.post("/{list_id}/items/clear-purchased", response_model=schemas.ShoppingList)
def clear_purchased_items(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Delete all items marked as purchased in a specific list for the current user.
    """
    shopping_list = (
        db.query(models.ShoppingList)
        .filter(
            models.ShoppingList.id == list_id,
            # ISOLATION: verify ownership
            models.ShoppingList.owner_id == current_user.id,
        )
        .first()
    )

    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found or access denied",
        )

    # Delete purchased items
    db.query(models.ShoppingItem).filter(
        models.ShoppingItem.shopping_list_id == list_id,
        models.ShoppingItem.is_purchased == True,
    ).delete(synchronize_session=False)

    db.commit()
    # Refresh list to reflect deletions
    db.refresh(shopping_list)
    return shopping_list
