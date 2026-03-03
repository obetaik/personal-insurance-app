def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'environment' in data
    assert data['environment'] == 'production'  # Default from TestConfig

def test_health_options_method(client):
    """Test OPTIONS method on health endpoint"""
    response = client.options('/api/health')
    assert response.status_code == 200

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['name'] == 'Insurance API'
    assert data['version'] == '1.0'
    assert data['status'] == 'running'
    assert 'endpoints' in data
    assert data['endpoints']['health'] == '/api/health'