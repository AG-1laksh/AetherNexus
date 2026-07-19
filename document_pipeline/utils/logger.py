import logging
import sys
from pathlib import Path

from config import BASE_DIR

# Define standard log directory
LOG_DIR = BASE_DIR / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "pipeline.log"

def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with both console and file handlers.
    Ensures consistent formatting across the pipeline.
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger
