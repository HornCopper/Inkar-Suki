import time
import functools
from sgtpyutils.logger import logger


def use_log(template: callable = lambda func, args, result: f'{func} call [{args}] complete with result:{result}'):
    def decorator(func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            msg = template(func, args, result)
            logger.debug(msg)
            return result
        return wrapper
    return decorator


def use_retry(max_attempts: int = 0, delay: int = int(1e3)):
    def decorator(func: callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = {'v': 0}

            def run_once(*args, **kwargs):
                try:
                    return (True, func(*args, **kwargs))
                except Exception as ex:
                    attempts['v'] += 1
                    logger.warning(
                        f"{func.__name__} run failed({ex}) {attempts['v']}/{max_attempts} times.")
                    time.sleep(int(delay/1e3))
                    if attempts['v'] > max_attempts and max_attempts > 0:
                        raise ex
                    return (False, None)
            while True:
                success, result = run_once(*args, **kwargs)
                if success:
                    return result
        return wrapper
    return decorator
