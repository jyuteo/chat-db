import os
import re
import sys
import json
import torch
import logging

from pathlib import Path
from typing import Dict, Union, Tuple
from logging import FileHandler, StreamHandler


class JsonFormatter(logging.Formatter):
    RECORD_DICT_KEYS = [
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "device",
    ]
    ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        record_dict = {
            "timestamp": self.formatTime(record, "%d-%m-%Y %H:%M:%S"),
            "level": record.levelname,
            "message": self.ANSI_ESCAPE_PATTERN.sub("", record.getMessage()),
        }
        for k, v in record.__dict__.items():
            if k not in self.RECORD_DICT_KEYS:
                record_dict[k] = v
        return json.dumps(record_dict)


class Logger:
    def __init__(
        self,
        log_filepath: str,
        is_master_log: bool = True,
        stream_log_level: int = logging.INFO,
        file_log_level: int = logging.DEBUG,
    ) -> None:
        self.log_filepath = log_filepath
        self.is_master_log = is_master_log
        self.stream_log_level = stream_log_level
        self.file_log_level = file_log_level
        self.logger = self._init_logger()

    def _init_logger(self) -> logging.Logger:
        if not os.path.exists(self.log_filepath):
            dir_path = Path(self.log_filepath).parent
            dir_path.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        sh = StreamHandler(sys.stdout)
        sh.setLevel(self.stream_log_level)

        fh = FileHandler(self.log_filepath, "w")
        fh.setLevel(self.file_log_level)

        json_formatter = JsonFormatter()
        sh.setFormatter(json_formatter)
        fh.setFormatter(json_formatter)

        if self.is_master_log:
            logger.addHandler(sh)
        logger.addHandler(fh)

        return logger

    def _convert_to_serializable(self, value):
        if isinstance(value, (int, float, str)):
            return value
        if isinstance(value, torch.Tensor):
            if value.dim() == 0:
                return value.item()
            elif value.dim() == 1:
                return value.tolist()
            else:
                return value.numpy().tolist()
        elif isinstance(value, list):
            return [self._convert_to_serializable(item) for item in value]
        elif isinstance(value, dict):
            return {key: self._convert_to_serializable(val) for key, val in value.items()}
        else:
            return str(value)

    def _process_logs(self, logs: Union[str, Dict]) -> Tuple[str, Dict]:
        if isinstance(logs, str):
            return logs, {}
        elif isinstance(logs, dict):
            logs = self._convert_to_serializable(logs)
            msg = logs.pop("msg", "")
            return msg, logs
        raise ValueError(f"Unsupported log type: {type(logs)}, should be either string or Dict")

    def debug(self, logs: Union[str, Dict]) -> None:
        msg, log_dict = self._process_logs(logs)
        self.logger.debug(msg, extra=log_dict)

    def info(self, logs: Union[str, Dict]) -> None:
        msg, log_dict = self._process_logs(logs)
        self.logger.info(msg, extra=log_dict)

    def warning(self, logs: Union[str, Dict]) -> None:
        msg, log_dict = self._process_logs(logs)
        self.logger.warning(msg, extra=log_dict)

    def error(self, logs: Union[str, Dict]) -> None:
        msg, log_dict = self._process_logs(logs)
        self.logger.error(msg, extra=log_dict)

    def critical(self, logs: Union[str, Dict]) -> None:
        msg, log_dict = self._process_logs(logs)
        self.logger.critical(msg, extra=log_dict)


if __name__ == "__main__":
    logger = Logger("./test_log.log")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning({"msg": "This is a warning message", "hello": "world", "foo": "bar"})
    logger.error("This is an error message")
    logger.critical("This is a critical message")
