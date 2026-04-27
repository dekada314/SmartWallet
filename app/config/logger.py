import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import structlog
from context import get_correlation_id

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def add_corelation_id(_, __ , event_dict):
    event_dict["correlation_id"] = get_correlation_id
    return event_dict

def build_rotate_handler(filename, level=logging.INFO):
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=2**28, 
        backupCount=5,
        encoding="utf-8"
    )
    handler.setLevel(level)
    return handler


def setup_loging():
    structlog.configure(
        processors=[
            add_corelation_id,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger
    )
    