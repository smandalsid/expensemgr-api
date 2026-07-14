from fastapi import APIRouter, status

from expensemgr.routers.users import user_dependency
from expensemgr.database.db import db_dependency

from expensemgr.services.division_by import DivisionByService

router = APIRouter(
    prefix='/divide_by',
    tags=['divide_by']
)

@router.get('', status_code=status.HTTP_200_OK)
def get_all_division_by(user: user_dependency, db: db_dependency):
    pass