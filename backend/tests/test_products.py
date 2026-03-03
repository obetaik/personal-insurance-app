def test_get_products_empty(client):
    """Test getting products when database is empty"""
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

def test_get_products_with_data(client, db, sample_product):
    """Test getting products with sample data"""
    response = client.get('/api/products')
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data) == 1
    assert data[0]['name'] == 'Test Auto Insurance'
    assert data[0]['category'] == 'Auto'
    assert data[0]['base_price'] == 500.00

def test_get_products_by_category(client, db, sample_product):
    """Test filtering products by category"""
    # Test existing category
    response = client.get('/api/products?category=Auto')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    
    # Test non-existent category
    response = client.get('/api/products?category=Home')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0

def test_get_single_product(client, db, sample_product):
    """Test getting a single product by ID"""
    product_id = sample_product.id
    
    response = client.get(f'/api/products/{product_id}')
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['id'] == product_id
    assert data['name'] == 'Test Auto Insurance'

def test_get_nonexistent_product(client):
    """Test getting a product that doesn't exist"""
    response = client.get('/api/products/99999')
    assert response.status_code == 404

def test_products_options_method(client):
    """Test OPTIONS method on products endpoint"""
    response = client.options('/api/products')
    assert response.status_code == 200