Guía Completa: API Flask en Producción

_Manual_

Autor:

Fecha:

# ÍNDICE

- 1\. Seguridad
- 2\. Manejo de Errores
- 3\. Base de Datos
- 4\. Validación de Datos
- 5\. Documentación
- 6\. Testing
- 7\. Logging y Monitoreo
- 8\. Performance
- 9\. Deployment

# 1\. SEGURIDAD

## Introducción

La seguridad es el aspecto más crítico de una API en producción. Una API sin seguridad adecuada puede ser vulnerable a ataques que comprometan datos sensibles de usuarios y la integridad del sistema.

## 1.1 Autenticación con JWT

### ¿Qué es JWT?

JWT (JSON Web Token) es un estándar para transmitir información de forma segura entre partes como un objeto JSON. Se compone de tres partes:

- Header: Tipo de token y algoritmo de encriptación
- Payload: Datos del usuario (claims)
- Signature: Firma para verificar autenticidad

### ¿Por qué usar JWT?

- Stateless: No necesita almacenar sesiones en el servidor
- Escalable: Funciona bien con microservicios
- Seguro: Firmado digitalmente
- Portable: Funciona en diferentes dominios

### Instalación

pip install PyJWT  
pip install werkzeug

### Implementación - jwt_handler.py

\# auth/jwt_handler.py  
import jwt  
from datetime import datetime, timedelta  
from flask import current_app  
<br/>class JWTHandler:  
@staticmethod  
def generate_token(user_id, username, role='user'):  
"""Genera un token JWT para un usuario"""  
payload = {  
'user_id': user_id,  
'username': username,  
'role': role,  
'exp': datetime.utcnow() + timedelta(hours=24),  
'iat': datetime.utcnow()  
}  
<br/>token = jwt.encode(  
payload,  
current_app.config\['SECRET_KEY'\],  
algorithm='HS256'  
)  
return token  
<br/>@staticmethod  
def decode_token(token):  
"""Decodifica y valida un token JWT"""  
try:  
payload = jwt.decode(  
token,  
current_app.config\['SECRET_KEY'\],  
algorithms=\['HS256'\]  
)  
return payload  
except jwt.ExpiredSignatureError:  
return {'error': 'Token expirado'}  
except jwt.InvalidTokenError:  
return {'error': 'Token inválido'}

### Decoradores de Autenticación

\# auth/decorators.py  
from functools import wraps  
from flask import request, jsonify  
from auth.jwt_handler import JWTHandler  
<br/>def token_required(f):  
"""Decorador para proteger endpoints"""  
@wraps(f)  
def decorated(\*args, \*\*kwargs):  
token = None  
if 'Authorization' in request.headers:  
auth_header = request.headers\['Authorization'\]  
try:  
token = auth_header.split(" ")\[1\]  
except IndexError:  
return jsonify({  
'success': False,  
'message': 'Formato de token inválido'  
}), 401  
<br/>if not token:  
return jsonify({  
'success': False,  
'message': 'Token requerido'  
}), 401  
<br/>payload = JWTHandler.decode_token(token)  
if 'error' in payload:  
return jsonify({  
'success': False,  
'message': payload\['error'\]  
}), 401  
<br/>return f(current_user=payload, \*args, \*\*kwargs)  
return decorated

### Tabla de Usuarios SQL

CREATE TABLE users (  
id INTEGER PRIMARY KEY AUTOINCREMENT,  
username VARCHAR(50) UNIQUE NOT NULL,  
password VARCHAR(255) NOT NULL,  
email VARCHAR(100),  
role VARCHAR(20) DEFAULT 'user',  
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);

### Ejemplos de Uso

\# 1. Registrar usuario  
curl -X POST <http://localhost:5000/api/auth/register> \\  
\-H "Content-Type: application/json" \\  
\-d '{"username": "juan", "password": "miPassword123", "email": "<juan@example.com>"}'  
<br/>\# 2. Login  
curl -X POST <http://localhost:5000/api/auth/login> \\  
\-H "Content-Type: application/json" \\  
\-d '{"username": "juan", "password": "miPassword123"}'  
<br/>\# 3. Acceder a endpoint protegido  
curl -X GET <http://localhost:5000/api/auth/profile> \\  
\-H "Authorization: Bearer &lt;token&gt;"

## 1.2 Rate Limiting

### ¿Qué es Rate Limiting?

Rate Limiting es una técnica para limitar el número de requests que un usuario puede hacer en un período de tiempo.

**Previene:**

- Ataques de fuerza bruta en login
- DDoS (Distributed Denial of Service)
- Abuso de recursos del servidor
- Scraping excesivo de datos

### Instalación

pip install Flask-Limiter  
pip install redis

### Implementación Básica

from flask import Flask  
from flask_limiter import Limiter  
from flask_limiter.util import get_remote_address  
<br/>app = Flask(\__name_\_)  
<br/>limiter = Limiter(  
app=app,  
key_func=get_remote_address,  
default_limits=\["200 per day", "50 per hour"\],  
storage_uri="memory://"  
)  
<br/>@app.route('/api/data')  
@limiter.limit("10 per minute")  
def get_data():  
return {'data': 'información'}  
<br/>@app.route('/api/login', methods=\['POST'\])  
@limiter.limit("5 per minute")  
def login():  
return {'message': 'login'}  
<br/>@app.errorhandler(429)  
def ratelimit_handler(e):  
return jsonify({  
'success': False,  
'message': 'Rate limit excedido',  
'retry_after': e.description  
}), 429

## 1.3 Prevención de SQL Injection

### ¿Qué es SQL Injection?

SQL Injection es un ataque donde el atacante inserta código SQL malicioso en los inputs para manipular la base de datos.

### Código VULNERABLE ❌

\# MAL - Vulnerable a SQL Injection  
@app.route('/user/&lt;username&gt;')  
def get_user_vulnerable(username):  
query = f"SELECT \* FROM users WHERE username = '{username}'"  
cursor.execute(query)  
return cursor.fetchall()  
<br/>\# Si username = "' OR '1'='1" obtendría TODOS los usuarios  
\# Si username = "'; DROP TABLE users; --" eliminaría la tabla

### Código SEGURO ✅

\# BIEN - Seguro con prepared statements  
@app.route('/user/&lt;username&gt;')  
def get_user_secure(username):  
\# SQLite  
query = "SELECT \* FROM users WHERE username = ?"  
cursor.execute(query, (username,))  
<br/>\# MySQL  
query = "SELECT \* FROM users WHERE username = %s"  
cursor.execute(query, (username,))  
<br/>return cursor.fetchall()

## 1.4 Variables de Entorno

### ¿Por qué usar variables de entorno?

- Separar configuración del código
- No exponer credenciales en repositorios
- Facilitar deployment en diferentes ambientes
- Mayor seguridad

### Instalación

pip install python-dotenv

### Archivo .env

