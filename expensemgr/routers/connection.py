from fastapi import APIRouter, status, HTTPException

from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.database.db import db_dependency
from expensemgr.services.users import user_dependency
from expensemgr.schemas.connection import ConnectionBase
from expensemgr.services.connection import ConnectionService

router = APIRouter(
    prefix="/connection",
    tags=["connection"]
)

@router.get("", status_code=status.HTTP_200_OK)
@expense_mgr_logger.wrapper_logger(log_args=False)
def get_connection_status(user:user_dependency, db: db_dependency, connection: ConnectionBase):
    try:
        return ConnectionService(db=db, user=user).get_connection_status(connection=connection)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Failed to get connection status! {str(e)}')



@router.post("", status_code=status.HTTP_201_CREATED)
@expense_mgr_logger.wrapper_logger(log_args=False)
def create_connection(user: user_dependency, db: db_dependency, connection: ConnectionBase):
    try:
        return ConnectionService(db=db, user=user).create_connection(connection=connection)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Failed to create connection! {str(e)}')