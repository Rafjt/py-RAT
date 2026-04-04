import logging
from pathlib import Path


def setup_logger():
    base_dir = Path(__file__).resolve().parent
    log_path = base_dir / "rat.log"

    logger = logging.getLogger("rat")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path)

    formatter = logging.Formatter("[%(asctime)s] - %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
