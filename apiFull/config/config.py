import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-this')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    
    # MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'establecimientos_db')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Excel
    EXCEL_PATH = os.getenv('EXCEL_PATH', 'data.xlsx')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # CORS
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///test.db'
    CACHE_TYPE = 'simple'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}