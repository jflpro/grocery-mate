# 📁 backend/seed_data.py
from sqlalchemy.orm import Session
from datetime import date
from app.database import SessionLocal
from app import models
from app.utils.security import get_password_hash  # Correct import pour hachage mot de passe

# ----------------------------
# Création de l'utilisateur de service
# ----------------------------
def create_service_user(db: Session) -> models.User:
    """Crée l'utilisateur par défaut (ID 1) pour posséder les données seedées."""
    user = db.query(models.User).filter_by(id=1).first()
    if not user:
        hashed_password = get_password_hash("password123")
        user = models.User(
            id=1,
            username="seed_user",
            email="seed@app.com",
            password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# ----------------------------
# Seed Ingrédients
# ----------------------------
def seed_ingredients(db: Session, owner_id: int):
    sample_ingredients = [
        {"name": "Chicken Breast", "category": "Meat", "location": "Fridge", "quantity": 2, "unit": "kg", "expiry_date": date(2025, 11, 5)},
        {"name": "Lettuce", "category": "Vegetables", "location": "Fridge", "quantity": 1, "unit": "pcs", "expiry_date": date(2025, 11, 4)},
        {"name": "Tomato", "category": "Vegetables", "location": "Fridge", "quantity": 5, "unit": "pcs", "expiry_date": date(2025, 11, 4)},
        {"name": "Olive Oil", "category": "Oil", "location": "Pantry", "quantity": 1, "unit": "liter", "expiry_date": None},
        {"name": "Banana", "category": "Fruits", "location": "Fridge", "quantity": 6, "unit": "pcs", "expiry_date": date(2025, 11, 2)},
        {"name": "Strawberry", "category": "Fruits", "location": "Fridge", "quantity": 200, "unit": "grams", "expiry_date": date(2025, 11, 1)},
    ]

    for item in sample_ingredients:
        existing = db.query(models.Ingredient).filter_by(name=item["name"], owner_id=owner_id).first()
        if not existing:
            ingredient = models.Ingredient(
                name=item["name"],
                category=item["category"],
                location=item["location"],
                quantity=item["quantity"],
                unit=item["unit"],
                expiry_date=item["expiry_date"],
                owner_id=owner_id
            )
            db.add(ingredient)
    db.commit()

# ----------------------------
# Seed Recettes
# ----------------------------
def seed_recipes(db: Session, owner_id: int):
    sample_recipes = [
        {
            "title": "Grilled Chicken Salad",
            "description": "Healthy protein-packed salad with fresh vegetables",
            "instructions": "1. Grill chicken\n2. Chop vegetables\n3. Mix\n4. Season",
            "prep_time": 20,
            "cook_time": 15,
            "servings": 2,
            "calories": 350,
            "is_healthy": True,
            "is_public": True,
            "ingredients": [
                {"name": "Chicken Breast", "quantity": 2, "unit": "kg"},
                {"name": "Lettuce", "quantity": 1, "unit": "pcs"},
                {"name": "Tomato", "quantity": 5, "unit": "pcs"},
                {"name": "Olive Oil", "quantity": 1, "unit": "liter"},
            ]
        },
        {
            "title": "Fruit Smoothie",
            "description": "Refreshing and vitamin-rich smoothie",
            "instructions": "1. Blend all ingredients",
            "prep_time": 10,
            "cook_time": 0,
            "servings": 2,
            "calories": 150,
            "is_healthy": True,
            "is_public": True,
            "ingredients": [
                {"name": "Banana", "quantity": 6, "unit": "pcs"},
                {"name": "Strawberry", "quantity": 200, "unit": "grams"},
            ]
        }
    ]

    for r in sample_recipes:
        existing = db.query(models.Recipe).filter_by(title=r["title"], owner_id=owner_id).first()
        if not existing:
            recipe = models.Recipe(
                title=r["title"],
                description=r["description"],
                instructions=r["instructions"],
                prep_time=r["prep_time"],
                cook_time=r["cook_time"],
                servings=r["servings"],
                calories=r["calories"],
                is_healthy=r["is_healthy"],
                is_public=r["is_public"],
                owner_id=owner_id
            )
            db.add(recipe)
            db.commit()
            db.refresh(recipe)

            # Ajouter les ingrédients de la recette
            for ing in r["ingredients"]:
                existing_ing = db.query(models.RecipeIngredient).filter_by(recipe_id=recipe.id, name=ing["name"]).first()
                if not existing_ing:
                    recipe_ing = models.RecipeIngredient(
                        recipe_id=recipe.id,
                        name=ing["name"],
                        quantity=ing["quantity"],
                        unit=ing["unit"]
                    )
                    db.add(recipe_ing)
            db.commit()

# ----------------------------
# Seed Shopping Lists
# ----------------------------
def seed_shopping_lists(db: Session, owner_id: int):
    sample_lists = [
        {
            "name": "Weekly Groceries",
            "items": [
                {"item_name": "Milk", "quantity": 1, "unit": "liter", "is_purchased": False},
                {"item_name": "Eggs", "quantity": 12, "unit": "pcs", "is_purchased": False},
                {"item_name": "Bread", "quantity": 1, "unit": "loaf", "is_purchased": True},
            ]
        }
    ]

    for l in sample_lists:
        existing_list = db.query(models.ShoppingList).filter_by(name=l["name"], owner_id=owner_id).first()
        if not existing_list:
            shopping_list = models.ShoppingList(
                name=l["name"],
                owner_id=owner_id
            )
            db.add(shopping_list)
            db.commit()
            db.refresh(shopping_list)

            for item in l["items"]:
                existing_item = db.query(models.ShoppingItem).filter_by(shopping_list_id=shopping_list.id, item_name=item["item_name"]).first()
                if not existing_item:
                    shopping_item = models.ShoppingItem(
                        shopping_list_id=shopping_list.id,
                        item_name=item["item_name"],
                        quantity=item["quantity"],
                        unit=item["unit"],
                        is_purchased=item["is_purchased"]
                    )
                    db.add(shopping_item)
            db.commit()

# ----------------------------
# Exécution du seed
# ----------------------------
if __name__ == "__main__":
    db = SessionLocal()
    print("🌱 Seeding database with sample data...")

    try:
        service_user = create_service_user(db)
        seed_ingredients(db, service_user.id)
        seed_recipes(db, service_user.id)
        seed_shopping_lists(db, service_user.id)
        print("✅ All sample data seeded successfully for seed_user (ID 1)")
    finally:
        db.close()
