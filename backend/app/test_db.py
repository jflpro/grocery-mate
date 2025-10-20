# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import ingredients, recipes, shopping_lists, seed, auth  # <-- Ajout du router auth

# --- Création des tables à partir des modèles SQLAlchemy ---
Base.metadata.create_all(bind=engine)

# --- Initialisation de l'application FastAPI ---
app = FastAPI(
    title="GroceryMate API",
    description="API for managing groceries, shopping lists, and recipes",
    version="1.0.0"
)

# --- Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inclusion des routes avec le préfixe /api ---
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(shopping_lists.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(auth.router, prefix="/api")  # <-- Route auth ajoutée

# --- Route principale (page d'accueil API) ---
@app.get("/")
def read_root():
    return {
        "message": "Welcome to GroceryMate API",
        "docs": "/docs",
        "redoc": "/redoc",
        "seed_endpoint": "/api/seed/"
    }

# --- Vérification de santé (health check) ---
@app.get("/health")
def health_check():
    return {"status": "healthy"}
