from pathlib import Path

from loguru import logger

from ..config import LOG_PATH, LOGGING_LEVEL


logger.add(Path(LOG_PATH, "parser_{time}.log"), format="{time} {file} {function} {level} {message}",
           level=LOGGING_LEVEL,
           retention='10 days')