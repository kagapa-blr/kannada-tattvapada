# app/utils/logger.py

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name: str, log_file: str = None, level=logging.DEBUG) -> logging.Logger:
    """
    Sets up a logger that writes all logs to file and only info/warnings/errors to console.

    :param name: Logger name.
    :param log_file: Optional log file name. Defaults to {name}.log.
    :param level: Logger level (default DEBUG).
    :return: Logger instance.
    """
    # Date-based folder: logs/dd-mm-yyyy/
    today_str = datetime.now().strftime("%d-%m-%Y")
    log_dir = os.path.join("logs", today_str)
    os.makedirs(log_dir, exist_ok=True)

    # Log file path
    log_file = log_file or f"{name}.log"
    log_path = os.path.join(log_dir, log_file)

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if logger already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")

    # File handler — accepts DEBUG and above
    file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler — only INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
