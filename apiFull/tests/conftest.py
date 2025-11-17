# tests/conftest.py
import pytest
from app import create_app
import sqlite3
import os

@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app('testing')
    
    # Setup: Crear base de datos de prueba
    if os.path.exists('test.db'):
        os.remove('test.db')
    
    conn = sqlite3.connect('test.db')
    with open('schema_sqlite.sql', 'r') as f:
        conn.executescript(f.read())
    conn.close()
    
    yield app
    
    # Teardown: Limpiar
    if os.path.exists('test.db'):
        os.remove('test.db')

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Headers con token de autenticación"""
    # Registrar usuario
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    token = response.json['data']['token']
    return {'Authorization': f'Bearer {token}'}