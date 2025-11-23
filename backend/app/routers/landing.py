from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, auth, schemas_admin
from ..database import get_db

router = APIRouter(
    prefix="/landing",
    tags=["Landing"],
)


def _get_singleton_landing(db: Session) -> models.LandingContent | None:
    """Retourne l’unique enregistrement de landing_content (ou None)."""
    return (
        db.query(models.LandingContent)
        .order_by(models.LandingContent.id.asc())
        .first()
    )


def _fallback_landing() -> schemas_admin.LandingContentResponse:
    """Contenu par défaut (mêmes textes que la landing statique actuelle)."""
    return schemas_admin.LandingContentResponse(
        id=0,
        hero_title="Smart Grocery Management",
        hero_subtitle=(
            "Track your inventory, avoid waste, and plan your recipes with a "
            "simple, modern web app."
        ),
        feature1_title="Real-time inventory",
        feature1_text="Know exactly what you have in your fridge and pantry, anytime.",
        feature2_title="Anti-waste by design",
        feature2_text="Track expiry dates and use ingredients before they go to waste.",
        feature3_title="Recipe-friendly",
        feature3_text="Link your ingredients to recipes and plan meals with confidence.",
        how1_title="Create your account",
        how1_text="Sign up in a few seconds and secure your personal space.",
        how2_title="Add your ingredients",
        how2_text=(
            "Save what you already have at home: name, quantity, location, expiry date."
        ),
        how3_title="Plan & shop smarter",
        how3_text="Build shopping lists and recipes based on your real inventory.",
        cta_title="Ready to take control of your kitchen?",
        cta_subtitle="Start with a simple account and keep your groceries under control.",
    )


# --------------------------------------------------------------------
# Public endpoint (pas d'auth)
# --------------------------------------------------------------------
@router.get("/public", response_model=schemas_admin.LandingContentResponse)
def get_public_landing_content(
    db: Session = Depends(get_db),
):
    """
    Public: contenu de la page d'accueil.
    Si aucun contenu en DB, renvoie des valeurs par défaut.
    """
    content = _get_singleton_landing(db)

    if content:
        return content

    return _fallback_landing()


# --------------------------------------------------------------------
# Admin endpoints (lecture + update)
# --------------------------------------------------------------------
@router.get("/admin", response_model=schemas_admin.LandingContentResponse)
def get_admin_landing_content(
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Admin: lire le contenu actuel de la landing (ou fallback si vide).
    """
    content = _get_singleton_landing(db)
    if content:
        return content

    # l’admin voit aussi le contenu par défaut s’il n’y a rien en base
    return _fallback_landing()


@router.put("/admin", response_model=schemas_admin.LandingContentResponse)
def update_landing_content(
    payload: schemas_admin.LandingContentUpdate,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth.get_current_admin_user),
):
    """
    Admin: mise à jour complète du contenu de la landing.
    On garantit qu'il n'y a qu'une seule ligne dans landing_content.
    """
    content = _get_singleton_landing(db)

    if not content:
        # création de la première version
        content = models.LandingContent(**payload.model_dump())
        db.add(content)
    else:
        # mise à jour champ par champ
        for field, value in payload.model_dump().items():
            setattr(content, field, value)

    db.commit()
    db.refresh(content)
    return content
