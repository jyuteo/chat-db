import os
import logging

from datetime import datetime
from pathlib import Path

from logger import Logger


_logger_instance = None


def get_logger() -> Logger:
    global _logger_instance
    if _logger_instance is None:
        root_dir = Path(__file__).resolve().parent.parent
        log_dir = root_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filepath = os.path.join(log_dir, f"log_{timestamp}.txt")
        _logger_instance = Logger(
            log_filepath=log_filepath, is_master_log=True, stream_log_level=logging.INFO, file_log_level=logging.DEBUG
        )
    return _logger_instance