SECRET_KEY=tu_clave_secreta_muy_larga  
DATABASE_URL=sqlite:///database.db  
MYSQL_HOST=localhost  
MYSQL_USER=root  
MYSQL_PASSWORD=tu_password  
MYSQL_DB=establecimientos_db  
EXCEL_PATH=data.xlsx  
JWT_SECRET_KEY=otra_clave_secreta  
JWT_EXPIRATION_HOURS=24  
REDIS_URL=redis://localhost:6379  
FLASK_ENV=development  
DEBUG=True

### .gitignore

.env  
\*.db  
\__pycache_\_/  
\*.pyc  
venv/  
logs/

### config.py

import os  
from dotenv import load_dotenv  
<br/>load_dotenv()  
<br/>class Config:  
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)  
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///database.db')  
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')  
MYSQL_USER = os.getenv('MYSQL_USER', 'root')  
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')  
MYSQL_DB = os.getenv('MYSQL_DB', 'establecimientos_db')  
EXCEL_PATH = os.getenv('EXCEL_PATH', 'data.xlsx')  
<br/>class DevelopmentConfig(Config):  
DEBUG = True  
TESTING = False  
<br/>class ProductionConfig(Config):  
DEBUG = False  
TESTING = False  
<br/>config = {  
'development': DevelopmentConfig,  
'production': ProductionConfig,  
'default': DevelopmentConfig  
}

## 1.5 CORS (Cross-Origin Resource Sharing)

### ¿Qué es CORS?

CORS es un mecanismo de seguridad que permite o restringe recursos en un servidor web para ser accedidos desde un dominio diferente.

### Instalación

pip install flask-cors

### Implementación

from flask import Flask  
from flask_cors import CORS  
<br/>app = Flask(\__name_\_)  
<br/>\# Para producción - Solo dominios específicos  
CORS(app, resources={  
r"/api/\*": {  
"origins": \["<https://mifrontend.com>", "<https://www.mifrontend.com"\>],  
"methods": \["GET", "POST", "PUT", "DELETE"\],  
"allow_headers": \["Content-Type", "Authorization"\],  
"supports_credentials": True  
}  
})  
<br/>\# Para desarrollo - Todos los orígenes (NO usar en producción)  
CORS(app)

# 2\. MANEJO DE ERRORES

## Códigos de Estado HTTP

**Códigos de éxito (2xx):**

- 200 OK - Solicitud exitosa
- 201 Created - Recurso creado exitosamente
- 204 No Content - Éxito sin contenido (ej: DELETE exitoso)

**Códigos de error del cliente (4xx):**

- 400 Bad Request - Datos inválidos
- 401 Unauthorized - No autenticado
- 403 Forbidden - No autorizado (sin permisos)
- 404 Not Found - Recurso no encontrado
- 409 Conflict - Conflicto (ej: usuario duplicado)
- 422 Unprocessable Entity - Validación fallida
- 429 Too Many Requests - Rate limit excedido

**Códigos de error del servidor (5xx):**

- 500 Internal Server Error - Error genérico del servidor
- 502 Bad Gateway - Error en servidor upstream
- 503 Service Unavailable - Servicio no disponible

## Formato Estándar de Respuestas

\# utils/responses.py  
<br/>def error_response(message, status_code, errors=None):  
response = {  
'success': False,  
'message': message,  
'status_code': status_code  
}  
if errors:  
response\['errors'\] = errors  
return response, status_code  
<br/>def success_response(data=None, message='Operación exitosa', status_code=200):  
response = {  
'success': True,  
'message': message,  
'status_code': status_code  
}  
if data is not None:  
response\['data'\] = data  
return response, status_code

## Manejadores Globales de Errores

\# middleware/error_handlers.py  
from flask import jsonify  
from werkzeug.exceptions import HTTPException  
from marshmallow import ValidationError  
<br/>def register_error_handlers(app):  
<br/>@app.errorhandler(400)  
def bad_request(error):  
return jsonify({  
'success': False,  
'message': 'Solicitud incorrecta',  
'status_code': 400  
}), 400  
<br/>@app.errorhandler(401)  
def unauthorized(error):  
return jsonify({  
'success': False,  
'message': 'No autenticado',  
'status_code': 401  
}), 401  
<br/>@app.errorhandler(404)  
def not_found(error):  
return jsonify({  
'success': False,  
'message': 'Recurso no encontrado',  
'status_code': 404  
}), 404  
<br/>@app.errorhandler(ValidationError)  
def handle_validation_error(error):  
return jsonify({  
'success': False,  
'message': 'Error de validación',  
'status_code': 422,  
'errors': error.messages  
}), 422  
<br/>@app.errorhandler(Exception)  
def handle_generic_exception(error):  
app.logger.error(f'Excepción: {str(error)}')  
<br/>if app.config.get('DEBUG'):  
message = str(error)  
else:  
message = 'Error interno del servidor'  
<br/>return jsonify({  
'success': False,  
'message': message,  
'status_code': 500  
}), 500

## Excepciones Personalizadas

\# exceptions/custom_exceptions.py  
<br/>class APIException(Exception):  
status_code = 500  
message = 'Error interno del servidor'  
<br/>def \__init_\_(self, message=None, status_code=None):  
super().\__init_\_()  
if message:  
self.message = message  
if status_code:  
self.status_code = status_code  
<br/>def to_dict(self):  
return {  
'success': False,  
'message': self.message,  
'status_code': self.status_code  
}  
<br/>class ResourceNotFoundError(APIException):  
status_code = 404  
message = 'Recurso no encontrado'  
<br/>class InvalidCredentialsError(APIException):  
status_code = 401  
message = 'Credenciales inválidas'  
<br/>class DatabaseError(APIException):  
status_code = 500  
message = 'Error en base de datos'  
<br/>\# Uso  
@app.route('/api/users/&lt;int:id&gt;')  
def get_user(id):  
user = find_user(id)  
if not user:  
raise ResourceNotFoundError(f'Usuario {id} no encontrado')  
return jsonify(user)

# 3\. BASE DE DATOS

## Connection Pooling

### ¿Por qué usar Connection Pooling?

- Reutiliza conexiones existentes
- Reduce overhead de crear/cerrar conexiones
- Mejora performance significativamente
- Maneja mejor la concurrencia

### Implementación para SQLite

\# database/sqlite_pool.py  
import sqlite3  
from contextlib import contextmanager  
import threading  
<br/>class SQLitePool:  
def \__init_\_(self, database, max_connections=5):  
self.database = database  
self.max_connections = max_connections  
self.\_pool = \[\]  
self.\_lock = threading.Lock()  
<br/>def get_connection(self):  
with self.\_lock:  
if self.\_pool:  
return self.\_pool.pop()  
return sqlite3.connect(self.database)  
<br/>def return_connection(self, conn):  
with self.\_lock:  
if len(self.\_pool) < self.max_connections:  
self.\_pool.append(conn)  
else:  
conn.close()  
<br/>@contextmanager  
def connection(self):  
conn = self.get_connection()  
conn.row_factory = sqlite3.Row  
try:  
yield conn  
conn.commit()  
except Exception:  
conn.rollback()  
raise  
finally:  
self.return_connection(conn)  
<br/>\# Uso  
pool = SQLitePool('database.db', max_connections=10)  
<br/>@app.route('/api/users')  
def get_users():  
with pool.connection() as conn:  
cursor = conn.cursor()  
cursor.execute('SELECT \* FROM users')  
users = cursor.fetchall()  
return jsonify(\[dict(u) for u in users\])

