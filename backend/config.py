import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
    }
    
    # Auth0
    AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
    AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')
    AUTH0_API_AUDIENCE = os.environ.get('AUTH0_API_AUDIENCE')
    AUTH0_CALLBACK_URL = os.environ.get('AUTH0_CALLBACK_URL')
    AUTH0_ISSUER = f'https://{AUTH0_DOMAIN}/' if AUTH0_DOMAIN else None
    AUTH0_ALGORITHMS = os.environ.get('AUTH0_ALGORITHMS', 'RS256').split(',')
    
    # Validate Auth0 settings
    # First check individual required variables
    required_auth0_vars = ['AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET', 'AUTH0_DOMAIN', 'AUTH0_CALLBACK_URL']
    missing_vars = []
    for var in required_auth0_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Auth0 environment variables are not properly set. Missing: {', '.join(missing_vars)}")
    
    # Additional validation for API audience
    if not AUTH0_API_AUDIENCE:
        raise ValueError("AUTH0_API_AUDIENCE environment variable is not set")
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # File Storage
    USE_LOCAL_STORAGE = os.environ.get('USE_LOCAL_STORAGE', 'true').lower() == 'true'
    LOCAL_STORAGE_PATH = os.environ.get('LOCAL_STORAGE_PATH', './uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Azure Blob Storage (for production)
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_CONTAINER = os.environ.get('AZURE_STORAGE_CONTAINER', 'insurance-documents')
    
    # Environment
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'