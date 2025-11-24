# 📁 backend/app/routers/news.py
from datetime import datetime
from typing import List

import re
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import models, auth, schemas_news
from ..database import get_db

router = APIRouter(
    prefix="/news",
    tags=["News"],
)

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------


def _get_news_or_404(news_id: int, db: Session) -> models.News:
    article = db.query(models.News).filter(models.News.id == news_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found",
        )
    return article


def _get_news_by_slug_or_404(slug: str, db: Session) -> models.News:
    article = (
        db.query(models.News)
        .filter(
            models.News.slug == slug,
            models.News.is_published.is_(True),
        )
        .first()
    )
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News article not found",
        )
    return article


def _create_slug(base_title: str, db: Session) -> str:
    """
    Crée un slug unique à partir du titre.
    """
    slug = base_title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")

    if not slug:
        slug = "news"

    base_slug = slug
    counter = 1

    while (
        db.query(models.News)
        .filter(models.News.slug == slug)
        .first()
        is not None
    ):
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# --------------------------------------------------------------------
# Public endpoints
# --------------------------------------------------------------------


@router.get("/public", response_model=List[schemas_news.NewsPublic])
def list_public_news(
    limit: int = Query(3, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """
    Liste les news publiées, triées par date de publication décroissante.
    """
    articles = (
        db.query(models.News)
        .filter(models.News.is_published.is_(True))
        .order_by(models.News.published_at.desc())
        .limit(limit)
        .all()
    )
    return articles


@router.get("/public/{slug}", response_model=schemas_news.NewsPublic)
def get_public_news_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Récupère une news publiée par son slug.
    """
    article = _get_news_by_slug_or_404(slug, db)
    return article


# --------------------------------------------------------------------
# Admin endpoints (CRUD total)
# --------------------------------------------------------------------


@router.get(
    "/",
    response_model=List[schemas_news.News],
)
def list_news_admin(
    include_unpublished: bool = True,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Liste complète des news pour l'admin.
    """
    query = db.query(models.News)
    if not include_unpublished:
        query = query.filter(models.News.is_published.is_(True))

    return query.order_by(models.News.created_at.desc()).all()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas_news.News,
)
def create_news(
    news_in: schemas_news.NewsCreate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Crée un article de news (brouillon ou publié directement).
    Le slug est généré automatiquement à partir du titre.
    """
    slug = _create_slug(news_in.title, db)

    published_at = None
    if news_in.is_published:
        published_at = datetime.utcnow()

    article = models.News(
        title=news_in.title,
        slug=slug,
        summary=news_in.summary,
        content=news_in.content,
        image_url=news_in.image_url,
        is_published=news_in.is_published,
        published_at=published_at,
        author_id=current_admin.id,
    )

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.put(
    "/{news_id}",
    response_model=schemas_news.News,
)
def update_news(
    news_id: int,
    news_in: schemas_news.NewsUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Met à jour un article de news.
    Si le titre change, on recalcule un slug unique.
    """
    article = _get_news_or_404(news_id, db)

    data = news_in.model_dump(exclude_unset=True)

    # Si le titre change, recalculer un slug unique
    if "title" in data and data["title"] and data["title"] != article.title:
        article.slug = _create_slug(data["title"], db)

    # Appliquer les autres champs
    for field, value in data.items():
        setattr(article, field, value)

    # Gestion de published_at
    if "is_published" in data:
        if data["is_published"] and not article.published_at:
            article.published_at = datetime.utcnow()
        # Si on dé-publie, on garde published_at (historique)

    db.commit()
    db.refresh(article)
    return article


@router.delete(
    "/{news_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Supprime un article de news.
    """
    article = _get_news_or_404(news_id, db)
    db.delete(article)
    db.commit()
    return None
