from abc import ABC, abstractmethod
from typing import Any, Union, Optional
from threading import RLock
from redis import Redis

class CacheStore(ABC):

    def __init__(self):
       self._store_instance: Optional[Union[Redis]] = None
       self._lock = RLock()

    @abstractmethod
    def set(self, key: Union[str, int], value: Any):
        raise NotImplementedError

    @abstractmethod
    def get(self, key: Union[str, int]):
        raise NotImplementedError

    @abstractmethod
    def exists(self, key: Union[str, int]) -> bool:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, key: Union[str, int]):
        raise NotImplementedError