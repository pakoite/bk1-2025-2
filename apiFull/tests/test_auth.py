# tests/test_auth.py
def test_register_success(client):
    """Test registro exitoso"""
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'password': 'password123',
        'email': 'new@example.com'
    })
    
    assert response.status_code == 201
    assert response.json['success'] == True
    assert 'user_id' in response.json['data']

def test_register_duplicate(client):
    """Test registro con usuario duplicado"""
    client.post('/api/auth/register', json={
        'username': 'duplicate',
        'password': 'password123',
        'email': 'dup@example.com'
    })
    
    response = client.post('/api/auth/register', json={
        'username': 'duplicate',
        'password': 'password456',
        'email': 'dup2@example.com'
    })
    
    assert response.status_code == 409
    assert response.json['success'] == False

def test_login_success(client):
    """Test login exitoso"""
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'password': 'password123',
        'email': 'login@example.com'
    })
    
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'token' in response.json['data']

def test_login_wrong_password(client):
    """Test login con contraseña incorrecta"""
    client.post('/api/auth/register', json={
        'username': 'wrongpass',
        'password': 'correct123',
        'email': 'wrong@example.com'
    })
    
    response = client.post('/api/auth/login', json={
        'username': 'wrongpass',
        'password': 'incorrect123'
    })
    
    assert response.status_code == 401

def test_protected_route_without_token(client):
    """Test acceso a ruta protegida sin token"""
    response = client.get('/api/auth/profile')
    
    assert response.status_code == 401

def test_protected_route_with_token(client, auth_headers):
    """Test acceso a ruta protegida con token"""
    response = client.get('/api/auth/profile', headers=auth_headers)
    
    assert response.status_code == 200
    assert 'username' in response.json['data']