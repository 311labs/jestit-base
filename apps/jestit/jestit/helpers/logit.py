import os
import sys
import logging
import threading
from decimal import Decimal
from collections import OrderedDict
from io import StringIO
from typing import Optional
# import traceback
# import time
# from datetime import datetime
# from binascii import hexlify
from . import paths

# Resolve paths
LOG_DIR = paths.LOG_ROOT

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Constants
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 3
COLOR_LOGS = True
LOG_MANAGER = None

def get_logger(name, filename=None, debug=False):
    global LOG_MANAGER
    if LOG_MANAGER is None:
        LOG_MANAGER = LogManager()
    return LOG_MANAGER.get_logger(name, filename, debug)


def pretty_print(msg):
    out = PrettyLogger.pretty_format(msg)
    print(out)


def color_print(msg, color, end="\n"):
    ConsoleLogger.print_message(msg, color, end)


# Utility: Thread-safe lock handler
class ThreadSafeLock:
    def __init__(self):
        self.lock = threading.RLock()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()


# Log Manager to Handle Multiple Loggers
class LogManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance.loggers = {}
            cls._instance.streams = {}
            cls._instance.master_logger = None
            cls._instance.lock = ThreadSafeLock()
        return cls._instance

    def get_logger(self, name, filename=None, debug=False):
        """Retrieve or create a logger."""
        with self.lock:
            if name in self.loggers:
                return self.loggers[name]

            level = logging.DEBUG if debug else logging.INFO
            logger = logging.getLogger(name)
            logger.setLevel(level)

            # Create file handler
            if filename:
                log_path = os.path.join(LOG_DIR, filename)
                file_handler = logging.FileHandler(log_path)
                file_handler.setFormatter(self._get_formatter())
                logger.addHandler(file_handler)

            # Capture to master logger if exists
            if self.master_logger:
                logger.addHandler(logging.StreamHandler(sys.stdout))

            self.loggers[name] = Logger(name, filename, logger)
            return self.loggers[name]

    def set_master_logger(self, logger: logging.Logger):
        """Assign master logger for global logging."""
        with self.lock:
            self.master_logger = logger

    def _get_formatter(self) -> logging.Formatter:
        return logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: %(message)s")


# Logger Wrapper
class Logger:
    def __init__(self, name, filename, logger):
        self.name = name
        self.filename = filename
        self.logger = logger

    def _build_log(self, *args):
        output = []
        for arg in args:
            if isinstance(arg, dict):
                output.append("")
                output.append(PrettyLogger.pretty_format(arg))
            else:
                output.append(str(arg))
        return "\n".join(output)

    def info(self, *args):
        self.logger.info(self._build_log(*args))

    def debug(self, *args):
        self.logger.debug(self._build_log(*args))

    def warning(self, *args):
        self.logger.warning(self._build_log(*args))

    def error(self, *args):
        self.logger.error(self._build_log(*args))

    def critical(self, *args):
        self.logger.critical(self._build_log(*args))

    def exception(self, *args):
        self.logger.exception(self._build_log(*args))


# Log Formatting with Colors
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[34m",  # Blue
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Pink
        "BLUE": "\033[34m",  # Blue
        "GREEN": "\033[32m",  # Green
        "YELLOW": "\033[33m",  # Yellow
        "RED": "\033[31m",  # Red
        "PINK": "\033[35m",  # Pink
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        return f"{log_color}{super().format(record)}{self.RESET}"


# Utility for Pretty Logging
class PrettyLogger:
    @staticmethod
    def pretty_format(data, indent=4, max_length=500000) -> str:
        """Formats complex data structures for logging."""
        output = StringIO()
        PrettyLogger._recursive_format(data, output, indent, max_length)
        return output.getvalue()

    @staticmethod
    def _recursive_format(data, output, indent, max_length, line_count=0):
        """Recursive function to pretty-print dictionaries and lists."""
        if isinstance(data, dict):
            data = OrderedDict(sorted(data.items()))

        if isinstance(data, list):
            output.write("[")
            for item in data:
                PrettyLogger._recursive_format(item, output, indent + 2, max_length, line_count)
            output.write("]")
        elif isinstance(data, dict):
            output.write("{")
            for key, value in data.items():
                output.write(f"\n{' ' * indent}\"{key}\": ")
                PrettyLogger._recursive_format(value, output, indent + 2, max_length, line_count)
            output.write("\n" + " " * (indent - 2) + "}")
        elif isinstance(data, Decimal):
            output.write(str(data))
        elif isinstance(data, str):
            output.write(f"\"{data}\"")
        else:
            output.write(str(data))

    @staticmethod
    def log_json(data, logger=None):
        """Logs data in JSON format."""
        if logger is None:
            logger = Logger("root")
        formatted_data = PrettyLogger.pretty_format(data)
        logger.info(formatted_data)


# Console Logger Utility
class ConsoleLogger:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    PINK = "\033[35m"
    BLUE = "\033[34m"
    WHITE = "\033[37m"

    HBLACK = "\033[90m"
    HRED = "\033[91m"
    HGREEN = "\033[92m"
    HYELLOW = "\033[93m"
    HBLUE = "\033[94m"
    HPINK = "\033[95m"
    HWHITE = "\033[97m"

    HEADER = "\033[95m"
    FAIL = "\033[91m"
    OFF = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    @staticmethod
    def print_message(msg, color_code="\033[32m", end="\n"):
        """Prints a color-coded message to the console."""
        sys.stdout.write(f"{color_code}{msg}\033[0m{end}")
        sys.stdout.flush()


# Rotating File Handler
class RotatingLogger:
    def __init__(self, log_file="app.log", max_bytes=MAX_LOG_SIZE, backup_count=LOG_BACKUP_COUNT):
        self.logger = logging.getLogger("RotatingLogger")
        self.logger.setLevel(logging.INFO)

        handler = logging.handlers.RotatingFileHandler(
            os.path.join(LOG_DIR, log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(handler)

    def log(self, message, level=logging.INFO):
        self.logger.log(level, message)


# Usage Example
if __name__ == "__main__":
    print(BASE_DIR)
    log = Logger("AppLogger", "app.log", debug=True)
    log.info("🚀 Application started successfully!")
    log.debug("🔍 Debugging mode enabled")
    log.warning("⚠️ Warning: Low disk space")
    log.error("❌ An error occurred while processing request")
    log.critical("🔥 Critical system failure!")

    # Pretty print a dictionary
    sample_data = {
        "user": "John Doe",
        "email": "john.doe@example.com",
        "permissions": ["read", "write"],
        "settings": {"theme": "dark", "notifications": True},
    }
    PrettyLogger.log_json(sample_data, log)

    # Console logger
    ConsoleLogger.print_message("✔ Task completed successfully", "\033[32m")
