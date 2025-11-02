from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import timedelta

from ..database.db import db_dependency
from ..schemas.users import CreateUser, UserOut
from ..services.users import *
from..services.auth import AuthService
from ..schemas.auth import Token

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def create_user(db: db_dependency, create_user: CreateUser):
    service = UserService(db=db)
    return service.create_user(create_user=create_user)
    
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    service = AuthService(db)
    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    token = service.create_access_token(user.username, user.user_key, user.is_admin, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}