### Implementación para MySQL

\# database/mysql_pool.py  
import mysql.connector  
from mysql.connector import pooling  
from contextlib import contextmanager  
<br/>class MySQLPool:  
def \__init_\_(self, pool_name, pool_size, \*\*config):  
self.pool = pooling.MySQLConnectionPool(  
pool_name=pool_name,  
pool_size=pool_size,  
pool_reset_session=True,  
\*\*config  
)  
<br/>@contextmanager  
def connection(self):  
conn = self.pool.get_connection()  
try:  
yield conn  
conn.commit()  
except Exception:  
conn.rollback()  
raise  
finally:  
conn.close()  
<br/>\# Configuración  
mysql_pool = MySQLPool(  
pool_name="mypool",  
pool_size=10,  
host="localhost",  
user="root",  
password="password",  
database="establecimientos_db"  
)  
<br/>\# Uso  
@app.route('/api/establecimientos')  
def get_establecimientos():  
with mysql_pool.connection() as conn:  
cursor = conn.cursor(dictionary=True)  
cursor.execute('SELECT \* FROM establecimientos')  
data = cursor.fetchall()  
cursor.close()  
return jsonify(data)

## Transacciones

### ¿Qué son las Transacciones?

Una transacción es un conjunto de operaciones que se ejecutan como una unidad. Si alguna operación falla, todas se revierten (rollback), garantizando la consistencia de los datos.

### Ejemplo: Transferencia de Dinero

\# database/transactions.py  
from database.mysql_pool import mysql_pool  
<br/>def transfer_money(from_account, to_account, amount):  
"""Transferir dinero entre cuentas usando transacción"""  
with mysql_pool.connection() as conn:  
cursor = conn.cursor()  
<br/>try:  
\# Verificar saldo suficiente  
cursor.execute(  
'SELECT balance FROM accounts WHERE id = %s',  
(from_account,)  
)  
balance = cursor.fetchone()\[0\]  
<br/>if balance < amount:  
raise ValueError('Saldo insuficiente')  
<br/>\# Restar del remitente  
cursor.execute(  
'UPDATE accounts SET balance = balance - %s WHERE id = %s',  
(amount, from_account)  
)  
<br/>\# Sumar al destinatario  
cursor.execute(  
'UPDATE accounts SET balance = balance + %s WHERE id = %s',  
(amount, to_account)  
)  
<br/>\# Registrar transacción  
cursor.execute(  
'''INSERT INTO transactions  
(from_account, to_account, amount, date)  
VALUES (%s, %s, %s, NOW())''',  
(from_account, to_account, amount)  
)  
<br/>conn.commit() # Confirmar todas las operaciones  
return True  
<br/>except Exception as e:  
conn.rollback() # Revertir si hay error  
raise e  
finally:  
cursor.close()

## Migraciones con Alembic

### Instalación

pip install alembic

### Inicialización

\# Inicializar alembic  
alembic init migrations  
<br/>\# Editar alembic.ini  
\# sqlalchemy.url = sqlite:///database.db  
<br/>\# Crear nueva migración  
alembic revision -m "create users table"

### Archivo de Migración

\# migrations/versions/001_create_users_table.py  
from alembic import op  
import sqlalchemy as sa  
<br/>def upgrade():  
op.create_table(  
'users',  
sa.Column('id', sa.Integer(), primary_key=True),  
sa.Column('username', sa.String(50), unique=True, nullable=False),  
sa.Column('email', sa.String(100)),  
sa.Column('password', sa.String(255), nullable=False),  
sa.Column('role', sa.String(20), default='user'),  
sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())  
)  
<br/>def downgrade():  
op.drop_table('users')

### Comandos de Migración

\# Aplicar migraciones  
alembic upgrade head  
<br/>\# Revertir última migración  
alembic downgrade -1  
<br/>\# Ver historial  
alembic history

## Índices para Optimización

Los índices mejoran significativamente la velocidad de las consultas, especialmente en tablas grandes.

\-- Índice simple  
CREATE INDEX idx_username ON users(username);  
<br/>\-- Índice compuesto  
CREATE INDEX idx_user_email ON users(username, email);  
<br/>\-- Índice único  
CREATE UNIQUE INDEX idx_unique_email ON users(email);  
<br/>\-- Para establecimientos  
CREATE INDEX idx_municipio ON establecimientos(municipio);  
CREATE INDEX idx_codigo_postal ON establecimientos(cod_postal);  
CREATE INDEX idx_latlong ON establecimientos(latitud, longitud);  
<br/>\-- Ver índices existentes  
\-- SQLite  
SELECT \* FROM sqlite_master WHERE type = 'index';  
<br/>\-- MySQL  
SHOW INDEX FROM establecimientos;

# 4\. VALIDACIÓN DE DATOS

## Marshmallow Schemas

### Instalación

pip install marshmallow

### ¿Por qué usar Marshmallow?

- Validación automática de datos
- Serialización/deserialización de objetos
- Mensajes de error claros y personalizables
- Validaciones personalizadas complejas
- Integración perfecta con Flask

### Schema de Usuario Completo

\# validators/schemas.py  
from marshmallow import Schema, fields, validate, validates, validates*schema, ValidationError  
<br/>class UserSchema(Schema):  
id = fields.Int(dump_only=True)  
<br/>username = fields.Str(  
required=True,  
validate=\[  
validate.Length(min=3, max=50),  
validate.Regexp(r'^\[a-zA-Z0-9*\]+\$', error='Solo letras, números y guión bajo')  
\]  
)  
<br/>email = fields.Email(required=True)  
<br/>password = fields.Str(  
required=True,  
load_only=True,  
validate=validate.Length(min=8, error='Mínimo 8 caracteres')  
)  
<br/>role = fields.Str(  
validate=validate.OneOf(\['user', 'admin', 'premium'\])  
)  
<br/>created_at = fields.DateTime(dump_only=True)  
<br/>@validates('username')  
def validate_username(self, value):  
"""Validación personalizada de username"""  
forbidden = \['admin', 'root', 'superuser'\]  
if value.lower() in forbidden:  
raise ValidationError('Username no permitido')

### Schema de Establecimiento

