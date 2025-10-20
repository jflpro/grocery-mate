from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional # Ajout de Optional pour la clarté
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/shopping-lists", tags=["shopping-lists"])

# --- Shopping Lists (CRUD) ---

@router.get("/", response_model=List[schemas.ShoppingList])
def get_shopping_lists(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Récupère toutes les listes de courses de l'utilisateur courant."""
    # ISOLATION: Filtre par user_id
    return db.query(models.ShoppingList).filter(
        models.ShoppingList.user_id == current_user.id
    ).order_by(models.ShoppingList.created_at.desc()).all()

@router.get("/{list_id}", response_model=schemas.ShoppingList)
def get_shopping_list(
    list_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Récupère une liste de courses spécifique de l'utilisateur courant."""
    shopping_list = db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id,
        # ISOLATION: Vérifie la propriété
        models.ShoppingList.user_id == current_user.id
    ).first()
    
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found or access denied")
    return shopping_list

@router.post("/", response_model=schemas.ShoppingList, status_code=status.HTTP_201_CREATED)
def create_shopping_list(
    shopping_list: schemas.ShoppingListCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Crée une nouvelle liste de courses pour l'utilisateur courant."""
    
    # --- CORRECTION APPLIQUÉE ICI ---
    # L'utilisateur ne doit pas envoyer le user_id. On l'assigne automatiquement 
    # à partir du token (current_user.id) pour garantir la sécurité.
    
    # Prépare les données de la liste
    list_data = shopping_list.model_dump()
    
    # ASSIGNATION: Ajoute le user_id de l'utilisateur authentifié
    db_list = models.ShoppingList(**list_data, user_id=current_user.id)
    
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

@router.delete("/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list(
    list_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Supprime une liste de courses et tous ses éléments (via cascade='all, delete-orphan')."""
    db_list = db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id,
        # ISOLATION: Vérifie la propriété avant suppression
        models.ShoppingList.user_id == current_user.id
    )
    if not db_list.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found or access denied")
        
    db_list.delete(synchronize_session=False)
    db.commit()
    return 

# --- Shopping Items (Actions) ---

@router.post("/{list_id}/items", response_model=schemas.ShoppingItem, status_code=status.HTTP_201_CREATED)
def add_item_to_list(
    list_id: int, 
    item: schemas.ShoppingItemCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Ajoute un élément à une liste de courses appartenant à l'utilisateur courant."""
    # Vérifie l'existence et la propriété de la liste parente
    shopping_list = db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id,
        # ISOLATION: Vérifie la propriété de la liste
        models.ShoppingList.user_id == current_user.id
    ).first()
    
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found or access denied")
        
    db_item = models.ShoppingItem(**item.model_dump(), shopping_list_id=list_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/items/{item_id}", response_model=schemas.ShoppingItem)
def update_shopping_item(
    item_id: int, 
    is_purchased: bool, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Met à jour le statut d'achat d'un élément (et vérifie la propriété via la liste parente)."""
    # JOINTURE: Joint ShoppingItem et ShoppingList pour vérifier la propriété du parent
    db_item = db.query(models.ShoppingItem).join(models.ShoppingList).filter(
        models.ShoppingItem.id == item_id,
        models.ShoppingList.user_id == current_user.id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping item not found or access denied")
        
    db_item.is_purchased = is_purchased
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_item(
    item_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Supprime un élément (et vérifie la propriété via la liste parente)."""
    # JOINTURE: Joint ShoppingItem et ShoppingList pour vérifier la propriété du parent
    db_item_query = db.query(models.ShoppingItem).join(models.ShoppingList).filter(
        models.ShoppingItem.id == item_id,
        models.ShoppingList.user_id == current_user.id
    )
    
    if not db_item_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping item not found or access denied")
        
    db_item_query.delete(synchronize_session=False)
    db.commit()
    return 

@router.post("/{list_id}/items/clear-purchased", response_model=schemas.ShoppingList)
def clear_purchased_items(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Supprime tous les éléments marqués comme achetés dans une liste spécifique de l'utilisateur."""
    shopping_list = db.query(models.ShoppingList).filter(
        models.ShoppingList.id == list_id,
        # ISOLATION: Vérifie la propriété
        models.ShoppingList.user_id == current_user.id
    ).first()

    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found or access denied")

    # Supprimer les éléments achetés
    db.query(models.ShoppingItem).filter(
        models.ShoppingItem.shopping_list_id == list_id,
        models.ShoppingItem.is_purchased == True
    ).delete(synchronize_session=False)

    db.commit()
    # Recharge la liste pour refléter les suppressions
    db.refresh(shopping_list)
    return shopping_list
