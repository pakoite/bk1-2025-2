# Checklist para API de Producción

## 1. Seguridad

### Autenticación y Autorización

- [ ] JWT o OAuth2 para autenticación
- [ ] Sistema de roles y permisos
- [ ] Rate limiting por usuario/IP
- [ ] Validación de tokens en cada request

### Protección de Datos

- [ ] CORS configurado correctamente
- [ ] Encriptación de datos sensibles
- [ ] Variables de entorno para credenciales (.env)
- [ ] HTTPS obligatorio
- [ ] Sanitización de inputs (prevenir SQL Injection)
- [ ] Validación de datos de entrada con schemas

### Headers de Seguridad

- [ ] Helmet o equivalente para Flask
- [ ] CSP (Content Security Policy)
- [ ] X-Frame-Options
- [ ] X-Content-Type-Options

## 2. Manejo de Errores

- [ ] Manejo global de excepciones
- [ ] Códigos HTTP apropiados
- [ ] Mensajes de error consistentes
- [ ] No exponer información sensible en errores
- [ ] Logging de errores

## 3. Base de Datos

### Conexiones

- [ ] Pool de conexiones
- [ ] Manejo de transacciones
- [ ] Rollback en caso de error
- [ ] Context managers para cerrar conexiones

### Migraciones

- [ ] Sistema de migraciones (Alembic)
- [ ] Versionado de esquema
- [ ] Scripts de rollback

### Optimización

- [ ] Índices en columnas frecuentemente consultadas
- [ ] Queries optimizadas
- [ ] Paginación en listados

## 4. Validación de Datos

- [ ] Validación con Marshmallow o Pydantic
- [ ] Schemas para request/response
- [ ] Validación de tipos de datos
- [ ] Validación de formatos (email, teléfono, etc.)

## 5. Documentación

- [ ] Swagger/OpenAPI
- [ ] Documentación de endpoints
- [ ] Ejemplos de uso
- [ ] Códigos de error documentados

## 6. Testing

- [ ] Tests unitarios
- [ ] Tests de integración
- [ ] Tests de endpoints
- [ ] Cobertura mínima 80%
- [ ] Tests de carga

## 7. Logging y Monitoreo

- [ ] Sistema de logs estructurado
- [ ] Diferentes niveles (DEBUG, INFO, WARNING, ERROR)
- [ ] Rotación de logs
- [ ] Monitoreo de métricas (CPU, memoria, requests)
- [ ] Alertas automáticas
- [ ] APM (Application Performance Monitoring)

## 8. Performance

- [ ] Cache (Redis/Memcached)
- [ ] Compresión de respuestas (gzip)
- [ ] Lazy loading de datos
- [ ] Optimización de queries N+1
- [ ] CDN para archivos estáticos

## 9. Deployment

- [ ] Docker/Containerización
- [ ] CI/CD Pipeline
- [ ] Variables de entorno por ambiente
- [ ] Configuración por ambiente (dev, staging, prod)
- [ ] Health check endpoint
- [ ] Graceful shutdown
- [ ] Load balancer
- [ ] Auto-scaling

## 10. Backup y Recuperación

- [ ] Backups automáticos de BD
- [ ] Plan de recuperación ante desastres
- [ ] Backup de archivos (Excel)
- [ ] Testing de restauración

## 11. Versionado de API

- [ ] Versionado en URL (/api/v1/)
- [ ] Deprecation notices
- [ ] Mantener versiones anteriores

## 12. Limitaciones

- [ ] Rate limiting global
- [ ] Throttling por endpoint
- [ ] Tamaño máximo de payload
- [ ] Timeout de requests

## 13. Dependencias

- [ ] Actualización regular de dependencias
- [ ] Auditoría de seguridad (pip-audit)
- [ ] Lock file (requirements.lock)
- [ ] Dependencias mínimas necesarias

## 14. Configuración

- [ ] Separar configuración de código
- [ ] Config por ambiente
- [ ] Secrets management (Vault, AWS Secrets)
- [ ] Feature flags

## 15. Código

- [ ] Type hints
- [ ] Linting (pylint, flake8)
- [ ] Formateo (black)
- [ ] Code review process
- [ ] Documentación inline
- [ ] Principios SOLID

## 16. Compliance

- [ ] GDPR si aplica
- [ ] Términos y condiciones
- [ ] Política de privacidad
- [ ] Auditoría de accesos

## 17. API Específico

### Excel Source

- [ ] Validar existencia de archivo
- [ ] Manejo de archivos grandes
- [ ] Cache de lectura
- [ ] Validación de estructura del Excel

### Database Sources

- [ ] Prepared statements
- [ ] Connection pooling
- [ ] Timeout de queries
- [ ] Read replicas para lectura

## Ejemplo de Implementación Básica

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    EXCEL_PATH = os.getenv('EXCEL_PATH', 'data.xlsx')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
```

```python
# middleware/error_handler.py
from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            'error': e.name,
            'message': e.description,
            'status': e.code
        }), e.code

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
```

```python
# middleware/auth.py
from functools import wraps
from flask import request, jsonify
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token invalid'}), 401
        return f(*args, **kwargs)
    return decorated
```

```python
# validators/schemas.py
from marshmallow import Schema, fields, validate

class EstablecimientoSchema(Schema):
    id = fields.Int(dump_only=True)
    clee = fields.Str(required=True, validate=validate.Length(max=255))
    nom_estab = fields.Str(required=True, validate=validate.Length(max=255))
    correoelec = fields.Email()
    latitud = fields.Float()
    longitud = fields.Float()
```

```python
# app.py mejorado
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')

CORS(app, resources={r"/api/*": {"origins": ["https://yourdomain.com"]}})

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

if not app.debug:
    file_handler = RotatingFileHandler('logs/api.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

app.register_blueprint(excel_bp, url_prefix='/api/v1/excel')
app.register_blueprint(sqlite_bp, url_prefix='/api/v1/sqlite')
app.register_blueprint(mysql_bp, url_prefix='/api/v1/mysql')

if __name__ == '__main__':
    app.run()
```
