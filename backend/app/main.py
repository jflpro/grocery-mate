from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_tables_if_not_exists
from app.routers import ingredients, recipes, shopping_lists, seed, auth, newsletter

# --- Création des tables manquantes (sécurisé pour production) ---
create_db_tables_if_not_exists()

# --- Initialisation de l'application FastAPI ---
app = FastAPI(
    title="GroceryMate API",
    description="API for managing groceries, shopping lists, and recipes",
    version="1.0.0"
)

# --- Middleware CORS ---
# Autorise le frontend à accéder au backend dans Docker
origins = [
    "http://localhost:5173",              # Frontend local
    "http://127.0.0.1:5173",             # Variante loopback
    "http://grocery_frontend:5173",      # Nom du service Docker du frontend
    "http://grocery_backend:8000",       # Pour tests inter-conteneurs
    "http://host.docker.internal:5173",  # Cas Docker Desktop Windows/macOS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # Limité à ces origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Inclusion des routes avec le préfixe /api ---
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(shopping_lists.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(newsletter.router, prefix="/api")

# --- Route principale ---
@app.get("/")
def read_root():
    return {
        "message": "Welcome to GroceryMate API",
        "docs": "/docs",
        "redoc": "/redoc",
        "seed_endpoint": "/api/seed/"
    }

# --- Vérification de santé ---
@app.get("/health")
def health_check():
    return {"status": "healthy"}
