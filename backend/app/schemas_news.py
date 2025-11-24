# 📁 backend/app/schemas_news.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------
# Base
# --------------------------------------------------------------------


class NewsBase(BaseModel):
    title: str = Field(..., max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: str
    image_url: Optional[str] = None
    is_published: bool = False


# --------------------------------------------------------------------
# Payloads d'écriture (admin)
# --------------------------------------------------------------------


class NewsCreate(NewsBase):
    """Payload pour créer une news (admin)."""
    pass


class NewsUpdate(BaseModel):
    """Payload pour mettre à jour une news (admin)."""
    title: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None


# --------------------------------------------------------------------
# Réponses complètes (admin)
# --------------------------------------------------------------------


class News(NewsBase):
    id: int
    slug: str
    author_id: Optional[int] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --------------------------------------------------------------------
# Vue publique
# --------------------------------------------------------------------


class NewsPublic(BaseModel):
    """Vue utilisée sur la landing publique."""
    id: int
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
