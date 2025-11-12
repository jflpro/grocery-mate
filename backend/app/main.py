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
    ai,  # ✅ Route AI
)

# --- Création des tables manquantes ---
create_db_tables_if_not_exists()

# --- Initialisation de l'application ---
app = FastAPI(
    title="GroceryMate API",
    description="API for managing groceries, shopping lists, recipes, and AI-powered features",
    version="1.1.0",
)

# --- Middleware CORS ---
origins = [
    "http://localhost:5173",              # Frontend local
    "http://127.0.0.1:5173",              # Variante loopback
    "http://grocery_frontend:5173",       # Service Docker frontend
    "http://grocery_backend:8000",        # Communication inter-conteneurs
    "http://host.docker.internal:5173",   # Docker Desktop Windows/macOS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inclusion des routes principales ---
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(shopping_lists.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(newsletter.router, prefix="/api")
app.include_router(ai.router, prefix="/api/ai")  # ✅ Route AI

# --- Route racine ---
@app.get("/")
def read_root():
    """Point d’entrée de l’API GroceryMate."""
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

# --- Vérification de santé ---
@app.get("/health")
def health_check():
    return {"status": "healthy"}
