import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from ..config.settings import LOG_LEVEL, LOG_FILE

def setup_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """
    Configura e retorna um logger personalizado.
    
    Args:
        name: Nome do logger
        log_file: Caminho opcional para arquivo de log
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger principal da aplicação
app_logger = setup_logger('manga_recap', LOG_FILE)

def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger para o módulo especificado.
    
    Args:
        name: Nome do módulo
        
    Returns:
        logging.Logger: Logger configurado
    """
    return logging.getLogger(f'manga_recap.{name}') 