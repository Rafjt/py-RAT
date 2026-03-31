import logging


def setup_logger():
    logger = logging.getLogger("rat")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler("rat.log")

    formatter = logging.Formatter("[%(asctime)s] - %(levelname)s: %(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
