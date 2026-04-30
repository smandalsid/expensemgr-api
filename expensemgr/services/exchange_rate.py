from sqlalchemy import select

from expensemgr.database.db import db_dependency
from expensemgr.database.models.expense import Currency
from expensemgr.routers.users import user_dependency
from expensemgr.cache_store.redis.redis_store import redis_dependency
from expensemgr.utils.logger import expense_mgr_logger
from expensemgr.schemas.exchange_rate import ExchangeRateOut


class ExchangeRateService:
    def __init__(
        self, db: db_dependency, user: user_dependency, redis: redis_dependency
    ):
        self.db = db
        self.user = user
        self.redis = redis

    @expense_mgr_logger.wrapper_logger(log_args=True)
    def get_exchange_rate_multiplier(
        self, user_curr_code: str, db_curr_code: str
    ) -> ExchangeRateOut:
        if user_curr_code == db_curr_code:
            return ExchangeRateOut(
                user_curr_code=user_curr_code,
                db_curr_code=db_curr_code,
                exchange_rate=1,
            )
        if user_curr_code == "USD":
            numerator = 1
        else:
            numerator = self.redis.get(key=f"EXCHANGE_RATE:{user_curr_code}")
        if db_curr_code == "USD":
            denominator = 1
        else:
            denominator = self.redis.get(key=f"EXCHANGE_RATE:{db_curr_code}")
        exchange_rate = ExchangeRateOut(
            user_curr_code=user_curr_code,
            db_curr_code=db_curr_code,
            exchange_rate=float(numerator) / float(denominator),
        )
        return exchange_rate
