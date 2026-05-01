from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import select

from expensemgr.database.db import db_dependency
from expensemgr.database.models.users import User
from expensemgr.services.utils import ALGORITHM, SECRET_KEY

from .utils import bcrypt_context


class AuthService:
    def __init__(self, db: db_dependency):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> User:
        user: User = self.db.fetch_one_record(
            query=select(User).where(User.username == username)
        )
        if not user:
            return False
        if not bcrypt_context.verify(password, user.password):
            return False
        return user

    def create_access_token(
        self, username: str, user_key: int, is_admin: bool, expires_delta: timedelta
    ):
        encode = {"sub": username, "user_key": user_key, "is_admin": is_admin}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({"exp": expires})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    async def get_current_user(
        token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    ):
        try:
            payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            user_key: int = payload.get("user_key")
            is_admin: str = payload.get("is_admin")
            if username is None or user_key is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            else:
                return {
                    "username": username,
                    "user_key": user_key,
                    "is_admin": is_admin,
                }
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
