import logging
import os
from datetime import datetime

# Create dated log folder
today = datetime.now().strftime("%Y-%m-%d")
LOG_DIR = os.path.join("logs", today)
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str):
    """
    Returns a configured logger.
    Logs:
        - All levels to file (DEBUG, INFO, ERROR)
        - INFO and above to console
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger  # Avoid duplicate handlers

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(f"{LOG_DIR}/{name}.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler: info and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
