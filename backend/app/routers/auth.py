from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, auth
from app.database import get_db
from app.utils import security

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

# ---------------------------------------------------------
# 1. Register
# ---------------------------------------------------------

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """Crée un nouvel utilisateur. Lève 400 si l'email existe déjà."""
    db_user = auth.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return auth.create_user(db=db, user=user_in)


# ---------------------------------------------------------
# 2. Login / Token
# ---------------------------------------------------------

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    Authentifie l'utilisateur et génère un JWT.
    form_data.username = email (côté frontend tu envoies email dans 'username').
    """
    user = auth.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        data={"user_id": str(user.id)},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ---------------------------------------------------------
# 3. /me
# ---------------------------------------------------------

@router.get("/me", response_model=schemas.UserOut)
async def read_users_me(
    current_user = Depends(auth.get_current_active_user),
):
    """Retourne l'utilisateur actuellement authentifié."""
    return current_user


# ---------------------------------------------------------
# 4. Logout
# ---------------------------------------------------------

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(
    current_user = Depends(auth.get_current_active_user),
):
    """
    Pour JWT : il n'y a pas de vraie invalidation côté backend
    => le frontend doit juste supprimer le token stocké.
    """
    return {
        "message": "Successfully logged out. Client token should be deleted."
    }
