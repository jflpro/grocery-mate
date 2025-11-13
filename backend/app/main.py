from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_tables_if_not_exists
from app.routers import (
    ingredients,
    recipes,
    shopping_lists,
    seed,
    auth,
    newsletter,
    ai,
)

# --- Création des tables ---
create_db_tables_if_not_exists()

# --- App FastAPI ---
app = FastAPI(
    title="GroceryMate API",
    description="API for managing groceries, shopping lists, recipes, and AI-powered features",
    version="1.1.0",
)

# ---------------------------------------------------------
# 🔐 CORS — VERSION SÉCURISÉE (PROD + DEV)
# ---------------------------------------------------------

origins = [
    # Développement local
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Production
    "http://91.99.21.21",
    "http://91.99.21.21:5173",  # ton front en prod
    "http://91.99.21.21:80",    # via Nginx Proxy Manager
    "http://91.99.21.21:443",   # HTTPS NPM

    # Réseau Docker interne (optionnel mais propre)
    "http://grocery_frontend",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # aucune wildcard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Routes API
# ---------------------------------------------------------

app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(shopping_lists.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(newsletter.router, prefix="/api")
app.include_router(ai.router, prefix="/api/ai")

# ---------------------------------------------------------
# Racine API
# ---------------------------------------------------------
@app.get("/")
def read_root():
    return {
        "message": "Welcome to GroceryMate API",
        "docs": "/docs",
        "redoc": "/redoc",
        "ai_routes": {
            "ask": "/api/ai/ask",
            "recipe": "/api/ai/recipe",
        },
        "seed_endpoint": "/api/seed/",
    }

# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}