class EstablecimientoSchema(Schema):  
id = fields.Int(dump_only=True)  
<br/>clee = fields.Str(  
required=True,  
validate=validate.Length(max=255)  
)  
<br/>nom_estab = fields.Str(  
required=True,  
validate=validate.Length(min=1, max=255)  
)  
<br/>raz_social = fields.Str(  
validate=validate.Length(max=255)  
)  
<br/>correoelec = fields.Email(allow_none=True)  
<br/>telefono = fields.Str(  
validate=validate.Regexp(  
r'^\\d{10}\$',  
error='Teléfono debe tener 10 dígitos'  
)  
)  
<br/>latitud = fields.Float(  
validate=validate.Range(min=-90, max=90)  
)  
<br/>longitud = fields.Float(  
validate=validate.Range(min=-180, max=180)  
)  
<br/>cod_postal = fields.Str(  
validate=validate.Regexp(r'^\\d{5}\$')  
)  
<br/>per_ocu = fields.Int(  
validate=validate.Range(min=0)  
)  
<br/>fecha_alta = fields.DateTime(format='%Y-%m-%d')

### Uso en Endpoints

from validators.schemas import EstablecimientoSchema  
from marshmallow import ValidationError  
<br/>@app.route('/api/establecimientos', methods=\['POST'\])  
def create():  
schema = EstablecimientoSchema()  
<br/>try:  
\# Validar datos entrantes  
validated_data = schema.load(request.json)  
except ValidationError as err:  
return jsonify({  
'success': False,  
'message': 'Error de validación',  
'errors': err.messages  
}), 422  
<br/>\# Insertar en DB con datos validados  
conn = get_db()  
cursor = conn.cursor()  
cursor.execute(  
'INSERT INTO establecimientos (clee, nom_estab, correoelec) VALUES (?, ?, ?)',  
(validated_data\['clee'\], validated_data\['nom_estab'\], validated_data.get('correoelec'))  
)  
conn.commit()  
<br/>return jsonify({  
'success': True,  
'message': 'Creado exitosamente'  
}), 201

### Validaciones Avanzadas

class PasswordChangeSchema(Schema):  
old_password = fields.Str(required=True)  
new_password = fields.Str(required=True, validate=validate.Length(min=8))  
confirm_password = fields.Str(required=True)  
<br/>@validates_schema  
def validate_passwords_match(self, data, \*\*kwargs):  
"""Validar que las contraseñas coincidan"""  
if data\['new_password'\] != data\['confirm_password'\]:  
raise ValidationError(  
'Las contraseñas no coinciden',  
'confirm_password'  
)  
<br/>@validates('new_password')  
def validate_password_strength(self, value):  
"""Validar fortaleza de contraseña"""  
if not any(c.isupper() for c in value):  
raise ValidationError('Debe contener al menos una mayúscula')  
if not any(c.isdigit() for c in value):  
raise ValidationError('Debe contener al menos un número')  
if not any(c in '!@#\$%^&\*' for c in value):  
raise ValidationError('Debe contener al menos un carácter especial')

# 5\. DOCUMENTACIÓN

## Swagger/OpenAPI con Flasgger

### ¿Por qué documentar la API?

- Facilita el uso de la API para otros desarrolladores
- Reduce preguntas y soporte
- Permite probar endpoints directamente
- Genera documentación automáticamente
- Estándar de la industria

### Instalación

pip install flasgger

### Configuración Básica

from flasgger import Swagger  
<br/>app = Flask(\__name_\_)  
<br/>swagger_config = {  
"headers": \[\],  
"specs": \[  
{  
"endpoint": 'apispec',  
"route": '/apispec.json',  
"rule_filter": lambda rule: True,  
"model_filter": lambda tag: True,  
}  
\],  
"static_url_path": "/flasgger_static",  
"swagger_ui": True,  
"specs_route": "/docs/"  
}  
<br/>swagger_template = {  
"info": {  
"title": "API de Establecimientos",  
"description": "API REST para gestión de establecimientos",  
"version": "1.0.0"  
},  
"securityDefinitions": {  
"Bearer": {  
"type": "apiKey",  
"name": "Authorization",  
"in": "header",  
"description": "JWT Authorization header. Ejemplo: 'Bearer {token}'"  
}  
}  
}  
<br/>swagger = Swagger(app, config=swagger_config, template=swagger_template)

### Documentar Endpoints

@app.route('/api/users/&lt;int:id&gt;', methods=\['GET'\])  
def get_user(id):  
"""  
Obtener usuario por ID  
\---  
tags:  
\- Users  
parameters:  
\- name: id  
in: path  
type: integer  
required: true  
description: ID del usuario  
responses:  
200:  
description: Usuario encontrado  
schema:  
properties:  
success:  
type: boolean  
example: true  
data:  
type: object  
properties:  
id:  
type: integer  
example: 1  
username:  
type: string  
example: "juan"  
email:  
type: string  
example: "<juan@example.com>"  
404:  
description: Usuario no encontrado  
schema:  
properties:  
success:  
type: boolean  
example: false  
message:  
type: string  
example: "Usuario no encontrado"  
security:  
\- Bearer: \[\]  
"""  
\# Código del endpoint  
pass

### Endpoint con Body

@app.route('/api/users', methods=\['POST'\])  
def create_user():  
"""  
Crear nuevo usuario  
\---  
tags:  
\- Users  
parameters:  
\- name: body  
in: body  
required: true  
schema:  
type: object  
required:  
\- username  
\- password  
\- email  
properties:  
username:  
type: string  
example: "juan"  
password:  
type: string  
example: "miPassword123"  
email:  
type: string  
example: "<juan@example.com>"  
responses:  
201:  
description: Usuario creado exitosamente  
400:  
description: Datos inválidos  
409:  
description: Usuario ya existe  
"""  
pass

### Acceder a la Documentación

Una vez configurado, accede a: <http://localhost:5000/docs/>

# 6\. TESTING

## Pytest

### ¿Por qué hacer tests?

- Detectar bugs antes de producción
- Documentación viva del código
- Facilita refactorización
- Aumenta confianza en el código
- Reduce costos de mantenimiento

### Instalación

pip install pytest  
pip install pytest-cov

### Estructura de Tests

tests/  
├── \__init_\_.py  
├── conftest.py # Configuración y fixtures  
├── test_auth.py # Tests de autenticación  
├── test_establecimientos.py  
├── test_validation.py  
└── test_integration.py

### conftest.py - Fixtures

\# tests/conftest.py  
import pytest  
from app import create_app  
import sqlite3  
import os  
<br/>@pytest.fixture  
def app():  
"""Crear aplicación de prueba"""  
app = create_app('testing')  
<br/>\# Setup: Crear base de datos de prueba  
conn = sqlite3.connect('test.db')  
cursor = conn.cursor()  
cursor.execute('''  
CREATE TABLE IF NOT EXISTS users (  
id INTEGER PRIMARY KEY,  
username TEXT UNIQUE,  
password TEXT,  
email TEXT,  
role TEXT  
)  
''')  
conn.commit()  
conn.close()  
<br/>yield app  
<br/>\# Teardown: Limpiar  
if os.path.exists('test.db'):  
os.remove('test.db')  
<br/>@pytest.fixture  
def client(app):  
"""Cliente de prueba"""  
return app.test_client()  
<br/>@pytest.fixture  
def auth_headers(client):  
"""Headers con token de autenticación"""  
\# Registrar usuario  
client.post('/api/auth/register', json={  
'username': 'testuser',  
'password': 'testpass123',  
'email': '<test@example.com>'  
})  
<br/>\# Login  
response = client.post('/api/auth/login', json={  
'username': 'testuser',  
'password': 'testpass123'  
})  
<br/>token = response.json\['data'\]\['token'\]  
return {'Authorization': f'Bearer {token}'}

