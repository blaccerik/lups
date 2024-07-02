import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def log_time(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        logger.warning(f'Function {func.__name__.rjust(24)} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper
