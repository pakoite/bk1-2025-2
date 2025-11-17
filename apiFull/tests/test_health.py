# tests/test_health.py
def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    
    assert response.status_code in [200, 503]
    assert 'status' in response.json
    assert 'timestamp' in response.json
    assert 'checks' in response.json

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')
    
    assert response.status_code == 200
    assert 'name' in response.json
    assert 'version' in response.json
    assert 'endpoints' in response.json