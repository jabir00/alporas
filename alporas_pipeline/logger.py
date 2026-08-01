"""Logging helpers."""
from __future__ import annotations

import logging
from pathlib import Path

def setup_logging(level: int = logging.INFO, log_file: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger("alporas_pipeline")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    stream.setLevel(level)
    logger.addHandler(stream)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger
