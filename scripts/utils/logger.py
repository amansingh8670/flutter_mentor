"""
Shared logger for Flutter Mentor.

Usage:
    from scripts.utils.logger import logger

    logger.info("Repository indexing started")
    logger.success("Indexed 542 files")
    logger.warning("Widget not found")
    logger.error("Embedding request failed")
"""

from __future__ import annotations

import logging
import sys


class _Color:
    RESET = "\033[0m"

    GREY = "\033[90m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"


class ColoredFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: _Color.GREY,
        logging.INFO: _Color.BLUE,
        logging.WARNING: _Color.YELLOW,
        logging.ERROR: _Color.RED,
        logging.CRITICAL: _Color.RED,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{_Color.RESET}"


_logger = logging.getLogger("flutter_mentor")

if not _logger.handlers:

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        ColoredFormatter(
            "[%(levelname)s] %(message)s"
        )
    )

    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)


class Logger:

    @staticmethod
    def info(message: str):
        _logger.info(message)

    @staticmethod
    def success(message: str):
        _logger.info(f"✓ {message}")

    @staticmethod
    def warning(message: str):
        _logger.warning(message)

    @staticmethod
    def error(message: str):
        _logger.error(message)

    @staticmethod
    def debug(message: str):
        _logger.debug(message)

    @staticmethod
    def section(title: str):

        line = "=" * 80

        print(f"\n{line}")
        print(title)
        print(line)


logger = Logger()