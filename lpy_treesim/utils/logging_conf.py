#!/usr/bin/env python3
import os
import logging
import logging.config

PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PKG_DIR, "log")
LOG_FILE = os.path.join(LOG_DIR, "lpy_treesim.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        },
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(name)s " "(%(filename)s:%(lineno)d): %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": os.getenv("LOG_CONSOLE_LEVEL", "INFO"),
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "level": os.getenv("LPY_TREESIM_LOG_LEVEL", "DEBUG"),
            "filename": os.getenv("LPY_TREESIM_LOG_FILE", LOG_FILE),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)
    return


setup_logging()
