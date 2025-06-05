"""
Configurador de logging para DocN8NAgent
"""
import sys
from pathlib import Path
from loguru import logger
from src.core.config import LOG_CONFIG, LOGS_DIR


def setup_logging():
    """Configura el sistema de logging"""
    # Remover logger por defecto
    logger.remove()
    
    # Logger para consola
    logger.add(
        sys.stdout,
        level=LOG_CONFIG["level"],
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}",
        colorize=True
    )
    
    # Logger para archivo
    logger.add(
        LOGS_DIR / "docn8n_agent.log",
        level=LOG_CONFIG["level"],
        format=LOG_CONFIG["format"],
        rotation=LOG_CONFIG["rotation"],
        retention=LOG_CONFIG["retention"],
        encoding="utf-8"
    )
    
    # Logger para errores
    logger.add(
        LOGS_DIR / "errors.log",
        level="ERROR",
        format=LOG_CONFIG["format"],
        rotation="1 week",
        retention="2 months",
        encoding="utf-8"
    )
    
    logger.info("Sistema de logging configurado")


# Configurar logging al importar
setup_logging()
