from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/seed", tags=["seed"])

def create_service_user(db: Session):
    """Crée l'utilisateur par défaut (ID 1) pour posséder les données seedées."""
    default_user = db.query(models.User).filter(models.User.id == 1).first()
    if not default_user:
        # Hachage du mot de passe pour la sécurité
        hashed_password = auth.get_password_hash("password123")
        service_user = models.User(
            id=1, # Définition explicite de l'ID pour le seeder
            username="seed_user", 
            email="seed@app.com", 
            hashed_password=hashed_password
        )
        db.add(service_user)
        db.commit()
        db.refresh(service_user)
    return db.query(models.User).filter(models.User.id == 1).first()


@router.post("/")
def seed_all(db: Session = Depends(get_db)):
    """Insère des données d'exemple dans les tables Ingrédients, Recettes et Listes de courses."""
    
    # 1. Création ou récupération de l'utilisateur de service (ID=1)
    service_user = create_service_user(db)
    user_id = service_user.id
    
    
    # --- 2. Ingrédients (Assignés à l'utilisateur de service) ---
    sample_ingredients = [
        {"name": "Chicken Breast", "category": "Meat", "location": "Fridge", "quantity": 2, "unit": "kg", "user_id": user_id},
        {"name": "Lettuce", "category": "Vegetables", "location": "Fridge", "quantity": 1, "unit": "pcs", "user_id": user_id},
        {"name": "Tomato", "category": "Vegetables", "location": "Fridge", "quantity": 5, "unit": "pcs", "user_id": user_id},
        {"name": "Olive Oil", "category": "Oil", "location": "Pantry", "quantity": 1, "unit": "liter", "user_id": user_id},
        {"name": "Banana", "category": "Fruits", "location": "Fridge", "quantity": 6, "unit": "pcs", "user_id": user_id},
        {"name": "Strawberry", "category": "Fruits", "location": "Fridge", "quantity": 200, "unit": "grams", "user_id": user_id},
    ]
    
    for item in sample_ingredients:
        # Vérifie l'existence par nom et user_id pour éviter les doublons pour cet utilisateur
        existing = db.query(models.Ingredient).filter_by(name=item["name"], user_id=user_id).first()
        if not existing:
            db.add(models.Ingredient(**item))

    # --- 3. Recettes (Assignées à l'utilisateur de service) ---
    sample_recipes = [
        {
            "name": "Grilled Chicken Salad",
            "description": "Healthy protein-packed salad with fresh vegetables",
            "ingredients": '["Chicken Breast","Lettuce","Tomato","Olive Oil"]',
            "instructions": "1. Grill chicken\n2. Chop vegetables\n3. Mix\n4. Season",
            "prep_time": 20, "servings": 2, "calories": 350, "is_healthy": True,
            "user_id": user_id 
        },
        {
            "name": "Fruit Smoothie",
            "description": "Refreshing and vitamin-rich smoothie",
            "ingredients": '["Banana","Strawberry"]',
            "instructions": "1. Blend all ingredients",
            "prep_time": 10, "servings": 2, "calories": 150, "is_healthy": True,
            "user_id": user_id
        },
    ]
    
    for item in sample_recipes:
        existing = db.query(models.Recipe).filter_by(name=item["name"], user_id=user_id).first()
        if not existing:
            db.add(models.Recipe(**item))

    # --- 4. Shopping Lists (Assignées à l'utilisateur de service) ---
    sample_lists = [
        {
            "name": "Weekly Groceries",
            "user_id": user_id,
            "items": [
                {"item_name": "Milk", "quantity": 1, "unit": "liter", "is_checked": False},
                {"item_name": "Eggs", "quantity": 12, "unit": "pcs", "is_checked": False},
                {"item_name": "Bread", "quantity": 1, "unit": "loaf", "is_checked": True}, # Exemple d'article déjà coché
            ]
        }
    ]
    
    for sl in sample_lists:
        existing_list = db.query(models.ShoppingList).filter_by(name=sl["name"], user_id=user_id).first()
        if not existing_list:
            db_list = models.ShoppingList(name=sl["name"], user_id=sl["user_id"])
            db.add(db_list)
            db.commit() 
            
            for item in sl["items"]:
                db_item = models.ShoppingItem(
                    shopping_list_id=db_list.id,
                    item_name=item["item_name"],
                    quantity=item["quantity"],
                    unit=item["unit"],
                    is_checked=item["is_checked"]
                )
                db.add(db_item)

    db.commit()
    return {"message": "All sample data seeded successfully for seed_user (ID 1)"}
