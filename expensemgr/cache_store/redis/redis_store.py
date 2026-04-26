from redis.commands.search.field import NumericField, TextField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis import Redis
import json
from typing import Generator, Annotated, Optional
from fastapi import Depends
from threading import RLock

from expensemgr.cache_store.redis.redis import RedisEngine
from expensemgr.cache_store.cache_store_base import CacheStore
from expensemgr.utils.logger import expense_mgr_logger

class RedisStore(CacheStore):
    # def __init__(cls):
        # super().__init__()
    _lock = RLock()
    _store_instance: Optional[Redis] = None
    _instance: Optional['RedisStore'] = None

    @classmethod
    def get_instance(cls) -> 'RedisStore':
        if cls._instance is None:
            cls._instance = super(RedisStore, cls).__new__(cls)
            cls._initalise()
        return cls._instance

    @classmethod
    def _initalise(cls):
        cls._store_instance = RedisEngine.get_redis_instance(db=0)

    @classmethod
    def set(cls, key, value):
        with cls._lock:
            try:
                cls._store_instance.ft("idx:code").dropindex(True)
            except cls._store_instance.exceptions.ResponseError:
                pass

            schema = (
                TextField("$.code", as_name = "code", sortable=True),
                NumericField("$.value", as_name = "value"),
                TextField("$.updated_at", as_name="updated_at")
            )
            indexCreated =  cls._store_instance.ft("idx:code").create_index(
                schema,
                definition=IndexDefinition(
                    prefix=["EXCHANGE_RATE:"], index_type=IndexType.JSON
                )
            )

            with open("expensemgr/utils/exchange_rates/exchange_rates.json") as f:
                exchange_rates = json.load(f)
                updated_at = exchange_rates.get("meta").get("last_updated_at")
                with cls._store_instance.pipeline() as pipe:
                    for code, code_data in exchange_rates.get("data").items():
                        code_data["updated_at"] = updated_at
                        pipe.hset(
                            name=f"EXCHANGE_RATE:{code}",
                            mapping=code_data,
                            
                        )
                    pipe.execute()
    
    @classmethod
    def get(cls, key):
        return cls._store_instance.hget(
                name=key,
                key="value"
            )
    
    @classmethod
    def exists(cls, key):
        return cls._store_instance.exists(
            [f"EXCHANGE_RATE:{key}"]
        )
    
    @classmethod
    def delete(cls, key):
        return cls._store_instance.delete(
            [f"EXCHANGE_RATE:{key}"]
        )

def get_redis_dependency() -> Generator['RedisStore', None, None]:
    try:
        yield RedisStore.get_instance()
    except Exception as e:
        expense_mgr_logger.logger.exception(f"Error creating redis instance! {e}")

redis_dependency = Annotated[CacheStore, Depends(get_redis_dependency)]