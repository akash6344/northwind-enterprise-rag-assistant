from __future__ import annotations

import logging
import json
from typing import Any

logger = logging.getLogger("rag.telemetry")


def configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def log_event(event: str, **fields: Any) -> None:
    configure_logging()
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, default=str))