### Tests de Autenticación

\# tests/test_auth.py  
import pytest  
<br/>def test_register_success(client):  
"""Test registro exitoso"""  
response = client.post('/api/auth/register', json={  
'username': 'newuser',  
'password': 'password123',  
'email': '<new@example.com>'  
})  
<br/>assert response.status_code == 201  
assert response.json\['success'\] == True  
assert 'user_id' in response.json\['data'\]  
<br/>def test_register_duplicate_username(client):  
"""Test registro con username duplicado"""  
\# Primer registro  
client.post('/api/auth/register', json={  
'username': 'duplicate',  
'password': 'password123',  
'email': '<dup1@example.com>'  
})  
<br/>\# Segundo registro con mismo username  
response = client.post('/api/auth/register', json={  
'username': 'duplicate',  
'password': 'password456',  
'email': '<dup2@example.com>'  
})  
<br/>assert response.status_code == 409  
assert response.json\['success'\] == False  
<br/>def test_login_success(client):  
"""Test login exitoso"""  
\# Registrar usuario  
client.post('/api/auth/register', json={  
'username': 'loginuser',  
'password': 'password123',  
'email': '<login@example.com>'  
})  
<br/>\# Login  
response = client.post('/api/auth/login', json={  
'username': 'loginuser',  
'password': 'password123'  
})  
<br/>assert response.status_code == 200  
assert 'token' in response.json\['data'\]  
<br/>def test_login_wrong_password(client):  
"""Test login con contraseña incorrecta"""  
client.post('/api/auth/register', json={  
'username': 'wrongpass',  
'password': 'correct123',  
'email': '<wrong@example.com>'  
})  
<br/>response = client.post('/api/auth/login', json={  
'username': 'wrongpass',  
'password': 'incorrect123'  
})  
<br/>assert response.status_code == 401  
assert response.json\['success'\] == False  
<br/>def test_protected_route_without_token(client):  
"""Test acceso a ruta protegida sin token"""  
response = client.get('/api/auth/profile')  
<br/>assert response.status_code == 401  
<br/>def test_protected_route_with_token(client, auth_headers):  
"""Test acceso a ruta protegida con token"""  
response = client.get('/api/auth/profile', headers=auth_headers)  
<br/>assert response.status_code == 200  
assert 'username' in response.json\['data'\]

### Tests de Validación

\# tests/test_validation.py  
from validators.schemas import UserSchema  
from marshmallow import ValidationError  
import pytest  
<br/>def test_user_schema_valid():  
"""Test schema con datos válidos"""  
schema = UserSchema()  
data = {  
'username': 'validuser',  
'email': '<valid@example.com>',  
'password': 'password123'  
}  
<br/>result = schema.load(data)  
assert result\['username'\] == 'validuser'  
<br/>def test_user_schema_invalid_email():  
"""Test schema con email inválido"""  
schema = UserSchema()  
data = {  
'username': 'validuser',  
'email': 'invalid-email',  
'password': 'password123'  
}  
<br/>with pytest.raises(ValidationError) as exc:  
schema.load(data)  
<br/>assert 'email' in exc.value.messages  
<br/>def test_user_schema_short_password():  
"""Test schema con contraseña corta"""  
schema = UserSchema()  
data = {  
'username': 'validuser',  
'email': '<valid@example.com>',  
'password': 'short'  
}  
<br/>with pytest.raises(ValidationError) as exc:  
schema.load(data)  
<br/>assert 'password' in exc.value.messages

### Ejecutar Tests

\# Ejecutar todos los tests  
pytest  
<br/>\# Ejecutar con verbose  
pytest -v  
<br/>\# Ejecutar tests específicos  
pytest tests/test_auth.py  
<br/>\# Ejecutar test específico  
pytest tests/test_auth.py::test_login_success  
<br/>\# Con cobertura  
pytest --cov=app tests/  
<br/>\# Generar reporte HTML de cobertura  
pytest --cov=app --cov-report=html tests/

# 7\. LOGGING Y MONITOREO

## Sistema de Logging

### ¿Por qué hacer logging?

- Debugging en producción
- Auditoría de operaciones
- Detección de errores
- Análisis de patrones de uso
- Cumplimiento normativo

### Niveles de Log

- DEBUG: Información detallada para debugging
- INFO: Confirmación de operaciones normales
- WARNING: Algo inesperado pero no crítico
- ERROR: Error que impide una funcionalidad
- CRITICAL: Error grave que puede detener la aplicación

### Configuración de Logging

\# config/logging_config.py  
import logging  
from logging.handlers import RotatingFileHandler  
import os  
<br/>def setup_logging(app):  
"""Configurar sistema de logging"""  
<br/>if not os.path.exists('logs'):  
os.mkdir('logs')  
<br/>\# Handler para archivo  
file_handler = RotatingFileHandler(  
'logs/api.log',  
maxBytes=10240000, # 10MB  
backupCount=10  
)  
<br/>file_handler.setFormatter(logging.Formatter(  
'%(asctime)s %(levelname)s: %(message)s '  
'\[in %(pathname)s:%(lineno)d\]'  
))  
<br/>file_handler.setLevel(logging.INFO)  
app.logger.addHandler(file_handler)  
<br/>\# Handler para consola  
console_handler = logging.StreamHandler()  
console_handler.setLevel(logging.DEBUG)  
console_handler.setFormatter(logging.Formatter(  
'%(levelname)s - %(message)s'  
))  
app.logger.addHandler(console_handler)  
<br/>app.logger.setLevel(logging.INFO)  
app.logger.info('API iniciada')

### Uso de Logging en Endpoints

from flask import current_app  
<br/>@app.route('/api/users/&lt;int:id&gt;', methods=\['DELETE'\])  
@token_required  
def delete_user(current_user, id):  
"""Eliminar usuario con logging"""  
<br/>\# Log de información  
current_app.logger.info(  
f'Usuario {current_user\["username"\]} intenta eliminar usuario {id}'  
)  
<br/>try:  
\# Lógica de eliminación  
conn = get_db()  
cursor = conn.cursor()  
cursor.execute('DELETE FROM users WHERE id = ?', (id,))  
<br/>if cursor.rowcount == 0:  
current_app.logger.warning(f'Usuario {id} no encontrado')  
return jsonify({'success': False, 'message': 'No encontrado'}), 404  
<br/>conn.commit()  
<br/>\# Log de éxito  
current_app.logger.info(f'Usuario {id} eliminado exitosamente')  
<br/>return jsonify({'success': True}), 200  
<br/>except Exception as e:  
\# Log de error  
current_app.logger.error(  
f'Error al eliminar usuario {id}: {str(e)}',  
exc_info=True  
)  
return jsonify({'success': False, 'message': 'Error interno'}), 500  
finally:  
conn.close()

