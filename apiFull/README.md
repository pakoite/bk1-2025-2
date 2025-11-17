# API Flask - Producción Ready

API REST completa para gestión de establecimientos con múltiples fuentes de datos (Excel, SQLite, MySQL).

## 🚀 Características

- ✅ **Seguridad**: JWT Authentication, Rate Limiting, CORS
- ✅ **Validación**: Marshmallow schemas
- ✅ **Múltiples fuentes**: Excel (lectura), SQLite, MySQL
- ✅ **Cache**: Redis para optimización
- ✅ **Documentación**: Swagger/OpenAPI automática
- ✅ **Logging**: Sistema completo de logs
- ✅ **Testing**: Pytest con cobertura
- ✅ **Docker**: Containerización completa
- ✅ **Production Ready**: Gunicorn, health checks, error handling

## 📋 Requisitos

- Python 3.9+
- Redis (para cache y rate limiting)
- MySQL (opcional)
- Docker (opcional)

## 🛠️ Instalación

### Local
```bash
# Clonar repositorio
git clone <repo-url>
cd api_flask

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
sqlite3 database.db < schema_sqlite.sql

# Ejecutar aplicación
python app.py
```

### Docker
```bash
# Copiar variables de entorno
cp .env.example .env
# Editar .env

# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down
```

## 📚 Endpoints

### Autenticación
```bash
# Registrar usuario
POST /api/auth/register
Content-Type: application/json

{
  "username": "usuario",
  "password": "password123",
  "email": "user@example.com"
}

# Login
POST /api/auth/login
Content-Type: application/json

{
  "username": "usuario",
  "password": "password123"
}

# Perfil (requiere autenticación)
GET /api/auth/profile
Authorization: Bearer <token>
```

### Excel (Solo lectura)
```bash
# Listar todos
GET /api/excel/?page=1&per_page=20

# Por ID
GET /api/excel/<id>

# Buscar
GET /api/excel/search?municipio=<nombre>&cod_postal=<codigo>
```

### SQLite (CRUD completo)
```bash
# Listar
GET /api/sqlite/?page=1&per_page=20

# Por ID
GET /api/sqlite/<id>

# Crear (requiere auth)
POST /api/sqlite/
Authorization: Bearer <token>
Content-Type: application/json

{
  "clee": "12345",
  "nom_estab": "Establecimiento",
  "municipio": "Ciudad",
  ...
}

# Actualizar (requiere auth)
PUT /api/sqlite/<id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "nom_estab": "Nuevo Nombre"
}

# Eliminar (requiere auth)
DELETE /api/sqlite/<id>
Authorization: Bearer <token>
```

### MySQL (CRUD completo)

Mismos endpoints que SQLite pero en `/api/mysql/`

## 📖 Documentación

Una vez iniciada la aplicación, accede a:

- **Swagger UI**: http://localhost:5000/docs/
- **Health Check**: http://localhost:5000/health

## 🧪 Testing
```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/

# Generar reporte HTML
pytest --cov=app --cov-report=html tests/
```

## 🔧 Configuración

### Variables de Entorno

Ver `.env.example` para todas las opciones disponibles.

Variables principales:
- `SECRET_KEY`: Clave secreta para Flask
- `JWT_SECRET_KEY`: Clave para firmar JWT
- `DATABASE_URL`: URL de SQLite
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`: Configuración MySQL
- `REDIS_URL`: URL de Redis
- `FLASK_ENV`: development o production

## 🚀 Deployment

### Con Gunicorn
```bash
gunicorn -c gunicorn_config.py "app:create_app()"
```

### Con Docker
```bash
docker-compose up -d
```

## 📊 Monitoreo

- **Health Check**: `/health` - Verifica estado de la API y dependencias
- **Logs**: Directorio `logs/`
  - `api.log`: Log general de la aplicación
  - `gunicorn_access.log`: Logs de acceso
  - `gunicorn_error.log`: Logs de errores

## 🔒 Seguridad

- JWT para autenticación
- Rate limiting por IP
- Validación exhaustiva de inputs
- Prepared statements (prevención SQL injection)
- CORS configurado
- Headers de seguridad

## 📝 Estructura del Proyecto
```
api_flask/
├── app.py                      # Aplicación principal
├── requirements.txt            # Dependencias
├── .env                        # Variables de entorno
├── .gitignore                  # Archivos ignorados
├── Dockerfile                  # Imagen Docker
├── docker-compose.yml          # Orquestación
├── gunicorn_config.py         # Config Gunicorn
├── schema_sqlite.sql           # Schema SQLite
├── schema_mysql.sql            # Schema MySQL
│
├── auth/                       # Autenticación
│   ├── jwt_handler.py
│   ├── decorators.py
│   └── routes.py
│
├── validators/                 # Validación
│   └── schemas.py
│
├── middleware/                 # Middlewares
│   └── error_handlers.py
│
├── database/                   # Base de datos
│   ├── sqlite_pool.py
│   └── mysql_pool.py
│
├── config/                     # Configuración
│   ├── config.py
│   └── logging_config.py
│
├── tests/                      # Tests
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_health.py
│
├── logs/                       # Logs (generado)
├── excel_source.py             # Fuente Excel
├── sqlite_source.py            # Fuente SQLite
└── mysql_source.py             # Fuente MySQL
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abrir un issue en el repositorio.

## 📄 Licencia

MIT License