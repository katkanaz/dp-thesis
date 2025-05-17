import logging
from tqdm import tqdm
from pathlib import Path


class CrashHandler(logging.Handler):
    """A logging handler that raises an exception when a log is emitted."""

    def emit(self, record):
        raise RuntimeError(self.format(record))


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            message = self.format(record)
            tqdm.write(message)
            self.flush()
        except Exception:
            self.handleError(record)


logger = logging.getLogger("logger")
logger.addHandler(CrashHandler())


def setup_logger(log_file: Path, log_level=logging.INFO):
    """
    Configure the global logger.

    :param log_file: Path to log file
    :param log_level: Logging level; default logging.INFO
    """

    logger.handlers.clear()

    logger.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s")

    log_file.parent.mkdir(exist_ok=True, parents=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = TqdmLoggingHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.propagate = False
