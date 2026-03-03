def test_create_quote_unauthorized(client, sample_product):
    """Test creating a quote without authentication"""
    quote_data = {
        'product_id': sample_product.id,
        'coverage_amount': 100000
    }
    response = client.post('/api/quotes', json=quote_data)
    assert response.status_code == 401

def test_create_quote_missing_fields(client, auth_headers):
    """Test creating a quote with missing fields"""
    quote_data = {
        'product_id': 1
        # Missing coverage_amount
    }
    response = client.post('/api/quotes', json=quote_data, headers=auth_headers)
    assert response.status_code == 400