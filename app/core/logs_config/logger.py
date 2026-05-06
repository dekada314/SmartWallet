import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import structlog

from app.core.logs_config.context import CorrelationContext

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


class LogManager:
    _instanсe: None | LogManager = None
    _initialized = False

    def __new__(cls):
        if cls._instanсe is None:
            cls._instanсe = super().__new__(cls)
        return cls._instanсe

    def _add_corelation_id(self, _, __, event_dict):
        event_dict["corelation_id"] = CorrelationContext.get()
        return event_dict

    def _build_rotate_handler(self, filename, level=logging.INFO):
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
                self._add_corelation_id,
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(),
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(self._build_rotate_handler("root.log", level=logging.INFO))

        app_log = logging.getLogger("app")
        app_log.addHandler(self._build_rotate_handler("app.log", level=logging.INFO))
        app_log.propagate = False

        audit_log = logging.getLogger("audit")
        audit_log.addHandler(
            self._build_rotate_handler("audit.log", level=logging.INFO)
        )
        audit_log.propagate = False

        main_log = logging.getLogger("main")
        main_log.addHandler(self._build_rotate_handler("main.log", level=logging.INFO))
        main_log.propagate = False

        db_log = logging.getLogger("db")
        db_log.addHandler(self._build_rotate_handler("db.log", level=logging.INFO))
        db_log.propagate = False

        tg_api = logging.getLogger("tg_api")
        tg_api.addHandler(self._build_rotate_handler("tg_api.log", level=logging.INFO))
        tg_api.propagate = False

        self._initialized = True

    def get_logger(self, name):
        return logging.getLogger(name)
