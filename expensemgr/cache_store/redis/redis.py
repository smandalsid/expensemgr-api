import redis
from redis import Redis
from redis.backoff import ExponentialBackoff
from redis import ConnectionPool
from redis.retry import Retry
from redis.exceptions import BusyLoadingError
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
import redis.exceptions

import json
from typing import Optional, Generator, Annotated
from fastapi import Depends

from expensemgr.utils.secrets import REDIS_CONN_STR
from expensemgr.utils.logger import expense_mgr_logger

class RedisEngine:
    _pool: Optional[ConnectionPool] = None
    _retry: Optional[Retry] = None
    _r: Optional[Redis] = None
    _instance: Optional['RedisEngine'] = None

    @classmethod
    def _initalise(cls, db: int):
        cls._pool = redis.ConnectionPool().from_url(
            REDIS_CONN_STR,
        )
        cls._retry = Retry(
            backoff=ExponentialBackoff(), 
            retries=3,
            supported_errors=(TimeoutError, ConnectionError))
        cls._r = redis.Redis(
            retry=cls._retry,
            retry_on_error=[BusyLoadingError],
            health_check_interval = 3,
            db=db
        ).from_pool(cls._pool)

    @classmethod
    def get_instance(cls, db: int) -> "RedisEngine":
        if cls._instance is None:
            cls._instance = super(RedisEngine, cls).__new__(cls)
            cls._initalise(db=db)
        return cls._instance
    
    @classmethod
    def get_redis_instance(cls, db: int = 0) -> Redis:
        redis_engine_instance = cls.get_instance(db=db)
        return redis_engine_instance._r

# def get_redis_dependency() -> Generator['Redis', None, None]:
#     try:
#         yield RedisEngine.get_redis_instance(db=0)
#     except Exception as e:
#         expense_mgr_logger.logger.exception(f"Error creating redis instance! {e}")

# redis_dependency = Annotated[Redis, Depends(get_redis_dependency)]



# try:
#     redis_instance.ft("idx:code").dropindex(True)
# except redis.exceptions.ResponseError:
#     pass

# schema = (
#     TextField("$.code", as_name = "code", sortable=True),
#     NumericField("$.value", as_name = "value"),
#     TextField("$.updated_at", as_name="updated_at")
# )
# indexCreated = redis_instance.ft("idx:code").create_index(
#     schema,
#     definition=IndexDefinition(
#         prefix=["EXCHANGE_RATE:"], index_type=IndexType.JSON
#     )
# )

# with open("expensemgr/utils/exchange_rates/exchange_rates.json") as f:
#     exchange_rates = json.load(f)
#     updated_at = exchange_rates.get("meta").get("last_updated_at")
#     with redis_instance.pipeline() as pipe:
#         for code, code_data in exchange_rates.get("data").items():
#             code_data["updated_at"] = updated_at
#             pipe.hset(
#                 name=f"EXCHANGE_RATE:{code}",
#                 mapping=code_data,
                
#             )
#         pipe.execute()

# print(
#     redis_instance.hgetall(
#         name="EXCHANGE_RATE:INR"
#     )
# )
# print(redis_instance.hget(
#     name="EXCHANGE_RATE:INR",
#     key="value"
# ))
