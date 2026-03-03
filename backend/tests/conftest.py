import pytest
import os
import tempfile
from app import app as flask_app
from models import db as _db
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    DEBUG = False

@pytest.fixture(scope='session')
def app():
    """Create application for the tests"""
    flask_app.config.from_object(TestConfig)
    
    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()

@pytest.fixture(scope='session')
def db(app):
    """Create database for the tests"""
    with app.app_context():
        yield _db

@pytest.fixture(scope='function')
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers():
    """Create mock auth headers for testing"""
    # This is a mock token - in real tests, you'd generate a valid test token
    mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHx0ZXN0X3VzZXIiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJuYW1lIjoiVGVzdCBVc2VyIn0.signature"
    return {'Authorization': f'Bearer {mock_token}'}

@pytest.fixture(scope='function')
def sample_product(db):
    """Create a sample product for testing"""
    from models import InsuranceProduct
    
    product = InsuranceProduct(
        name='Test Auto Insurance',
        category='Auto',
        coverage_details='Test coverage details',
        base_price=500.00
    )
    db.session.add(product)
    db.session.commit()
    return product

@pytest.fixture(scope='function')
def sample_user(db):
    """Create a sample user for testing"""
    from models import User
    
    user = User(
        auth0_id='auth0|test_user_123',
        email='test@example.com',
        name='Test User'
    )
    db.session.add(user)
    db.session.commit()
    return user