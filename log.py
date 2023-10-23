import logging
import logging.handlers


RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"
DEFAULT_FORMAT = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"

# when debugging
#LEVEL = logging.DEBUG
# when operating
LEVEL = logging.CRITICAL



def set_logger(log_path) -> logging.Logger:

    try:
        from rich.logging import RichHandler
        logging.basicConfig(
            format=DEFAULT_FORMAT,
            handlers=[RichHandler(rich_tracebacks=True)]
        )
        logger = logging.getLogger("rich")
    except:
        logging.basicConfig(
            format=DEFAULT_FORMAT
        )

        logger = logging.getLogger()

    logger.setLevel(LEVEL)
    if log_path is not None:
        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
        logger.addHandler(file_handler)
        
    return logger


'''
exception handler

--- usage ---
import sys

if __name__ == '__main__':
    sys.excepthook  = handle_exception
'''

def handle_exception(exc_type, exc_value, exc_traceback):
    logger = logging.getLogger("rich")

    logger.error("Unexpected exception",
                 exc_info=(exc_type, exc_value, exc_traceback))
    
