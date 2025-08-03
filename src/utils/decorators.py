from functools import wraps
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from typing import Any, Callable

from src.logger import setup_logger
from src.settings import LOG_DIR

logger_1 = setup_logger(name="UtilsLogger", log_dir=f"{LOG_DIR}/utils_logs")
logger_2 = setup_logger(name="CreativeFabricaLog", log_dir=f"{LOG_DIR}/cre_fab_logs")

def selenium_exception_handler(func: Callable):
    '''This is decorator to catch exception of executing a function.'''
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            result = func(*args, **kwargs)
            return result
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException) as e:
            logger_2.error(f"Error {func.__name__} {e}")
            return 0
        except Exception as e:
            logger_2.error(f"Error {func.__name__} {e}")
            return 0
    return wrapper
