from fastapi import APIRouter, status

from expensemgr.database.db import db_dependency
from expensemgr.services.users import user_dependency
from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.services.aggregate import AggregateService
from expensemgr.schemas.aggregate import AggregateShareOut

router = APIRouter(
    prefix="/aggregate",
    tags=["aggregate"],
)


@router.get(
    "/get_all", status_code=status.HTTP_200_OK, response_model=list[AggregateShareOut]
)
@expense_mgr_logger.wrapper_logger(log_args=False)
def get_aggregate(db: db_dependency, user: user_dependency):
    return AggregateService(db=db, user=user).get_aggregate()


@router.put("/settle", status_code=status.HTTP_202_ACCEPTED)
@expense_mgr_logger.wrapper_logger(log_args=False)
def settle_aggregate(db: db_dependency, user: user_dependency, settle_with_user_key: int):
    return AggregateService(db=db, user=user).settle_aggregate(settle_with_user_key=settle_with_user_key)
