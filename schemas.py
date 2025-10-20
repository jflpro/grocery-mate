from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

# =============================
# 🧂 Ingredient Schemas
# =============================

class IngredientBase(BaseModel):
    name: str
    category: str
    location: str
    quantity: float
    unit: str
    expiry_date: Optional[date] = None  # date d’expiration optionnelle

class IngredientCreate(IngredientBase):
    pass  # user_id sera injecté depuis le router (current_user)

class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    expiry_date: Optional[date] = None

class Ingredient(IngredientBase):
    id: int
    user_id: int  # 🔹 lien avec l’utilisateur
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # permet de convertir depuis un modèle SQLAlchemy


# =============================
# 🛒 Shopping List Schemas
# =============================

class ShoppingItemBase(BaseModel):
    item_name: str
    quantity: float
    unit: str
    is_purchased: bool = False

class ShoppingItemCreate(ShoppingItemBase):
    pass

class ShoppingItem(ShoppingItemBase):
    id: int
    shopping_list_id: int

    class Config:
        from_attributes = True

class ShoppingListBase(BaseModel):
    name: str

class ShoppingListCreate(ShoppingListBase):
    user_id: int = 1  # valeur par défaut pour test, sera remplacée par current_user

class ShoppingList(ShoppingListBase):
    id: int
    created_at: datetime
    user_id: int
    items: List[ShoppingItem] = []

    class Config:
        from_attributes = True


# =============================
# 🍳 Recipe Schemas
# =============================

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    ingredients: str  # liste des ingrédients au format texte (JSON possible)
    instructions: str
    prep_time: Optional[int] = None
    servings: int = 2
    calories: Optional[int] = None
    is_healthy: bool = True

class RecipeCreate(RecipeBase):
    pass  # user_id sera injecté depuis le router (current_user)

class Recipe(RecipeBase):
    id: int
    user_id: int  # 🔹 lien avec l’utilisateur
    created_at: datetime

    class Config:
        from_attributes = True
