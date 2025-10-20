from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# --------------------------
# User model
# --------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)  # longueur sûre pour bcrypt
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations avec les autres tables
    ingredients = relationship("Ingredient", back_populates="owner")
    shopping_lists = relationship("ShoppingList", back_populates="owner")
    recipes = relationship("Recipe", back_populates="owner")

# --------------------------
# Ingredient model
# --------------------------
class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)
    location = Column(String, nullable=False)
    quantity = Column(Float, default=0)
    unit = Column(String, nullable=False)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign key vers User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="ingredients")

# --------------------------
# ShoppingList model
# --------------------------
class ShoppingList(Base):
    __tablename__ = "shopping_lists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key vers User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="shopping_lists")

    items = relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan")

# --------------------------
# ShoppingItem model
# --------------------------
class ShoppingItem(Base):
    __tablename__ = "shopping_items"

    id = Column(Integer, primary_key=True, index=True)
    shopping_list_id = Column(Integer, ForeignKey("shopping_lists.id"))
    item_name = Column(String, nullable=False)
    quantity = Column(Float, default=1)
    unit = Column(String, nullable=False)
    is_purchased = Column(Boolean, default=False)

    shopping_list = relationship("ShoppingList", back_populates="items")

# --------------------------
# Recipe model
# --------------------------
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    ingredients = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    prep_time = Column(Integer)
    servings = Column(Integer, default=2)
    calories = Column(Integer, nullable=True)
    is_healthy = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign key vers User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="recipes")
