# app.py
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flasgger import Swagger
import os
import time

# Importar configuración
from config.config import config
from config.logging_config import setup_logging

# Importar middlewares
from middleware.error_handlers import register_error_handlers

# Importar blueprints
from auth.routes import auth_bp
from excel_source import excel_bp
from sqlite_source import sqlite_bp
from mysql_source import mysql_bp

# Importar pools de base de datos
from database.sqlite_pool import init_pool
from database.mysql_pool import init_mysql_pool

def create_app(config_name=None):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar (development, production, testing)
    
    Returns:
        Flask app configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['ALLOWED_ORIGINS'] if app.config['ALLOWED_ORIGINS'] else "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Rate Limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=app.config['RATELIMIT_STORAGE_URL']
    )
    
    # Cache
    cache = Cache(app, config={
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
        'CACHE_REDIS_URL': app.config.get('CACHE_REDIS_URL'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    })
    
    # Inicializar cache en blueprints
    import excel_source
    import sqlite_source
    import mysql_source
    excel_source.init_cache(cache)
    sqlite_source.init_cache(cache)
    mysql_source.init_cache(cache)
    
    # Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "info": {
            "title": "API de Establecimientos",
            "description": "API REST para gestión de establecimientos con múltiples fuentes de datos",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header. Formato: 'Bearer {token}'"
            }
        }
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Inicializar pools de base de datos
    init_pool('database.db', max_connections=10)
    
    # Inicializar MySQL pool si está configurado
    if app.config.get('MYSQL_HOST'):
        try:
            init_mysql_pool(app.config)
            app.logger.info('MySQL pool inicializado')
        except Exception as e:
            app.logger.warning(f'No se pudo inicializar MySQL pool: {e}')
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(excel_bp, url_prefix='/api/excel')
    app.register_blueprint(sqlite_bp, url_prefix='/api/sqlite')
    app.register_blueprint(mysql_bp, url_prefix='/api/mysql')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint para monitoreo
        ---
        tags:
          - Health
        responses:
          200:
            description: Sistema saludable
          503:
            description: Sistema con problemas
        """
        import psutil
        from database.sqlite_pool import get_pool
        
        status = {
            'status': 'healthy',
            'timestamp': '',
            'checks': {}
        }
        
        from datetime import datetime
        status['timestamp'] = datetime.utcnow().isoformat()
        
        # Check SQLite
        try:
            pool = get_pool()
            with pool.connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                status['checks']['sqlite'] = 'healthy'
        except Exception as e:
            status['checks']['sqlite'] = 'unhealthy'
            status['status'] = 'degraded'
            app.logger.error(f'Health check SQLite failed: {e}')
        
        # Check MySQL si está disponible
        try:
            from database.mysql_pool import get_mysql_pool
            mysql_pool = get_mysql_pool()
            if mysql_pool:
                with mysql_pool.connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT 1')
                    cursor.close()
                    status['checks']['mysql'] = 'healthy'
        except Exception as e:
            status['checks']['mysql'] = 'unavailable'
            app.logger.warning(f'MySQL not available: {e}')
        
        # System metrics
        try:
            status['system'] = {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except:
            pass
        
        status_code = 200 if status['status'] == 'healthy' else 503
        return jsonify(status), status_code
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def index():
        """
        Endpoint raíz con información de la API
        """
        return jsonify({
            'name': 'API de Establecimientos',
            'version': '1.0.0',
            'description': 'API REST con múltiples fuentes de datos',
            'endpoints': {
                'docs': '/docs/',
                'health': '/health',
                'auth': '/api/auth',
                'excel': '/api/excel',
                'sqlite': '/api/sqlite',
                'mysql': '/api/mysql'
            }
        })
    
    # Request logging middleware
    @app.before_request
    def log_request():
        g.start_time = time.time()
        app.logger.info(
            f'REQUEST: {request.method} {request.path} from {request.remote_addr}'
        )
    
    @app.after_request
    def log_response(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            app.logger.info(
                f'RESPONSE: {request.method} {request.path} '
                f'Status: {response.status_code} Time: {elapsed:.3f}s'
            )
        return response
    
    app.logger.info(f'Application initialized with {config_name} config')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)