# 📁 app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_tables_if_not_exists
from .routers import (
    auth,
    ingredients,
    recipes,
    shopping_lists,
    seed,
    newsletter,
    ai,
)

# --------------------------------------------------------------------
# Application FastAPI
# --------------------------------------------------------------------
app = FastAPI(
    title="GroceryMate API",
    version="1.0.0",
    description="Backend API pour l'application GroceryMate",
)

# --------------------------------------------------------------------
# Configuration CORS
# --------------------------------------------------------------------
origins = [
    # Dev local
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1",

    # Prod
    "https://gro-mate.tech",
    "https://www.gro-mate.tech",
    "https://api.gro-mate.tech",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------
# Hooks de démarrage
# --------------------------------------------------------------------
@app.on_event("startup")
def on_startup() -> None:
    """Création des tables si elles n'existent pas."""
    create_db_tables_if_not_exists()


# --------------------------------------------------------------------
# Endpoint de santé
# --------------------------------------------------------------------
@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok"}


# --------------------------------------------------------------------
# Routers API
# --------------------------------------------------------------------
# Authentification / JWT / utilisateurs
app.include_router(auth.router, prefix="/api")

# Ingrédients
app.include_router(ingredients.router, prefix="/api")

# Recettes
app.include_router(recipes.router, prefix="/api")

# Listes de courses
app.include_router(shopping_lists.router, prefix="/api")

# Seed global (données de démo)
# => /api/seed/
app.include_router(seed.router, prefix="/api")

# Newsletter
app.include_router(newsletter.router, prefix="/api")

# IA (endpoints spécifiques IA)
# => /api/ai/...
app.include_router(ai.router, prefix="/api/ai")
