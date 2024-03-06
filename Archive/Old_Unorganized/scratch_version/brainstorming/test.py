import logging
import functools

# Configure logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M')

# Create logger
logger = logging.getLogger(__name__)

# Create decorator
def log_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("An error occurred in function %s: %s", func.__name__, str(e))
            raise
    return wrapper


class Test:

    @log_exceptions
    def throw_exception(self, exception):
        if not issubclass(exception, BaseException):
            raise TypeError(f"{exception} is not a valid exception type.")
        raise exception("This is a test exception.")
