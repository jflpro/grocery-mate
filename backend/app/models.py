from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.functions import func

from .database import Base

# ====================================================================
# AUTHENTICATION & USER MODELS
# ====================================================================


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)  # Password hash
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships (inverse relations)
    ingredients = relationship("Ingredient", back_populates="owner")
    recipes = relationship("Recipe", back_populates="owner")
    shopping_lists = relationship("ShoppingList", back_populates="owner")


# ====================================================================
# INGREDIENT MODEL (Inventory)
# ====================================================================


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key to the user (owner)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="ingredients")


# ====================================================================
# RECIPE MODEL
# ====================================================================


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    instructions = Column(String, nullable=False)

    prep_time = Column(Integer)  # Preparation time in minutes
    cook_time = Column(Integer)  # Cooking time in minutes
    servings = Column(Integer)
    calories = Column(Integer, nullable=True)
    is_healthy = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key to the user (creator/owner)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="recipes")

    # Relationship to the ingredients required for the recipe
    required_ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


# ====================================================================
# RECIPE INGREDIENT MODEL
# ====================================================================


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to the recipe
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)

    # Details of the required ingredient
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

    recipe = relationship("Recipe", back_populates="required_ingredients")


# ====================================================================
# SHOPPING LIST MODEL
# ====================================================================


class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="shopping_lists")

    # Relationship to the shopping items
    items = relationship(
        "ShoppingItem",
        back_populates="shopping_list",
        cascade="all, delete-orphan",
    )


# ====================================================================
# SHOPPING LIST ITEM MODEL
# ====================================================================


class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    unit = Column(String, nullable=False)
    is_purchased = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False)
    shopping_list = relationship("ShoppingList", back_populates="items")
