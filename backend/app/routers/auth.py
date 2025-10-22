from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, auth # Importez le module 'auth' pour les fonctions de service
from app.database import get_db
from app.utils import security # Importez le module 'security' pour la création de token

# Définition du routeur avec le préfixe /auth
router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

# --- 1. Route d'Enregistrement (Register) ---

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur. Lève une erreur 400 si l'email existe déjà."""
    # Vérifier si l'utilisateur existe déjà
    db_user = auth.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Créer l'utilisateur 
    return auth.create_user(db=db, user=user_in)

# --- 2. Route de Connexion (Token) ---

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    # FastAPI utilise OAuth2PasswordRequestForm pour lire l'email/username et le mot de passe depuis le corps du formulaire (form-data)
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
):
    """
    Authentifie l'utilisateur et génère un jeton d'accès JWT.
    Le 'username' dans le form_data sera utilisé comme 'email' dans notre implémentation.
    """
    # Utiliser form_data.username comme email pour l'authentification
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user:
        # Lève l'exception standard pour l'authentification OAuth2
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Définir l'expiration du jeton (par exemple, 30 minutes)
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Créer le jeton d'accès
    access_token = security.create_access_token(
        data={"user_id": str(user.id)}, # Utiliser l'ID de l'utilisateur comme sujet du token
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# --- 3. Route de Test Utilisateur Actif ---

# Le chemin est "/me" 
@router.get("/me", response_model=schemas.UserOut)
async def read_users_me(current_user: schemas.UserOut = Depends(auth.get_current_active_user)):
    """Retourne l'utilisateur actuellement authentifié."""
    return current_user

# --- 4. Route de Déconnexion (Logout) ---

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(current_user: schemas.UserOut = Depends(auth.get_current_active_user)):
    """
    Gère la déconnexion. 
    Pour les tokens JWT (stateless), cela indique au client de supprimer le token 
    et confirme que l'utilisateur était bien authentifié.
    """
    # L'utilisateur est authentifié si nous atteignons ce point.
    # L'action réelle (suppression du token) doit être effectuée côté client (frontend).
    return {"message": "Successfully logged out. Client token should be deleted."}
