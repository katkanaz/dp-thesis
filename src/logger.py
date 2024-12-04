import logging
from pathlib import Path


class CrashHandler(logging.Handler):
    """A logging handler that raises an exception when a log is emitted."""

    def emit(self, record):
        raise RuntimeError(self.format(record))


logger = logging.getLogger("logger")
logger.addHandler(CrashHandler())


def setup_logger(log_file: Path, log_level=logging.INFO):
    """
    Configure the global logger.

    :param log_file:
    :param log_level:
    :param log_format:
    """

    logger.handlers.clear()

    logger.setLevel(log_level)

    # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(modules)s - %(funcName)s - %(message)s")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s")

    log_file.parent.mkdir(exist_ok=True, parents=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


# __all__ = ["logger"]
