from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db
from app.crud import crud_auth

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Crée un nouvel utilisateur.
    Vérifie si l'email existe déjà et hache le mot de passe avant de sauvegarder.
    """
    # 1. Vérifier si l'utilisateur existe déjà
    db_user = crud_auth.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # 2. Hacher le mot de passe
    hashed_password = crud_auth.get_password_hash(user_in.password)
    user_in.password = hashed_password # Met à jour le schéma avec le hash

    # 3. Créer l'utilisateur dans la base de données
    return crud_auth.create_user(db=db, user=user_in)


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Authentifie l'utilisateur via le formulaire OAuth2 et génère un token JWT.
    """
    # 1. Authentifier l'utilisateur
    user = crud_auth.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 2. Créer le token d'accès
    access_token_expires = timedelta(minutes=crud_auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = crud_auth.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    
    # 3. Retourner le token
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserOut)
def read_users_me(
    # Utilisation de la dépendance renommée dans crud_auth.py
    current_user: models.User = Depends(crud_auth.get_current_active_user)
):
    """
    Récupère les informations de l'utilisateur actuellement authentifié.
    """
    return current_user
