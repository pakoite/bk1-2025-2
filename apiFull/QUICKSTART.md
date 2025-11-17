# Guía de Inicio Rápido

## 1. Instalación Local
```bash
# Clonar y entrar al directorio
cd api_flask

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Inicializar base de datos
sqlite3 database.db < schema_sqlite.sql

# Ejecutar
python app.py
```

## 2. Docker (Más fácil)
```bash
# Configurar
cp .env.example .env
# Editar .env

# Ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

## 3. Primer Request
```bash
# Registrar usuario
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test1234","email":"test@test.com"}'

# Registrar usuario
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test1234","email":"test@test.com"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test1234"}'

# Guardar el token que recibes
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Acceder a endpoint protegido
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer $TOKEN"
  ```
## 4. Verificar instalación
```bash
# Health check
curl http://localhost:5000/health
```
# Ver documentación
Abrir: http://localhost:5000/docs/

## 5. Crear datos de prueba
# Crear establecimiento (requiere token)
```bash
curl -X POST http://localhost:5000/api/sqlite/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "clee": "12345",
    "nom_estab": "Mi Establecimiento",
    "municipio": "Ciudad de México",
    "cod_postal": "12345",
    "latitud": 19.4326,
    "longitud": -99.1332
  }'
```
## 6. Problemas comunes
# Error: Redis connection refused
```bash
# Instalar y ejecutar Redis
# Ubuntu/Debian
sudo apt-get install redis-server
sudo service redis-server start

# macOS
brew install redis
brew services start redis

# Windows
# Descargar desde: https://redis.io/download
```
# Error: MySQL connection failed
# La API funciona sin MySQL, solo con SQLite
# Para habilitar MySQL, configurar en .env:
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DB=establecimientos_db

# Crear la base de datos:
mysql -u root -p < schema_mysql.sql