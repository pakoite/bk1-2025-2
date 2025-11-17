#!/bin/bash
# Script para probar la API

API_URL="http://localhost:5000"

echo "🧪 Probando API Flask..."
echo ""

# 1. Health Check
echo "1️⃣ Health Check..."
curl -s $API_URL/health | python -m json.tool
echo ""

# 2. Registro
echo "2️⃣ Registrando usuario..."
REGISTER_RESPONSE=$(curl -s -X POST $API_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test12345",
    "email": "test@example.com"
  }')
echo $REGISTER_RESPONSE | python -m json.tool
echo ""

# 3. Login
echo "3️⃣ Haciendo login..."
LOGIN_RESPONSE=$(curl -s -X POST $API_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "test12345"
  }')
echo $LOGIN_RESPONSE | python -m json.tool

# Extraer token
TOKEN=$(echo $LOGIN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")
echo ""
echo "Token obtenido: ${TOKEN:0:50}..."
echo ""

# 4. Perfil
echo "4️⃣ Obteniendo perfil..."
curl -s -X GET $API_URL/api/auth/profile \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo ""

# 5. Crear establecimiento
echo "5️⃣ Creando establecimiento..."
curl -s -X POST $API_URL/api/sqlite/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "clee": "TEST001",
    "nom_estab": "Establecimiento Test",
    "municipio": "Test City",
    "cod_postal": "12345",
    "latitud": 19.4326,
    "longitud": -99.1332
  }' | python -m json.tool
echo ""

# 6. Listar establecimientos
echo "6️⃣ Listando establecimientos..."
curl -s -X GET "$API_URL/api/sqlite/?page=1&per_page=5" | python -m json.tool
echo ""

echo "✅ Pruebas completadas"