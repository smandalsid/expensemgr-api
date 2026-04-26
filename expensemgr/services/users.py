from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import insert, select

from expensemgr.database.db import db_dependency
from expensemgr.database.models.users import User
from expensemgr.schemas.users import CreateUser, UserOut
from expensemgr.services.auth import AuthService
from expensemgr.services.utils import bcrypt_context
from expensemgr.utils.logger import expense_mgr_logger

user_dependency = Annotated[dict, Depends(AuthService.get_current_user)]


class UserService:

    def __init__(self, db: db_dependency):
        self.db = db

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def create_user(self, create_user: CreateUser) -> UserOut:
        validation_1 = select(User).where(User.username == create_user.username)
        if self.db.fetch_one_record(query=validation_1):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
            )
        validation_2 = select(User).where(User.phone_number == create_user.phone_number)
        if self.db.fetch_one_record(query=validation_2):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already exists",
            )
        validation_3 = select(User).where(User.email == create_user.email)
        if self.db.fetch_one_record(query=validation_3):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )
        if create_user.password != create_user.retyped_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password and retyped password do not match",
            )

        insert_user_stmt = insert(User).values(
            email=create_user.email,
            first_name=create_user.first_name,
            last_name=create_user.last_name,
            username=create_user.username,
            password=bcrypt_context.hash(create_user.password),
            phone_number=create_user.phone_number,
        )
        result = self.db.execute_query(insert_user_stmt)

        user = self.db.fetch_one_record(
            select(User).where(User.user_key == result.inserted_primary_key[0])
        )
        return user

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_user(self, user: user_dependency):
        user = self.db.fetch_one_record(
            select(User).where(User.user_key == user.get("user_key"))
        )
        if user is not None:
            return user
        else:
            return None
