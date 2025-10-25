from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import ingredients, recipes, shopping_lists, seed, auth

# --- Création des tables à partir des modèles SQLAlchemy ---
Base.metadata.create_all(bind=engine)

# --- Initialisation de l'application FastAPI ---
app = FastAPI(
    title="GroceryMate API",
    description="API for managing groceries, shopping lists, and recipes",
    version="1.0.0"
)

# --- Middleware CORS ---
# Permet au frontend de communiquer avec le backend, même si ports différents
origins = [
    "http://localhost:5173",           # Frontend Vite local
    "http://127.0.0.1:5173",           # Variante localhost
    "http://localhost:3000",           # Si React ou autre port utilisé
    "http://host.docker.internal:5173" # Frontend Docker
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Origines autorisées
    allow_credentials=True,   # Permet cookies/headers auth
    allow_methods=["*"],      # Toutes les méthodes HTTP (GET, POST, PUT, DELETE…)
    allow_headers=["*"],      # Tous les headers autorisés
)

# --- Inclusion des routes avec le préfixe /api ---
app.include_router(ingredients.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(shopping_lists.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

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
