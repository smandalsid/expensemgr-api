from fastapi import APIRouter, status

from expensemgr.routers.users import user_dependency
from expensemgr.database.db import db_dependency
from expensemgr.cache_store.redis.redis_store import redis_dependency
from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.services.exchange_rate import ExchangeRateService
from expensemgr.schemas.exchange_rate import ExchangeRateOut

router = APIRouter(prefix="/exchange_rate", tags=["exchange_rate"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=ExchangeRateOut)
@expense_mgr_logger.wrapper_logger(log_args=True)
def get_exchange_rate_multiplier(
    db: db_dependency,
    user: user_dependency,
    redis: redis_dependency,
    user_curr_code: str,
    db_curr_code: str,
):
    exchange_rate = ExchangeRateService(
        db=db, user=user, redis=redis
    ).get_exchange_rate_multiplier(
        user_curr_code=user_curr_code, db_curr_code=db_curr_code
    )
    return exchange_rate