### Middleware de Logging

\# middleware/request_logging.py  
from flask import request, g  
import time  
from flask import current_app  
<br/>@app.before_request  
def log_request():  
"""Log antes de cada request"""  
g.start_time = time.time()  
current_app.logger.info(  
f'REQUEST: {request.method} {request.path} '  
f'from {request.remote_addr}'  
)  
<br/>@app.after_request  
def log_response(response):  
"""Log después de cada request"""  
if hasattr(g, 'start_time'):  
elapsed = time.time() - g.start_time  
current_app.logger.info(  
f'RESPONSE: {request.method} {request.path} '  
f'Status: {response.status_code} '  
f'Time: {elapsed:.3f}s'  
)  
return response

### Health Check Endpoint

@app.route('/health', methods=\['GET'\])  
def health_check():  
"""  
Endpoint para verificar el estado de la API  
Útil para monitoreo y load balancers  
"""  
import psutil  
<br/>\# Verificar conexión a base de datos  
try:  
conn = get_db()  
cursor = conn.cursor()  
cursor.execute('SELECT 1')  
db_status = 'healthy'  
conn.close()  
except Exception as e:  
db_status = 'unhealthy'  
current_app.logger.error(f'Health check DB failed: {e}')  
<br/>\# Métricas del sistema  
cpu_percent = psutil.cpu_percent()  
memory = psutil.virtual_memory()  
<br/>status = {  
'status': 'healthy' if db_status == 'healthy' else 'degraded',  
'timestamp': datetime.utcnow().isoformat(),  
'database': db_status,  
'system': {  
'cpu_percent': cpu_percent,  
'memory_percent': memory.percent,  
'memory_available_mb': memory.available / (1024 \* 1024)  
}  
}  
<br/>status_code = 200 if status\['status'\] == 'healthy' else 503  
return jsonify(status), status_code

# 8\. PERFORMANCE

## Caché con Redis

### ¿Por qué usar caché?

- Reduce carga en base de datos
- Respuestas más rápidas
- Mejor experiencia de usuario
- Ahorro de recursos
- Manejo de alta concurrencia

### Instalación

pip install redis  
pip install Flask-Caching

### Configuración

from flask_caching import Cache  
<br/>cache_config = {  
'CACHE_TYPE': 'redis',  
'CACHE_REDIS_HOST': 'localhost',  
'CACHE_REDIS_PORT': 6379,  
'CACHE_REDIS_DB': 0,  
'CACHE_DEFAULT_TIMEOUT': 300 # 5 minutos  
}  
<br/>app.config.from_mapping(cache_config)  
cache = Cache(app)

### Uso de Caché

@app.route('/api/establecimientos', methods=\['GET'\])  
@cache.cached(timeout=300, query_string=True)  
def get_establecimientos():  
"""  
Endpoint con caché de 5 minutos  
query_string=True cachea basado en parámetros  
"""  
conn = get_db()  
cursor = conn.cursor()  
cursor.execute('SELECT \* FROM establecimientos')  
data = cursor.fetchall()  
conn.close()  
<br/>return jsonify(\[dict(row) for row in data\])  
<br/>@app.route('/api/establecimientos/&lt;int:id&gt;', methods=\['GET'\])  
@cache.cached(timeout=600)  
def get_establecimiento(id):  
"""Caché de 10 minutos para un establecimiento"""  
conn = get_db()  
cursor = conn.cursor()  
cursor.execute('SELECT \* FROM establecimientos WHERE id = ?', (id,))  
row = cursor.fetchone()  
conn.close()  
<br/>if not row:  
return jsonify({'success': False}), 404  
<br/>return jsonify({'success': True, 'data': dict(row)})  
<br/>@app.route('/api/establecimientos/&lt;int:id&gt;', methods=\['PUT'\])  
@token_required  
def update_establecimiento(current_user, id):  
"""Invalidar caché al actualizar"""  
\# Actualizar en DB  
\# ...  
<br/>\# Invalidar caché  
cache.delete(f'view//api/establecimientos/{id}')  
cache.delete('view//api/establecimientos')  
<br/>return jsonify({'success': True})

## Paginación

### ¿Por qué paginar?

- Reduce tiempo de respuesta
- Menos memoria consumida
- Mejor experiencia móvil
- Evita timeouts
- Escalabilidad

### Implementación

@app.route('/api/establecimientos', methods=\['GET'\])  
def get_establecimientos_paginated():  
"""  
Endpoint con paginación  
Query params: page, per_page  
"""  
\# Obtener parámetros  
page = request.args.get('page', 1, type=int)  
per_page = request.args.get('per_page', 20, type=int)  
<br/>\# Validar  
if page < 1:  
page = 1  
if per_page &lt; 1 or per_page &gt; 100:  
per_page = 20  
<br/>\# Calcular offset  
offset = (page - 1) \* per_page  
<br/>\# Obtener datos  
conn = get_db()  
cursor = conn.cursor()  
<br/>\# Total de registros  
cursor.execute('SELECT COUNT(\*) FROM establecimientos')  
total = cursor.fetchone()\[0\]  
<br/>\# Datos paginados  
cursor.execute(  
'SELECT \* FROM establecimientos LIMIT ? OFFSET ?',  
(per_page, offset)  
)  
items = cursor.fetchall()  
conn.close()  
<br/>\# Calcular total de páginas  
total_pages = (total + per_page - 1) // per_page  
<br/>return jsonify({  
'success': True,  
'data': \[dict(item) for item in items\],  
'pagination': {  
'page': page,  
'per_page': per_page,  
'total': total,  
'total_pages': total_pages,  
'has_next': page < total_pages,  
'has_prev': page > 1  
}  
})

## Compresión de Respuestas

from flask_compress import Compress  
<br/>app = Flask(\__name_\_)  
Compress(app)  
<br/>\# Configuración  
app.config\['COMPRESS_MIMETYPES'\] = \[  
'text/html',  
'text/css',  
'text/xml',  
'application/json',  
'application/javascript'  
\]  
app.config\['COMPRESS_LEVEL'\] = 6 # Nivel de compresión (1-9)  
app.config\['COMPRESS_MIN_SIZE'\] = 500 # Comprimir solo >500 bytes

## Optimización de Queries

### Problema N+1

El problema N+1 ocurre cuando se hace una query para obtener N items, y luego N queries adicionales para obtener datos relacionados.

