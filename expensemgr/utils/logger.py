import logging
from functools import wraps
# from typing import 
from datetime import datetime, timezone
from typing import Optional

class BaseLogger:
    def __init__(self, name: Optional[str]):
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(level=logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(f"%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
        self.logger.addHandler(stream_handler)

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        if self.logger is None:
            return self.__new__(name)

    def wrapper_logger(self, log_args: bool = False, log_result: bool = False):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    start_time = datetime.now(timezone.utc)
                    if log_args:
                        self.logger.info(f'{func.__name__} called with args - {args}')
                    result = func(*args, **kwargs)
                    if log_result:
                        self.logger.info(f'{func.__name__} returned - {result}')
                    end_time = datetime.now(timezone.utc)
                    self.logger.info(f'{func.__name__} - Execution time: {end_time-start_time}')
                except Exception as e:
                    self.logger.exception(f'{func.__name__} - Exception occured: {str(e)}')
                    raise e
                return result
            return wrapper
        return decorator
                
expense_mgr_logger = BaseLogger(name='expense_mgr_logger')