# 📁 app/seed_data.py
from datetime import date
from sqlalchemy.orm import Session

from . import models
from .database import SessionLocal
from .utils.security import get_password_hash


# ----------------------------
# Création d’un user de service (ID 1)
# ----------------------------
def create_service_user(db: Session) -> models.User:
    """
    Crée seed_user (ID 1) si nécessaire.
    Cet utilisateur servira de propriétaire (owner_id) pour les données seedées.
    """
    user = db.query(models.User).filter_by(id=1).first()
    if not user:
        hashed_password = get_password_hash("password123")
        user = models.User(
            id=1,
            username="seed_user",
            email="seed@app.com",
            password=hashed_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ----------------------------
# Seed Ingrédients
# ----------------------------
def seed_ingredients(db: Session, owner_id: int) -> None:
    sample_ingredients = [
        {
            "name": "Chicken Breast",
            "category": "Meat",
            "location": "Fridge",
            "quantity": 2,
            "unit": "kg",
            "expiry_date": date(2025, 11, 5),
        },
        {
            "name": "Lettuce",
            "category": "Vegetables",
            "location": "Fridge",
            "quantity": 1,
            "unit": "pcs",
            "expiry_date": date(2025, 11, 4),
        },
        {
            "name": "Tomato",
            "category": "Vegetables",
            "location": "Fridge",
            "quantity": 5,
            "unit": "pcs",
            "expiry_date": date(2025, 11, 4),
        },
        {
            "name": "Olive Oil",
            "category": "Oil",
            "location": "Pantry",
            "quantity": 1,
            "unit": "liter",
            "expiry_date": None,
        },
        {
            "name": "Banana",
            "category": "Fruits",
            "location": "Fridge",
            "quantity": 6,
            "unit": "pcs",
            "expiry_date": date(2025, 11, 2),
        },
        {
            "name": "Strawberry",
            "category": "Fruits",
            "location": "Fridge",
            "quantity": 200,
            "unit": "grams",
            "expiry_date": date(2025, 11, 1),
        },
    ]

    for item in sample_ingredients:
        existing = (
            db.query(models.Ingredient)
            .filter_by(name=item["name"], owner_id=owner_id)
            .first()
        )
        if not existing:
            ingredient = models.Ingredient(
                name=item["name"],
                category=item["category"],
                location=item["location"],
                quantity=item["quantity"],
                unit=item["unit"],
                expiry_date=item["expiry_date"],
                owner_id=owner_id,
            )
            db.add(ingredient)
    db.commit()


# ----------------------------
# Seed Recettes
# ----------------------------
def seed_recipes(db: Session, owner_id: int) -> None:
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
            ],
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
            ],
        },
    ]

    for r in sample_recipes:
        existing = (
            db.query(models.Recipe)
            .filter_by(title=r["title"], owner_id=owner_id)
            .first()
        )
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
                owner_id=owner_id,
            )
            db.add(recipe)
            db.commit()
            db.refresh(recipe)

            for ing in r["ingredients"]:
                existing_ing = (
                    db.query(models.RecipeIngredient)
                    .filter_by(recipe_id=recipe.id, name=ing["name"])
                    .first()
                )
                if not existing_ing:
                    recipe_ing = models.RecipeIngredient(
                        recipe_id=recipe.id,
                        name=ing["name"],
                        quantity=ing["quantity"],
                        unit=ing["unit"],
                    )
                    db.add(recipe_ing)
            db.commit()


# ----------------------------
# Seed Shopping Lists
# ----------------------------
def seed_shopping_lists(db: Session, owner_id: int) -> None:
    sample_lists = [
        {
            "name": "Weekly Groceries",
            "items": [
                {
                    "item_name": "Milk",
                    "quantity": 1,
                    "unit": "liter",
                    "is_purchased": False,
                },
                {
                    "item_name": "Eggs",
                    "quantity": 12,
                    "unit": "pcs",
                    "is_purchased": False,
                },
                {
                    "item_name": "Bread",
                    "quantity": 1,
                    "unit": "loaf",
                    "is_purchased": True,
                },
            ],
        }
    ]

    for l in sample_lists:
        existing_list = (
            db.query(models.ShoppingList)
            .filter_by(name=l["name"], owner_id=owner_id)
            .first()
        )
        if not existing_list:
            shopping_list = models.ShoppingList(
                name=l["name"],
                owner_id=owner_id,
            )
            db.add(shopping_list)
            db.commit()
            db.refresh(shopping_list)

            for item in l["items"]:
                existing_item = (
                    db.query(models.ShoppingItem)
                    .filter_by(
                        shopping_list_id=shopping_list.id,
                        item_name=item["item_name"],
                    )
                    .first()
                )
                if not existing_item:
                    shopping_item = models.ShoppingItem(
                        shopping_list_id=shopping_list.id,
                        item_name=item["item_name"],
                        quantity=item["quantity"],
                        unit=item["unit"],
                        is_purchased=item["is_purchased"],
                    )
                    db.add(shopping_item)
            db.commit()


# ----------------------------
# Utilitaire possible pour un seed par user
# ----------------------------
def run_seed_for_user(owner_id: int) -> None:
    """
    Exemple d’usage si tu veux plus tard un endpoint /api/seed/me
    qui seed pour l’utilisateur connecté.
    """
    db = SessionLocal()
    try:
        seed_ingredients(db, owner_id)
        seed_recipes(db, owner_id)
        seed_shopping_lists(db, owner_id)
    finally:
        db.close()