\# ❌ MAL - Problema N+1  
@app.route('/api/establecimientos-with-municipio')  
def get_with_municipio_bad():  
cursor.execute('SELECT \* FROM establecimientos')  
establecimientos = cursor.fetchall()  
<br/>result = \[\]  
for est in establecimientos: # 1 query  
\# N queries adicionales  
cursor.execute(  
'SELECT nombre FROM municipios WHERE id = ?',  
(est\['municipio_id'\],)  
)  
municipio = cursor.fetchone()  
result.append({  
\*\*dict(est),  
'municipio_nombre': municipio\['nombre'\] if municipio else None  
})  
<br/>return jsonify(result)  
<br/>\# ✅ BIEN - JOIN en una sola query  
@app.route('/api/establecimientos-with-municipio')  
def get_with_municipio_good():  
cursor.execute('''  
SELECT e.\*, m.nombre as municipio_nombre  
FROM establecimientos e  
LEFT JOIN municipios m ON e.municipio_id = m.id  
''')  
establecimientos = cursor.fetchall()  
<br/>return jsonify(\[dict(est) for est in establecimientos\])

# 9\. DEPLOYMENT

## Docker

### ¿Por qué usar Docker?

- Entorno consistente entre desarrollo y producción
- Fácil replicación
- Aislamiento de dependencias
- Escalabilidad
- Portabilidad

### Dockerfile

\# Dockerfile  
FROM python:3.9-slim  
<br/>WORKDIR /app  
<br/>\# Copiar requirements  
COPY requirements.txt .  
<br/>\# Instalar dependencias  
RUN pip install --no-cache-dir -r requirements.txt  
<br/>\# Copiar código  
COPY . .  
<br/>\# Variables de entorno  
ENV FLASK_APP=app.py  
ENV FLASK_ENV=production  
<br/>\# Exponer puerto  
EXPOSE 5000  
<br/>\# Comando de inicio  
CMD \["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"\]

### docker-compose.yml

\# docker-compose.yml  
version: '3.8'  
<br/>services:  
api:  
build: .  
ports:  
\- "5000:5000"  
environment:  
\- FLASK_ENV=production  
\- DATABASE_URL=mysql://root:password@db:3306/establecimientos_db  
\- REDIS_URL=redis://redis:6379/0  
depends_on:  
\- db  
\- redis  
volumes:  
\- ./logs:/app/logs  
restart: always  
<br/>db:  
image: mysql:8.0  
environment:  
\- MYSQL_ROOT_PASSWORD=password  
\- MYSQL_DATABASE=establecimientos_db  
volumes:  
\- mysql_data:/var/lib/mysql  
ports:  
\- "3306:3306"  
restart: always  
<br/>redis:  
image: redis:7-alpine  
ports:  
\- "6379:6379"  
volumes:  
\- redis_data:/data  
restart: always  
<br/>volumes:  
mysql_data:  
redis_data:

### Comandos Docker

\# Construir imagen  
docker build -t api-flask .  
<br/>\# Ejecutar contenedor  
docker run -p 5000:5000 api-flask  
<br/>\# Con docker-compose  
docker-compose up -d  
<br/>\# Ver logs  
docker-compose logs -f api  
<br/>\# Detener  
docker-compose down  
<br/>\# Reconstruir  
docker-compose up -d --build

## Gunicorn (WSGI Server)

### ¿Por qué usar Gunicorn?

El servidor de desarrollo de Flask NO es adecuado para producción. Gunicorn es un servidor WSGI robusto y eficiente.

- Manejo de múltiples workers
- Pre-fork worker model
- Compatible con reverse proxies
- Manejo de señales Unix
- Estable y probado en producción

### Instalación

pip install gunicorn

### Configuración

\# gunicorn_config.py  
import multiprocessing  
<br/>\# Número de workers (2-4 x núcleos de CPU)  
workers = multiprocessing.cpu_count() \* 2 + 1  
<br/>\# Tipo de worker  
worker_class = 'sync'  
<br/>\# Conexiones por worker  
worker_connections = 1000  
<br/>\# Timeout en segundos  
timeout = 30  
<br/>\# Bind  
bind = '0.0.0.0:5000'  
<br/>\# Logs  
accesslog = 'logs/access.log'  
errorlog = 'logs/error.log'  
loglevel = 'info'  
<br/>\# Preload app  
preload_app = True  
<br/>\# Restart workers después de N requests  
max_requests = 1000  
max_requests_jitter = 50

### Ejecutar con Gunicorn

\# Comando básico  
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app  
<br/>\# Con archivo de configuración  
gunicorn -c gunicorn_config.py app:app  
<br/>\# Con reload (desarrollo)  
gunicorn --bind 0.0.0.0:5000 --reload app:app

## Nginx como Reverse Proxy

### ¿Por qué usar Nginx?

- Manejo de SSL/TLS
- Load balancing
- Servir archivos estáticos
- Compresión
- Rate limiting adicional
- Cache HTTP

### Configuración Nginx

\# /etc/nginx/sites-available/api  
server {  
listen 80;  
server_name api.ejemplo.com;  
<br/>\# Redirigir a HTTPS  
return 301 https://\$server_name\$request_uri;  
}  
<br/>server {  
listen 443 ssl http2;  
server_name api.ejemplo.com;  
<br/>\# SSL  
ssl_certificate /etc/ssl/certs/api.ejemplo.com.crt;  
ssl_certificate_key /etc/ssl/private/api.ejemplo.com.key;  
<br/>\# Security headers  
add_header X-Frame-Options "SAMEORIGIN" always;  
add_header X-Content-Type-Options "nosniff" always;  
add_header X-XSS-Protection "1; mode=block" always;  
<br/>\# Logs  
access_log /var/log/nginx/api_access.log;  
error_log /var/log/nginx/api_error.log;  
<br/>\# Max upload size  
client_max_body_size 10M;  
<br/>location / {  
\# Proxy a Gunicorn  
proxy_pass <http://127.0.0.1:5000>;  
proxy_set_header Host \$host;  
proxy_set_header X-Real-IP \$remote_addr;  
proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;  
proxy_set_header X-Forwarded-Proto \$scheme;  
<br/>\# Timeouts  
proxy_connect_timeout 60s;  
proxy_send_timeout 60s;  
proxy_read_timeout 60s;  
}  
<br/>\# Servir archivos estáticos directamente  
location /static/ {  
alias /app/static/;  
expires 30d;  
add_header Cache-Control "public, immutable";  
}  
}

## Variables de Entorno para Producción

\# .env.production  
SECRET_KEY=clave_super_secreta_generada_aleatoriamente  
JWT_SECRET_KEY=otra_clave_super_secreta  
<br/>\# Database  
DATABASE_URL=sqlite:///production.db  
MYSQL_HOST=db.produccion.com  
MYSQL_USER=api_user  
MYSQL_PASSWORD=contraseña_segura  
MYSQL_DB=establecimientos_db  
<br/>\# Redis  
REDIS_URL=redis://redis.produccion.com:6379/0  
<br/>\# Flask  
FLASK_ENV=production  
DEBUG=False  
<br/>\# Logging  
LOG_LEVEL=INFO  
<br/>\# CORS  
ALLOWED_ORIGINS=<https://frontend.com,https://www.frontend.com>  
<br/>\# Rate Limiting  
RATELIMIT_STORAGE_URL=redis://redis.produccion.com:6379/1

