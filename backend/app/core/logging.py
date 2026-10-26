import logging
import sys
from backend.app.core.config import settings

def setup_logging():
    """Configure centralized secure logging without leaking credentials."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )

logger = logging.getLogger("veritasai")
