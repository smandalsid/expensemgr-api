from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from expensemgr.database.db import db_dependency
from expensemgr.schemas.users import UserOut
from expensemgr.services.auth import AuthService
from expensemgr.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

user_dependency = Annotated[dict, Depends(AuthService.get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserOut)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    user_model = UserService(db=db).get_user(user=user)
    if user_model is not None:
        return user_model
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User details not found"
        )
