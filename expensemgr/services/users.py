from fastapi import HTTPException, status, Depends
from typing import Annotated

from expensemgr.database.db import db_dependency
from expensemgr.schemas.users import CreateUser, UserOut
from expensemgr.database.models.users import User
from expensemgr.services.auth import AuthService

from .utils import bcrypt_context

user_dependency = Annotated[dict, Depends(AuthService.get_current_user)]

class UserService:

    def __init__(self, db: db_dependency):
        self.db = db

    def create_user(self, create_user: CreateUser) -> UserOut:

        if self.db.query(User).filter(User.username == create_user.username).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
        if self.db.query(User).filter(User.phone_number == create_user.phone_number).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already exists")
        if self.db.query(User).filter(User.email == create_user.email).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        if create_user.password!=create_user.retyped_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password and retyped password do not match")
        
        
        create_user_model = User(
            email = create_user.email,
            first_name = create_user.first_name,
            last_name = create_user.last_name,
            username = create_user.username,
            password = bcrypt_context.hash(create_user.password),
            phone_number = create_user.phone_number
        )
        self.db.add(create_user_model)
        self.db.commit()

        user = self.db.query(User).filter(User.user_key == create_user_model.user_key).first()
        return user

    def get_user(self, user: user_dependency):

        user_response = self.db.query(User).filter(User.user_key == user.get('user_key')).first()
        if user_response is not None:
            return user_response
        else:
            return None