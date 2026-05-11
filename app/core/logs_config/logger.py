import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

import structlog

from app.core.logs_config.context import CorrelationContext

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


class LogManager:
    _instance: None | LogManager = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _create_json_formatter(self) -> structlog.stdlib.ProcessorFormatter:
        return structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(
                serializer=lambda data, **kwargs: json.dumps(
                    data, ensure_ascii=False, cls=CustomJSONEncoder, **kwargs
                )
            )
        )

    def _create_consoler_formatter(self) -> structlog.stdlib.ProcessorFormatter:
        return structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True)
        )

    def _add_correlation_id(self, _, __, event_dict):
        event_dict["corelation_id"] = CorrelationContext.get()
        return event_dict

    def _build_rotate_handler(
        self, filename, level=logging.INFO
    ) -> RotatingFileHandler:
        handler = RotatingFileHandler(
            os.path.join(LOG_DIR, filename),
            maxBytes=2**28,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setLevel(level)
        return handler

    def setup(self):
        if self._initialized:
            return

        structlog.configure(
            processors=[
                self._add_correlation_id,
                structlog.stdlib.add_log_level,
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        json_formatter = self._create_json_formatter()
        console_formatter = self._create_consoler_formatter()

        logger_layers = {
            "app": logging.INFO,
            "audit": logging.INFO,
            "main": logging.INFO,
            "db": logging.ERROR,
            "tg_api": logging.ERROR,
        }

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_handler = self._build_rotate_handler("root.log", level=logging.INFO)
        root_handler.setFormatter(json_formatter)
        root_logger.addHandler(root_handler)

        for logger_name, level in logger_layers.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level=level)
            logger.propagate = False

            file_handler = self._build_rotate_handler(f"{logger_name}.log", level=level)
            file_handler.setFormatter(json_formatter)
            logger.addHandler(file_handler)

        consoler_handler = logging.StreamHandler(stream=sys.stdout)
        consoler_handler.setLevel(logging.INFO)
        consoler_handler.setFormatter(console_formatter)

        logging.getLogger("app").addHandler(consoler_handler)

        self._initialized = True

    def get_logger(self, name):
        return structlog.get_logger(name)
