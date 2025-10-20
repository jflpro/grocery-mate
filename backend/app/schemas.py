from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

# --- BASE / CORE SCHEMAS ---

# Schéma de base pour l'utilisateur
class UserBase(BaseModel):
    email: EmailStr
    username: str

# Schéma pour la création d'un utilisateur (enregistrement)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Schéma complet de l'utilisateur (utilisé pour /auth/me)
class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schéma de réponse simple
class MessageResponse(BaseModel):
    """Réponse standard pour les confirmations et les messages d'erreur."""
    message: str

# --- AUTH SCHEMAS ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None


# --- INGREDIENT SCHEMAS (Inventaire personnel) ---

class IngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    location: str = Field(..., max_length=50)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    expiry_date: Optional[date] = None
    
# Schéma pour la création
class IngredientCreate(IngredientBase):
    pass

# Schéma pour la mise à jour
class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=50)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    expiry_date: Optional[date] = None

# Schéma complet pour la lecture
class Ingredient(IngredientBase):
    id: int
    owner_id: int # Correspond au modèle SQLAlchemy
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- RECIPE INGREDIENT SCHEMAS (Ingrédients requis pour UNE recette) ---

class RecipeIngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)

class RecipeIngredientCreate(RecipeIngredientBase):
    pass

class RecipeIngredient(RecipeIngredientBase):
    id: int
    recipe_id: int

    class Config:
        from_attributes = True


# --- RECIPE SCHEMAS ---

class RecipeBase(BaseModel):
    # ATTENTION: Renommé de 'name' à 'title' pour le modèle SQLAlchemy
    title: str = Field(..., max_length=200) 
    description: Optional[str] = None
    # Suppression du champ 'ingredients' (Text) car il est géré par la relation Many-to-Many
    instructions: str
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0) # Ajout de cook_time
    servings: int = Field(2, ge=1)
    calories: Optional[int] = Field(None, ge=0)
    is_healthy: bool = True
    is_public: bool = False # NOUVEAU: Pour partager la recette

# Schéma pour la création de recette (inclut les ingrédients requis)
class RecipeCreate(RecipeBase):
    required_ingredients: List[RecipeIngredientCreate] = []

# Schéma pour la mise à jour de recette
class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)
    servings: Optional[int] = Field(None, ge=1)
    calories: Optional[int] = Field(None, ge=0)
    is_healthy: Optional[bool] = None
    is_public: Optional[bool] = None

# Schéma complet pour la lecture de recette (inclut les ingrédients requis)
class RecipeOut(RecipeBase):
    id: int
    owner_id: int # Correspond au modèle SQLAlchemy
    created_at: datetime
    # Relation Many-to-Many
    required_ingredients: List[RecipeIngredient] = [] 
    
    class Config:
        from_attributes = True

# Schéma de réponse pour la vérification de l'inventaire
class InventoryCheckResponse(BaseModel):
    recipe_id: int
    can_make: bool
    missing_items: List[dict] # Liste des ingrédients manquants et quantités
    available_items: List[dict] # Liste des ingrédients disponibles et quantités

    class Config:
        from_attributes = True


# --- SHOPPING LIST SCHEMAS ---

class ShoppingItemBase(BaseModel):
    item_name: str = Field(..., max_length=100)
    quantity: float = Field(1, gt=0)
    unit: str = Field(..., max_length=20)

class ShoppingItemCreate(ShoppingItemBase):
    pass

class ShoppingItemUpdate(BaseModel):
    item_name: Optional[str] = Field(None, max_length=100)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    is_purchased: Optional[bool] = None

class ShoppingItem(ShoppingItemBase):
    id: int
    shopping_list_id: int
    is_purchased: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ShoppingListBase(BaseModel):
    name: str = Field(..., max_length=100)

class ShoppingListCreate(ShoppingListBase):
    pass

class ShoppingList(ShoppingListBase):
    id: int
    owner_id: int # Correspond au modèle SQLAlchemy
    created_at: datetime
    items: List[ShoppingItem] = []

    class Config:
        from_attributes = True
