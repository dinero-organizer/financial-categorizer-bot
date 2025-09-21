import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_logger(name: str) -> logging.Logger:
    """Obtém um logger com o nome fornecido."""
    logger = logging.getLogger(name)
    return logger