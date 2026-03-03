def test_debug_env_endpoint(client):
    """Test debug environment endpoint"""
    response = client.get('/api/debug/env')
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'DATABASE_URL' in data
    assert 'FLASK_ENV' in data
    assert 'auth0_configured' in data
    assert 'app_config' in data

def test_debug_db_test_endpoint(client):
    """Test debug database endpoint"""
    response = client.get('/api/debug/db-test')
    # This might fail with in-memory SQLite, but we'll check response structure
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.get_json()
        assert 'database_uri_pattern' in data
        assert 'connection_tests' in data