## Systemd Service

\# /etc/systemd/system/api-flask.service  
\[Unit\]  
Description=API Flask con Gunicorn  
After=network.target  
<br/>\[Service\]  
User=www-data  
Group=www-data  
WorkingDirectory=/var/www/api  
Environment="PATH=/var/www/api/venv/bin"  
ExecStart=/var/www/api/venv/bin/gunicorn -c gunicorn_config.py app:app  
Restart=always  
RestartSec=10  
<br/>\[Install\]  
WantedBy=multi-user.target

### Comandos Systemd

\# Habilitar servicio  
sudo systemctl enable api-flask  
<br/>\# Iniciar servicio  
sudo systemctl start api-flask  
<br/>\# Ver estado  
sudo systemctl status api-flask  
<br/>\# Reiniciar  
sudo systemctl restart api-flask  
<br/>\# Ver logs  
sudo journalctl -u api-flask -f

## CI/CD con GitHub Actions

\# .github/workflows/deploy.yml  
name: Deploy to Production  
<br/>on:  
push:  
branches: \[ main \]  
<br/>jobs:  
test:  
runs-on: ubuntu-latest  
<br/>steps:  
\- uses: actions/checkout@v2  
<br/>\- name: Set up Python  
uses: actions/setup-python@v2  
with:  
python-version: 3.9  
<br/>\- name: Install dependencies  
run: |  
pip install -r requirements.txt  
pip install pytest pytest-cov  
<br/>\- name: Run tests  
run: pytest --cov=app tests/  
<br/>deploy:  
needs: test  
runs-on: ubuntu-latest  
<br/>steps:  
\- name: Deploy to server  
uses: appleboy/ssh-action@master  
with:  
host: \${{ secrets.SERVER_HOST }}  
username: \${{ secrets.SERVER_USER }}  
key: \${{ secrets.SSH_PRIVATE_KEY }}  
script: |  
cd /var/www/api  
git pull origin main  
source venv/bin/activate  
pip install -r requirements.txt  
sudo systemctl restart api-flask

# EJERCICIOS PRÁCTICOS

## Ejercicio 1: Sistema de Autenticación Completo

Implementa un sistema completo que incluya:

- Registro de usuarios con validación de email
- Login que devuelva JWT
- Endpoint protegido para ver perfil
- Endpoint para actualizar perfil
- Endpoint para cambiar contraseña
- Sistema de roles (user, admin)

## Ejercicio 2: CRUD con Validación

Crea un CRUD completo para establecimientos:

- Schema de validación con Marshmallow
- Todos los endpoints con paginación
- Filtros por municipio y código postal
- Caché en endpoints de lectura
- Tests para todos los endpoints

## Ejercicio 3: Rate Limiting Diferenciado

Implementa rate limiting donde:

- Usuarios anónimos: 10 requests/minuto
- Usuarios autenticados: 100 requests/minuto
- Usuarios premium: 1000 requests/minuto
- Endpoint de login: 5 intentos/minuto

## Ejercicio 4: Sistema de Logging

Implementa logging completo:

- Log de todas las requests con tiempo de respuesta
- Log de errores con stack trace
- Log de acciones críticas (login, registro, delete)
- Rotación de logs
- Diferentes niveles según ambiente

## Ejercicio 5: Deployment

Despliega la API:

- Crear Dockerfile
- Crear docker-compose con MySQL y Redis
- Configurar Gunicorn
- Health check endpoint
- Variables de entorno para producción

# CHECKLIST PARA PRODUCCIÓN

## Seguridad

- ✓ JWT implementado correctamente
- ✓ Rate limiting configurado
- ✓ SQL Injection prevenido (prepared statements)
- ✓ Variables de entorno (.env)
- ✓ CORS configurado correctamente
- ✓ HTTPS habilitado
- ✓ Headers de seguridad
- ✓ Contraseñas hasheadas

## Errores y Validación

- ✓ Manejadores globales de errores
- ✓ Códigos HTTP apropiados
- ✓ Mensajes de error consistentes
- ✓ Schemas de validación (Marshmallow)
- ✓ Excepciones personalizadas

## Base de Datos

- ✓ Connection pooling
- ✓ Transacciones donde sea necesario
- ✓ Índices en columnas frecuentes
- ✓ Migraciones con Alembic
- ✓ Backups automáticos

## Documentación y Testing

- ✓ Swagger/OpenAPI implementado
- ✓ Tests unitarios (pytest)
- ✓ Tests de integración
- ✓ Cobertura mínima 80%
- ✓ README actualizado

## Performance

- ✓ Caché con Redis
- ✓ Paginación en listados
- ✓ Compresión de respuestas
- ✓ Queries optimizadas
- ✓ No problema N+1

## Deployment

- ✓ Docker configurado
- ✓ Gunicorn como WSGI server
- ✓ Nginx como reverse proxy
- ✓ SSL/TLS configurado
- ✓ Logging configurado
- ✓ Health check endpoint
- ✓ Variables de entorno por ambiente
- ✓ CI/CD pipeline

# RECURSOS ADICIONALES

## Documentación Oficial

- Flask: <https://flask.palletsprojects.com/>
- Marshmallow: <https://marshmallow.readthedocs.io/>
- SQLAlchemy: <https://www.sqlalchemy.org/>
- Pytest: <https://docs.pytest.org/>
- Docker: <https://docs.docker.com/>
- Gunicorn: <https://docs.gunicorn.org/>
- Nginx: <https://nginx.org/en/docs/>

## Libros Recomendados

- Flask Web Development (Miguel Grinberg)
- RESTful Web APIs (Leonard Richardson)
- The Twelve-Factor App (Adam Wiggins)
- Building Microservices (Sam Newman)

## Herramientas Útiles

- Postman - Testing de APIs
- Insomnia - Cliente REST
- pgAdmin - Gestión PostgreSQL
- Redis Commander - Gestión Redis
- Swagger Editor - Documentación OpenAPI
- GitHub Actions - CI/CD
- Docker Compose - Orquestación
- Sentry - Monitoreo de errores

# CONCLUSIÓN

Esta guía ha cubierto los aspectos fundamentales para llevar una API Flask desde desarrollo hasta producción. Cada sección representa una pieza crítica del rompecabezas que es construir software de calidad.

## Principios Clave

- Seguridad primero: Nunca comprometer la seguridad por conveniencia
- Validación exhaustiva: No confiar en datos del cliente
- Logging apropiado: Fundamental para debugging en producción
- Testing continuo: Los tests son inversión, no gasto
- Performance importa: Usuarios aprecian respuestas rápidas
- Documentación clara: El código se lee más que se escribe
- Deploy automatizado: Reducir errores humanos
- Monitoreo constante: Detectar problemas antes que usuarios
