# THIS MODULE WILL IMPORT THE NECESSARY LOGGERS

# Importing all necessary libraries

import logging
from udise_api_calls import configuration as api_config


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

    logger.addHandler(log_handler)

    return logger


def main(module_name):
    LOG_FROMAT = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    info_file = str(api_config.LOGS_PATH + "/info.log")
    debug_file = str(api_config.LOGS_PATH + "/debug.log")

    # INITIALIZE INFO AND DEBUG HANDLERS
    logger = init_logger(
        logger_name=module_name,
        formatter=LOG_FROMAT,
        handler_file=info_file,
        log_filter=logging.INFO,
    )
    logger = init_logger(
        logger_name=module_name,
        formatter=LOG_FROMAT,
        handler_file=debug_file,
        log_filter=logging.DEBUG,
    )

    # INITIALIZE CONSOLE HANDLER
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings+ go to console
    console_handler.setFormatter(LOG_FROMAT)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    main(module_name=__name__)
