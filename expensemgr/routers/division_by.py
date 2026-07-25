from fastapi import APIRouter, status, HTTPException

from expensemgr.routers.users import user_dependency
from expensemgr.database.db import db_dependency

from expensemgr.services.division_by import DivisionByService, DivisionByException
from expensemgr.schemas.division_by import DivisionBy
from expensemgr.utils.constants import auth_failed

router = APIRouter(prefix="/divide_by", tags=["divide_by"])


@router.get("/get_all", status_code=status.HTTP_200_OK, response_model=list[DivisionBy])
def get_all_division_by(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=auth_failed
        )
    try:
        return DivisionByService(db=db).get_all_divsion_by()
    except DivisionByException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
