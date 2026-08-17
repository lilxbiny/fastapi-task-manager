from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut
from app.services.auth import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_in)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm exposes the submitted identifier as `username`
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)
