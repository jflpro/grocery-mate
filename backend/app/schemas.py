from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

# --- BASE / CORE SCHEMAS ---


# Base schema for the user
class UserBase(BaseModel):
    email: EmailStr
    username: str


# Schema for user creation (registration)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Full user schema (used for /auth/me)
class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Simple response schema
class MessageResponse(BaseModel):
    """Standard response for confirmations and error messages."""
    message: str


# --- AUTH SCHEMAS ---


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# --- INGREDIENT SCHEMAS (Personal inventory) ---


class IngredientBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    location: str = Field(..., max_length=50)
    quantity: float = Field(..., gt=0)
    unit: str = Field(..., max_length=20)
    expiry_date: Optional[date] = None


# Schema for ingredient creation
class IngredientCreate(IngredientBase):
    pass


# Schema for ingredient update
class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=50)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    expiry_date: Optional[date] = None


# Full schema for ingredient reading
class Ingredient(IngredientBase):
    id: int
    owner_id: int  # Corresponds to the SQLAlchemy model
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- RECIPE INGREDIENT SCHEMAS (Required ingredients for ONE recipe) ---


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
    # WARNING: Renamed from 'name' to 'title' to match the SQLAlchemy model
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    # Removed the 'ingredients' (Text) field because it is handled by the relation
    # with RecipeIngredient instead
    instructions: str
    prep_time: Optional[int] = Field(None, ge=0)
    cook_time: Optional[int] = Field(None, ge=0)  # Additional cook_time
    servings: int = Field(2, ge=1)
    calories: Optional[int] = Field(None, ge=0)
    is_healthy: bool = True
    is_public: bool = False  # NEW: To share the recipe


# Schema for recipe creation (includes required ingredients)
class RecipeCreate(RecipeBase):
    required_ingredients: List[RecipeIngredientCreate] = []


# Schema for recipe update
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


# Full schema for recipe reading (includes required ingredients)
class RecipeOut(RecipeBase):
    id: int
    owner_id: int  # Corresponds to the SQLAlchemy model
    created_at: datetime
    # Relation: required ingredients for this recipe
    required_ingredients: List[RecipeIngredient] = []

    class Config:
        from_attributes = True


# Schema for inventory check response
class InventoryCheckResponse(BaseModel):
    recipe_id: int
    can_make: bool
    # List of missing ingredients and quantities
    missing_items: List[dict]
    # List of available ingredients and quantities
    available_items: List[dict]

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
    owner_id: int  # Corresponds to the SQLAlchemy model
    created_at: datetime
    items: List[ShoppingItem] = []

    class Config:
        from_attributes = True
