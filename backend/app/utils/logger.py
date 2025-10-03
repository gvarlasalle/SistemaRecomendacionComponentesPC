from loguru import logger
import sys
from pathlib import Path
from app.config import settings

log_dir = Path(settings.LOG_FILE).parent
log_dir.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(sys.stdout, level=settings.LOG_LEVEL, colorize=True)
logger.add(settings.LOG_FILE, rotation="500 MB", level=settings.LOG_LEVEL)


def get_logger(name: str):
    return logger.bind(name=name)