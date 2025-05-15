import logging
from logging.handlers import RotatingFileHandler
import os
from app.config import Config

def setup_logger(name, log_file):
    """Setup and return a logger instance"""
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(Config.LOG_DIR, log_file),
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Create loggers
main_logger = setup_logger('main', 'main.log')
download_logger = setup_logger('download_manager', 'downloads.log')
web_logger = setup_logger('web', 'web.log') 