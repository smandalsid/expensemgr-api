from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import insert, select, update
from datetime import datetime, timezone

from expensemgr.database.db import db_dependency
from expensemgr.database.models.users import User
from expensemgr.schemas.users import CreateUser, UserOut
from expensemgr.services.auth import AuthService
from expensemgr.services.utils import bcrypt_context
from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.utils.constants import VersionActiveInd

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
        result = self.db.execute_query(query=insert_user_stmt)

        user = self.db.fetch_one_record(
            query=select(User).where(User.user_key == result.inserted_primary_key[0])
        )
        return user

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_user(self, user: user_dependency):
        user = self.db.fetch_one_record(
            query=select(User).where(User.user_key == user.get("user_key"))
        )
        if user is not None:
            return user
        else:
            return None

    @expense_mgr_logger.wrapper_logger()
    def change_password(
        self, 
        user: user_dependency,
        old_password: str,
        new_password: str
    ) -> UserOut:
        user_key = user.get("user_key")
        user = self.db.fetch_one_record(
            query=select(User.username.label("username")).where(User.user_key == user_key)
        )
        auth_service = AuthService(db=self.db)
        pass_match = auth_service.authenticate_user(username=user[0], password=old_password)

        if not pass_match:
            raise Exception('Old password incorrect!')
        
        update_user = update(
            User
        ).where(
            User.user_key == user_key,
            User.user_active_ind == VersionActiveInd.ACTIVE.value
        ).values(
            password = bcrypt_context.hash(new_password),
            meta_changed_dttm = datetime.now(timezone.utc)
        )
        udpated = self.db.execute_query(query=update_user).rowcount

        if udpated:
            return {'detail': 'Password changed!'}
        return {'detail': 'Password change failed for some reason!'}