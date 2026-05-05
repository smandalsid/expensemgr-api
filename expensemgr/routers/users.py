from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from expensemgr.database.db import db_dependency
from expensemgr.schemas.users import UserOut
from expensemgr.services.auth import AuthService
from expensemgr.services.users import UserService
from expensemgr.utils.constants import auth_failed
from expensemgr.utils.logger import expense_mgr_logger

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

user_dependency = Annotated[dict, Depends(AuthService.get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserOut)
@expense_mgr_logger.wrapper_logger()
def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )

    user_model = UserService(db=db).get_user(user=user)
    if user_model is not None:
        return user_model
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User details not found"
        )

@router.put('/change_password', status_code=status.HTTP_200_OK)
@expense_mgr_logger.wrapper_logger()
def change_password(user: user_dependency, db: db_dependency, old_password: str, new_password: str, reenter_password: str):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    if new_password != reenter_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match!"
        )
    try:
        return UserService(db=db).change_password(
            user=user,
            old_password=old_password,
            new_password=new_password
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
