# THIS MODULE WILL IMPORT THE NECESSARY LOGGERS

# Importing all necessary libraries

import logging
from functools import wraps
import inspect
from udise_api_calls import api_config


def init_logger(
    logger_name: str, formatter: logging.Formatter, handler_file: str, log_filter
):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # CONFIGURIG THE HANDLER
    log_handler = logging.FileHandler(handler_file)
    log_handler.setLevel(log_filter)
    log_handler.addFilter(lambda r: r.levelno == log_filter)
    log_handler.setFormatter(formatter)

    if not log_handler in logger.handlers:
        logger.addHandler(log_handler)

    return logger


def log_documentation_decorator(function):

    @wraps(function)
    def wrapper(*args, **kwargs):
        LOGGER = logging.getLogger(function.__module__)
        source_file = inspect.getsourcefile(function)
        LOGGER.info(f"Running the code: {source_file}")
        LOGGER.debug(f"Running the code: {source_file}")

        result = function(*args, **kwargs)

        LOGGER.info("Run complete.")
        LOGGER.debug("Run complete.")

        return result

    return wrapper


@log_documentation_decorator
def main(module_name):
    LOG_FROMAT = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    info_file = api_config.LOGS_PATH / "info.log"
    debug_file = api_config.LOGS_PATH / "debug.log"

    # INITIALIZE INFO AND DEBUG HANDLERS
    LOGGER = init_logger(
        logger_name=module_name,
        formatter=LOG_FROMAT,
        handler_file=info_file,
        log_filter=logging.INFO,
    )
    LOGGER = init_logger(
        logger_name=module_name,
        formatter=LOG_FROMAT,
        handler_file=debug_file,
        log_filter=logging.DEBUG,
    )

    # INITIALIZE CONSOLE HANDLER
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings+ go to console
    console_handler.setFormatter(LOG_FROMAT)

    if not console_handler in LOGGER.handlers:
        LOGGER.addHandler(console_handler)

    return LOGGER


if __name__ == "__main__":
    main(module_name=__name__)
