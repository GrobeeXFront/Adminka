#!/usr/bin/env python3
"""
Настройка логирования
"""

import logging
import logging.handlers
import sys
from config import LOG_FILE, LOG_LEVEL, LOG_MAX_SIZE, LOG_BACKUP_COUNT

def setup_logging():
    """Настройка расширенной системы логирования"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOG_LEVEL))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)