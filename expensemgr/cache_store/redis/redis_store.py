from upstash_redis import Redis
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
    _instance: Optional["RedisStore"] = None

    @classmethod
    def get_instance(cls) -> "RedisStore":
        if cls._instance is None:
            cls._instance = super(RedisStore, cls).__new__(cls)
            cls._initalise()
        return cls._instance

    @classmethod
    def _initalise(cls):
        cls._store_instance = RedisEngine.get_redis_instance()

    @classmethod
    def set(cls):
        with cls._lock:
            with open("expensemgr/utils/exchange_rates/exchange_rates.json") as f:
                exchange_rates = json.load(f)
                updated_at = exchange_rates.get("meta").get("last_updated_at")
                pipeline = cls._store_instance.pipeline()
                for code, code_data in exchange_rates.get("data").items():
                    code_data["updated_at"] = updated_at
                    pipeline.hset(
                        f"EXCHANGE_RATE:{code}",
                        values=code_data,
                    )
                pipeline.exec()

    @classmethod
    def get(cls, key):
        return cls._store_instance.hget(key, "value")

    @classmethod
    def exists(cls, key):
        return cls._store_instance.exists(f"EXCHANGE_RATE:{key}")

    @classmethod
    def delete(cls, key):
        return cls._store_instance.delete(f"EXCHANGE_RATE:{key}")


def get_redis_dependency() -> Generator["RedisStore", None, None]:
    try:
        yield RedisStore.get_instance()
    except Exception as e:
        expense_mgr_logger.logger.exception(f"Error creating redis instance! {e}")


redis_dependency = Annotated[CacheStore, Depends(get_redis_dependency)]
