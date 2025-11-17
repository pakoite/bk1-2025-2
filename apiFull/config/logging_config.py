import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    """
    Configurar sistema de logging
    
    Args:
        app: Instancia de Flask
    """
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Handler para archivo
    file_handler = RotatingFileHandler(
        'logs/api.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))
    app.logger.addHandler(console_handler)
    
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.info('API iniciada')