#!/usr/bin/env python
"""
Insurance API - Main Application
Production-Ready Version - With Proper CORS Handling and Debugging
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# Configure logging based on environment
log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup immediately
logger.info("="*60)
logger.info("APPLICATION STARTING - Initializing components")
logger.info("="*60)

try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    logger.info("✓ Flask imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import Flask: {e}")
    sys.exit(1)

try:
    from werkzeug.utils import secure_filename
    from dateutil import parser
    logger.info("✓ Werkzeug and dateutil imported")
except ImportError as e:
    logger.error(f"✗ Failed to import werkzeug/dateutil: {e}")
    sys.exit(1)

try:
    from config import Config
    logger.info("✓ Config imported")
except ImportError as e:
    logger.error(f"✗ Failed to import Config: {e}")
    sys.exit(1)

try:
    from models import db, User, InsuranceProduct, Quote, Policy, Payment, Claim
    logger.info("✓ Models imported")
except ImportError as e:
    logger.error(f"✗ Failed to import models: {e}")
    sys.exit(1)

try:
    from auth import requires_auth, AuthError
    logger.info("✓ Auth imported")
except ImportError as e:
    logger.error(f"✗ Failed to import auth: {e}")
    sys.exit(1)

# Create Flask app
app = Flask(__name__)
logger.info("✓ Flask app created")

# Load configuration
try:
    app.config.from_object(Config)
    logger.info("✓ Configuration loaded from Config object")
    
    # Log configuration status (without sensitive values)
    logger.info(f"  - ENV: {app.config.get('ENV', 'production')}")
    logger.info(f"  - DEBUG: {app.config.get('DEBUG', False)}")
    logger.info(f"  - USE_LOCAL_STORAGE: {app.config.get('USE_LOCAL_STORAGE', True)}")
    
    # Check critical config values
    critical_configs = {
        'SECRET_KEY': bool(app.config.get('SECRET_KEY')),
        'SQLALCHEMY_DATABASE_URI': bool(app.config.get('SQLALCHEMY_DATABASE_URI')),
        'CORS_ORIGINS': bool(app.config.get('CORS_ORIGINS'))
    }
    for key, present in critical_configs.items():
        if present:
            logger.info(f"  ✓ {key} is set")
        else:
            logger.warning(f"  ⚠ {key} is NOT set")
            
except Exception as e:
    logger.error(f"✗ Failed to load configuration: {e}")
    sys.exit(1)

# ============================================
# CORS CONFIGURATION - Using Flask-CORS Only
# ============================================
cors_origins = app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
logger.info(f"CORS configured for origins: {cors_origins}")

# Initialize CORS with comprehensive configuration
try:
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": cors_origins,
                 "methods": ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": [
                     "Content-Type", 
                     "Authorization", 
                     "Accept", 
                     "X-Requested-With",
                     "Origin"
                 ],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 86400,
                 "send_wildcard": False
             }
         })
    
    # Also add CORS for root endpoint
    CORS(app, 
         resources={
             r"/": {
                 "origins": cors_origins,
                 "methods": ["GET", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         })
    logger.info("✓ CORS initialized with Flask-CORS")
except Exception as e:
    logger.error(f"✗ Failed to initialize CORS: {e}")
    # Continue anyway as CORS might not be critical for startup

# Initialize database
db.init_app(app)
logger.info("✓ Database initialized with app")

# Initialize database tables ONCE before any workers are forked
with app.app_context():
    logger.info("Creating database tables (pre-fork)...")
    try:
        # This will create tables if they don't exist
        db.create_all()
        logger.info("✓ Database tables created/verified")
        
      
            
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        # Log more details about the error
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
        if db_uri != 'Not configured' and '@' in db_uri:
            masked_uri = db_uri.split('@')[0].split('://')[0] + '://***:***@' + db_uri.split('@')[1]
            logger.error(f"  Database URI pattern: {masked_uri}")

# Create upload directory
if app.config.get('USE_LOCAL_STORAGE', True):
    try:
        upload_path = app.config.get('LOCAL_STORAGE_PATH', './uploads')
        os.makedirs(upload_path, exist_ok=True)
        os.makedirs(os.path.join(upload_path, 'documents'), exist_ok=True)
        os.makedirs(os.path.join(upload_path, 'temp'), exist_ok=True)
        logger.info(f"✓ Upload directories created at {upload_path}")
        
        # Verify directories are writable
        for dir_name in [upload_path, os.path.join(upload_path, 'documents'), os.path.join(upload_path, 'temp')]:
            if os.access(dir_name, os.W_OK):
                logger.info(f"  ✓ {dir_name} is writable")
            else:
                logger.warning(f"  ⚠ {dir_name} is NOT writable")
    except Exception as e:
        logger.error(f"✗ Failed to create upload directories: {e}")

# Log environment variables (masked) for debugging
logger.info("Environment variables (masked):")
env_vars_to_check = ['DATABASE_URL', 'AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET', 
                     'AUTH0_DOMAIN', 'AUTH0_CALLBACK_URL', 'AUTH0_API_AUDIENCE',
                     'FLASK_ENV', 'PORT', 'CORS_ORIGINS']

for var in env_vars_to_check:
    value = os.environ.get(var, 'NOT SET')
    if var == 'DATABASE_URL' and value != 'NOT SET' and '@' in value:
        masked = value.split('@')[0].split('://')[0] + '://***:***@' + value.split('@')[1]
        logger.info(f"  {var}: {masked}")
    elif var.startswith('AUTH0') and value != 'NOT SET':
        logger.info(f"  {var}: {'*' * 8} (set)")
    elif value != 'NOT SET':
        logger.info(f"  {var}: {value}")
    else:
        logger.warning(f"  ⚠ {var}: {value}")

# Check Auth0 configuration
auth0_vars = {
    'AUTH0_CLIENT_ID': app.config.get('AUTH0_CLIENT_ID'),
    'AUTH0_CLIENT_SECRET': app.config.get('AUTH0_CLIENT_SECRET'),
    'AUTH0_DOMAIN': app.config.get('AUTH0_DOMAIN'),
    'AUTH0_CALLBACK_URL': app.config.get('AUTH0_CALLBACK_URL'),
    'AUTH0_API_AUDIENCE': app.config.get('AUTH0_API_AUDIENCE')
}
missing_auth0 = [k for k, v in auth0_vars.items() if not v]
if missing_auth0:
    logger.warning(f"⚠ Auth0 missing variables: {missing_auth0}")
else:
    logger.info("✓ All Auth0 variables are configured")

# Error handlers
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    logger.warning(f"Auth error: {ex.error}")
    return jsonify(ex.error), ex.status_code

@app.errorhandler(404)
def not_found(error):
    logger.debug(f"404 error: {error}")
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    logger.debug(f"405 error: {error}")
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    try:
        db.session.rollback()
    except:
        pass
    return jsonify({'error': 'Internal server error'}), 500

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'name': 'Insurance API',
        'version': '1.0',
        'status': 'running',
        'environment': app.config.get('ENV', 'production'),
        'endpoints': {
            'health': '/api/health',
            'products': '/api/products',
            'docs': 'See documentation for full API reference'
        }
    })

# Enhanced Health check endpoint with detailed debugging
@app.route('/api/health', methods=['GET', 'HEAD', 'OPTIONS'])
def health():
    """Health check endpoint with detailed debugging"""
    if request.method == 'OPTIONS':
        return '', 200
    
    logger.debug("Health check endpoint called")
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'environment': app.config.get('ENV', 'production'),
        'checks': {}
    }
    
    all_checks_passed = True
    
    # Check 1: Basic app status
    health_status['checks']['app'] = {
        'status': 'running',
        'uptime': 'unknown'
    }
    
    # Check 2: Database connection
    try:
        with app.app_context():
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).scalar()
            if result == 1:
                health_status['checks']['database'] = {
                    'status': 'connected',
                    'message': 'Database connection successful'
                }
                logger.debug("✅ Health check: Database connected")
            else:
                health_status['checks']['database'] = {
                    'status': 'degraded',
                    'message': f'Unexpected query result: {result}'
                }
                logger.warning(f"⚠ Health check: Unexpected database result: {result}")
    except Exception as e:
        all_checks_passed = False
        health_status['checks']['database'] = {
            'status': 'disconnected',
            'message': str(e),
            'error_type': type(e).__name__
        }
        logger.error(f"❌ Health check: Database connection failed - {e}")
        
        # Try to get more detailed database error
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
        if db_uri != 'Not configured':
            try:
                from urllib.parse import urlparse
                parsed = urlparse(db_uri)
                health_status['checks']['database']['details'] = {
                    'scheme': parsed.scheme,
                    'host': parsed.hostname,
                    'port': parsed.port,
                    'database': parsed.path[1:] if parsed.path else None
                }
            except:
                pass
    
    # Check 3: Database configuration
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
    if db_uri != 'Not set' and '@' in db_uri:
        masked_uri = db_uri.split('@')[0].split('://')[0] + '://***:***@' + db_uri.split('@')[1]
        health_status['checks']['database_config'] = {
            'status': 'configured',
            'uri_pattern': masked_uri
        }
    else:
        health_status['checks']['database_config'] = {
            'status': 'misconfigured',
            'uri': db_uri
        }
    
    # Check 4: Auth0 configuration
    auth0_status = {}
    auth0_vars_check = {
        'AUTH0_CLIENT_ID': bool(app.config.get('AUTH0_CLIENT_ID')),
        'AUTH0_CLIENT_SECRET': bool(app.config.get('AUTH0_CLIENT_SECRET')),
        'AUTH0_DOMAIN': bool(app.config.get('AUTH0_DOMAIN')),
        'AUTH0_CALLBACK_URL': bool(app.config.get('AUTH0_CALLBACK_URL')),
        'AUTH0_API_AUDIENCE': bool(app.config.get('AUTH0_API_AUDIENCE'))
    }
    
    missing = [k for k, v in auth0_vars_check.items() if not v]
    if missing:
        all_checks_passed = False
        auth0_status = {
            'status': 'incomplete',
            'missing_vars': missing,
            'present_vars': [k for k, v in auth0_vars_check.items() if v]
        }
        logger.warning(f"⚠ Health check: Missing Auth0 variables - {missing}")
    else:
        auth0_status = {
            'status': 'configured',
            'present_vars': list(auth0_vars_check.keys())
        }
        logger.debug("✅ Health check: Auth0 configured")
    
    health_status['checks']['auth0'] = auth0_status
    
    # Check 5: Storage directories
    if app.config.get('USE_LOCAL_STORAGE', True):
        upload_path = app.config.get('LOCAL_STORAGE_PATH', './uploads')
        docs_path = os.path.join(upload_path, 'documents')
        temp_path = os.path.join(upload_path, 'temp')
        
        dirs_status = {}
        for path_name, path in [('base', upload_path), ('documents', docs_path), ('temp', temp_path)]:
            try:
                exists = os.path.exists(path)
                writable = os.access(path, os.W_OK) if exists else False
                dirs_status[path_name] = {
                    'exists': exists,
                    'writable': writable
                }
                if not exists:
                    logger.warning(f"⚠ Storage path does not exist: {path}")
                elif not writable:
                    logger.warning(f"⚠ Storage path not writable: {path}")
            except Exception as e:
                dirs_status[path_name] = {
                    'exists': False,
                    'error': str(e)
                }
        
        health_status['checks']['storage'] = {
            'status': 'ok' if all(d.get('exists', False) and d.get('writable', False) for d in dirs_status.values()) else 'issues',
            'directories': dirs_status
        }
    
    # Check 6: Environment
    env_vars = {
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'not set'),
        'FLASK_DEBUG': os.environ.get('FLASK_DEBUG', 'not set'),
        'PORT': os.environ.get('PORT', 'not set')
    }
    health_status['checks']['environment'] = env_vars
    
    # Check 7: System info
    health_status['checks']['system'] = {
        'python_version': sys.version.split()[0],
        'platform': sys.platform
    }
    
    # Set overall status
    if not all_checks_passed:
        health_status['status'] = 'degraded'
        logger.warning("⚠ Health check: Overall status degraded")
    else:
        logger.debug("✅ Health check: All checks passed")
    
    # Add response headers for debugging
    response = jsonify(health_status)
    response.headers.add('X-Health-Check', 'true')
    response.headers.add('X-Database-Status', health_status['checks'].get('database', {}).get('status', 'unknown'))
    
    return response

# Debug endpoint to check environment (REMOVE IN PRODUCTION)
@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    """Debug endpoint to check environment variables (REMOVE IN PRODUCTION)"""
    if app.config.get('ENV') == 'production':
        return jsonify({'error': 'Not available in production'}), 403
    
    safe_vars = {}
    for key in ['DATABASE_URL', 'FLASK_ENV', 'FLASK_DEBUG', 'PORT', 'CORS_ORIGINS']:
        value = os.environ.get(key, 'NOT SET')
        # Mask database password
        if key == 'DATABASE_URL' and value != 'NOT SET' and '@' in value:
            parts = value.split('@')
            masked = parts[0].split('://')[0] + '://***:***@' + parts[1]
            safe_vars[key] = masked
        else:
            safe_vars[key] = value
    
    # Check which Auth0 vars are set (just show keys, not values)
    auth0_vars = ['AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET', 'AUTH0_DOMAIN', 
                  'AUTH0_CALLBACK_URL', 'AUTH0_API_AUDIENCE']
    safe_vars['auth0_configured'] = [v for v in auth0_vars if os.environ.get(v)]
    safe_vars['auth0_missing'] = [v for v in auth0_vars if not os.environ.get(v)]
    
    # Add app config
    safe_vars['app_config'] = {
        'ENV': app.config.get('ENV'),
        'DEBUG': app.config.get('DEBUG'),
        'USE_LOCAL_STORAGE': app.config.get('USE_LOCAL_STORAGE'),
        'CORS_ORIGINS': app.config.get('CORS_ORIGINS')
    }
    
    return jsonify(safe_vars)

# Test database connection endpoint
@app.route('/api/debug/db-test', methods=['GET'])
def debug_db_test():
    """Test database connection with detailed output"""
    if app.config.get('ENV') == 'production':
        return jsonify({'error': 'Not available in production'}), 403
    
    from sqlalchemy import text
    
    result = {
        'connection_tests': [],
        'database_info': {}
    }
    
    # Test 1: Get database URI (masked)
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
    if db_uri != 'Not configured' and '@' in db_uri:
        masked_uri = db_uri.split('@')[0].split('://')[0] + '://***:***@' + db_uri.split('@')[1]
        result['database_uri_pattern'] = masked_uri
    else:
        result['database_uri_pattern'] = db_uri
    
    # Test 2: Try to connect
    try:
        with app.app_context():
            # Test connection
            start = datetime.now()
            simple_result = db.session.execute(text('SELECT 1')).scalar()
            result['connection_tests'].append({
                'test': 'simple_query',
                'query': 'SELECT 1',
                'result': simple_result
            })
            
            # Get database version
            version_result = db.session.execute(text('SELECT VERSION()')).scalar()
            result['connection_tests'].append({
                'test': 'get_version',
                'query': 'SELECT VERSION()',
                'result': version_result
            })
            
            # Get tables
            tables_result = db.session.execute(text('SHOW TABLES')).fetchall()
            result['database_info']['tables'] = [t[0] for t in tables_result]
            
            response_time = (datetime.now() - start).total_seconds()
            result['connection_tests'].append({
                'test': 'response_time',
                'seconds': response_time
            })
            
            result['status'] = 'connected'
            logger.info("✅ Debug DB test successful")
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)
        result['error_type'] = type(e).__name__
        logger.error(f"❌ Debug DB test failed: {e}")
    
    return jsonify(result)

# Initialize database command
@app.cli.command('init-db')
def init_db():
    """Initialize the database with sample data"""
    logger.info("Initializing database...")
    
    with app.app_context():
        try:
            db.create_all()
            logger.info("✓ Database tables created")
            
  
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            print(f"\n✗ Database initialization failed: {e}")

# ==================== User Management ====================
@app.route('/api/users/profile', methods=['OPTIONS'])
def handle_profile_options():
    """Handle OPTIONS requests for profile endpoint"""
    return '', 200

@app.route('/api/users/profile', methods=['GET'])
@requires_auth
def get_user_profile():
    """Get current user profile"""
    logger.info("GET USER PROFILE ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        # Create new user from Auth0 data
        user = User(
            auth0_id=auth0_id,
            email=request.user.get('email', ''),
            name=request.user.get('name', '')
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"Created new user with ID: {user.id}")
    
    return jsonify({
        'id': user.id,
        'auth0_id': user.auth0_id,
        'name': user.name,
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })

@app.route('/api/users/profile', methods=['PUT'])
@requires_auth
def update_user_profile():
    """Update user profile - supports all profile fields"""
    logger.info("UPDATE USER PROFILE ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    # Update only fields that are provided and exist in the model
    updatable_fields = ['name', 'phone', 'address', 'city', 'state', 'zip_code']
    
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    # Handle date_of_birth separately
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            user.date_of_birth = parser.parse(data['date_of_birth']).date()
        except:
            return jsonify({'error': 'Invalid date format for date_of_birth'}), 400
    
    db.session.commit()
    
    # Return updated profile
    return jsonify({
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'auth0_id': user.auth0_id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone if hasattr(user, 'phone') else None,
            'address': user.address if hasattr(user, 'address') else None,
            'city': user.city if hasattr(user, 'city') else None,
            'state': user.state if hasattr(user, 'state') else None,
            'zip_code': user.zip_code if hasattr(user, 'zip_code') else None,
            'date_of_birth': user.date_of_birth.isoformat() if hasattr(user, 'date_of_birth') and user.date_of_birth else None
        }
    })




# ==================== Products ====================
@app.route('/api/products', methods=['GET', 'OPTIONS'])
def get_products():
    """Get all insurance products"""
    if request.method == 'OPTIONS':
        return '', 200
    
    category = request.args.get('category')
    query = InsuranceProduct.query
    if category:
        query = query.filter_by(category=category)
    
    products = query.all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'coverage_details': p.coverage_details,
        'base_price': p.base_price
    } for p in products])

@app.route('/api/products/<int:product_id>', methods=['GET', 'OPTIONS'])
def get_product(product_id):
    """Get specific product details"""
    if request.method == 'OPTIONS':
        return '', 200
    
    product = InsuranceProduct.query.get_or_404(product_id)
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'coverage_details': product.coverage_details,
        'base_price': product.base_price
    })

# ==================== Quotes ====================
@app.route('/api/quotes', methods=['OPTIONS'])
def handle_quotes_options():
    """Handle OPTIONS requests for quotes endpoint"""
    return '', 200

@app.route('/api/quotes', methods=['GET'])
@requires_auth
def get_user_quotes():
    """Get all quotes for current user"""
    logger.info("GET USER QUOTES ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    quotes = Quote.query.filter_by(user_id=user.id).order_by(Quote.created_at.desc()).all()
    
    return jsonify([{
        'id': q.id,
        'quote_number': q.quote_number,
        'product_name': q.product.name,
        'coverage_amount': q.coverage_amount,
        'calculated_price': q.calculated_price,
        'status': q.status,
        'created_at': q.created_at.isoformat(),
        'expires_at': q.expires_at.isoformat() if q.expires_at else None
    } for q in quotes])

@app.route('/api/quotes', methods=['POST'])
@requires_auth
def create_quote():
    """Create a new quote"""
    logger.info("CREATE QUOTE ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    # Validate required fields
    required_fields = ['product_id', 'coverage_amount']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    product = InsuranceProduct.query.get(data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Calculate premium
    base_price = product.base_price
    coverage_amount = float(data['coverage_amount'])
    deductible = float(data.get('deductible', 0))
    calculated_price = base_price * (coverage_amount / 100000) * (1 - (deductible / 10000))
    
    # Create quote
    quote = Quote(
        user_id=user.id,
        product_id=product.id,
        coverage_amount=coverage_amount,
        deductible=deductible,
        additional_options=data.get('additional_options'),
        calculated_price=calculated_price,
        status='Pending',
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.session.add(quote)
    db.session.commit()
    
    return jsonify({
        'id': quote.id,
        'quote_number': quote.quote_number,
        'calculated_price': quote.calculated_price,
        'status': quote.status,
        'expires_at': quote.expires_at.isoformat() if quote.expires_at else None,
        'product': {'id': product.id, 'name': product.name}
    }), 201

@app.route('/api/quotes/<int:quote_id>', methods=['OPTIONS'])
def handle_quote_options(quote_id):
    """Handle OPTIONS requests for specific quote endpoint"""
    return '', 200

@app.route('/api/quotes/<int:quote_id>', methods=['GET'])
@requires_auth
def get_quote(quote_id):
    """Get specific quote details"""
    logger.info(f"GET QUOTE ENDPOINT HIT for quote_id: {quote_id}")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    quote = Quote.query.filter_by(id=quote_id, user_id=user.id).first_or_404()
    
    return jsonify({
        'id': quote.id,
        'quote_number': quote.quote_number,
        'product': {
            'id': quote.product.id,
            'name': quote.product.name,
            'category': quote.product.category
        },
        'coverage_amount': quote.coverage_amount,
        'deductible': quote.deductible,
        'additional_options': quote.additional_options,
        'calculated_price': quote.calculated_price,
        'status': quote.status,
        'created_at': quote.created_at.isoformat(),
        'expires_at': quote.expires_at.isoformat() if quote.expires_at else None
    })

# ==================== Policies ====================
@app.route('/api/policies', methods=['OPTIONS'])
def handle_policies_options():
    """Handle OPTIONS requests for policies endpoint"""
    return '', 200

@app.route('/api/policies', methods=['GET'])
@requires_auth
def get_user_policies():
    """Get all policies for current user"""
    logger.info("GET USER POLICIES ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    policies = Policy.query.filter_by(user_id=user.id).order_by(Policy.created_at.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'policy_number': p.policy_number,
        'product_name': p.product.name,
        'premium_amount': p.premium_amount,
        'start_date': p.start_date.isoformat(),
        'end_date': p.end_date.isoformat(),
        'status': p.status
    } for p in policies])

@app.route('/api/policies', methods=['POST'])
@requires_auth
def create_policy():
    """Create a new policy from a quote"""
    logger.info("CREATE POLICY ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    if 'quote_id' not in data:
        return jsonify({'error': 'quote_id is required'}), 400
    
    quote = Quote.query.filter_by(id=data['quote_id'], user_id=user.id).first()
    if not quote:
        return jsonify({'error': 'Quote not found'}), 404
    
    if quote.status != 'Pending':
        return jsonify({'error': 'Quote is not available for purchase'}), 400
    
    if quote.expires_at and quote.expires_at < datetime.utcnow():
        quote.status = 'Expired'
        db.session.commit()
        return jsonify({'error': 'Quote has expired'}), 400
    
    start_date = parser.parse(data.get('start_date', datetime.utcnow().isoformat()))
    end_date = parser.parse(data.get('end_date', (datetime.utcnow() + timedelta(days=365)).isoformat()))
    
    policy = Policy(
        user_id=user.id,
        product_id=quote.product_id,
        quote_id=quote.id,
        start_date=start_date,
        end_date=end_date,
        premium_amount=quote.calculated_price,
        status='Active'
    )
    
    quote.status = 'Accepted'
    db.session.add(policy)
    db.session.commit()
    
    return jsonify({
        'id': policy.id,
        'policy_number': policy.policy_number,
        'premium_amount': policy.premium_amount,
        'start_date': policy.start_date.isoformat(),
        'end_date': policy.end_date.isoformat(),
        'status': policy.status
    }), 201

@app.route('/api/policies/<int:policy_id>', methods=['OPTIONS'])
def handle_policy_options(policy_id):
    """Handle OPTIONS requests for specific policy endpoint"""
    return '', 200

@app.route('/api/policies/<int:policy_id>', methods=['GET'])
@requires_auth
def get_policy(policy_id):
    """Get specific policy details"""
    logger.info(f"GET POLICY ENDPOINT HIT for policy_id: {policy_id}")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    policy = Policy.query.filter_by(id=policy_id, user_id=user.id).first_or_404()
    
    return jsonify({
        'id': policy.id,
        'policy_number': policy.policy_number,
        'product': {
            'id': policy.product.id,
            'name': policy.product.name,
            'category': policy.product.category,
            'coverage_details': policy.product.coverage_details
        },
        'premium_amount': policy.premium_amount,
        'start_date': policy.start_date.isoformat(),
        'end_date': policy.end_date.isoformat(),
        'status': policy.status,
        'created_at': policy.created_at.isoformat()
    })

# ==================== Payments ====================
@app.route('/api/payments', methods=['OPTIONS'])
def handle_payments_options():
    """Handle OPTIONS requests for payments endpoint"""
    return '', 200

@app.route('/api/payments', methods=['GET'])
@requires_auth
def get_user_payments():
    """Get all payments for current user"""
    logger.info("GET USER PAYMENTS ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    payments = Payment.query.filter_by(user_id=user.id).order_by(Payment.payment_date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'transaction_id': p.transaction_id,
        'policy_number': p.policy.policy_number,
        'amount': p.amount,
        'payment_date': p.payment_date.isoformat(),
        'payment_method': p.payment_method,
        'status': p.status
    } for p in payments])

@app.route('/api/policies/<int:policy_id>/payments', methods=['OPTIONS'])
def handle_policy_payments_options(policy_id):
    """Handle OPTIONS requests for policy payments endpoint"""
    return '', 200

@app.route('/api/policies/<int:policy_id>/payments', methods=['POST'])
@requires_auth
def create_payment(policy_id):
    """Create a payment for a policy"""
    logger.info(f"CREATE PAYMENT ENDPOINT HIT for policy_id: {policy_id}")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    policy = Policy.query.filter_by(id=policy_id, user_id=user.id).first()
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    data = request.json or {}
    
    payment = Payment(
        user_id=user.id,
        policy_id=policy.id,
        amount=policy.premium_amount,
        payment_method=data.get('payment_method', 'Credit Card'),
        status='Completed'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        'id': payment.id,
        'transaction_id': payment.transaction_id,
        'amount': payment.amount,
        'payment_date': payment.payment_date.isoformat(),
        'payment_method': payment.payment_method,
        'status': payment.status
    }), 201

# ==================== Claims ====================
@app.route('/api/claims', methods=['OPTIONS'])
def handle_claims_options():
    """Handle OPTIONS requests for claims endpoint"""
    return '', 200

@app.route('/api/claims', methods=['GET'])
@requires_auth
def get_user_claims():
    """Get all claims for current user"""
    logger.info("GET USER CLAIMS ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    claims = Claim.query.filter_by(user_id=user.id).order_by(Claim.filing_date.desc()).all()
    
    return jsonify([{
        'id': c.id,
        'claim_number': c.claim_number,
        'policy_number': c.policy.policy_number,
        'incident_date': c.incident_date.isoformat(),
        'filing_date': c.filing_date.isoformat(),
        'claim_amount': c.claim_amount,
        'status': c.status,
        'documents': c.documents or []
    } for c in claims])

@app.route('/api/claims', methods=['POST'])
@requires_auth
def create_claim():
    """File a new claim"""
    logger.info("CREATE CLAIM ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    
    required_fields = ['policy_id', 'incident_date', 'description', 'claim_amount']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    policy = Policy.query.filter_by(id=data['policy_id'], user_id=user.id).first()
    if not policy:
        return jsonify({'error': 'Policy not found'}), 404
    
    try:
        incident_date = parser.parse(data['incident_date'])
    except:
        return jsonify({'error': 'Invalid incident date format'}), 400
    
    claim = Claim(
        user_id=user.id,
        policy_id=policy.id,
        incident_date=incident_date,
        description=data['description'],
        claim_amount=float(data['claim_amount']),
        status='Submitted',
        documents=[]
    )
    
    db.session.add(claim)
    db.session.commit()
    
    return jsonify({
        'id': claim.id,
        'claim_number': claim.claim_number,
        'status': claim.status,
        'filing_date': claim.filing_date.isoformat()
    }), 201

@app.route('/api/claims/<int:claim_id>', methods=['OPTIONS'])
def handle_claim_options(claim_id):
    """Handle OPTIONS requests for specific claim endpoint"""
    return '', 200

@app.route('/api/claims/<int:claim_id>', methods=['GET'])
@requires_auth
def get_claim(claim_id):
    """Get specific claim details"""
    logger.info(f"GET CLAIM ENDPOINT HIT for claim_id: {claim_id}")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    claim = Claim.query.filter_by(id=claim_id, user_id=user.id).first_or_404()
    
    return jsonify({
        'id': claim.id,
        'claim_number': claim.claim_number,
        'policy': {
            'id': claim.policy.id,
            'policy_number': claim.policy.policy_number,
            'product_name': claim.policy.product.name
        },
        'incident_date': claim.incident_date.isoformat(),
        'filing_date': claim.filing_date.isoformat(),
        'description': claim.description,
        'claim_amount': claim.claim_amount,
        'status': claim.status,
        'documents': claim.documents or [],
        'approved_amount': claim.approved_amount,
        'resolution_date': claim.resolution_date.isoformat() if claim.resolution_date else None
    })

# ==================== Document Upload ====================
@app.route('/api/claims/<int:claim_id>/documents', methods=['OPTIONS'])
def handle_document_options(claim_id):
    """Handle OPTIONS requests for document upload endpoint"""
    return '', 200

@app.route('/api/claims/<int:claim_id>/documents', methods=['POST'])
@requires_auth
def upload_claim_document(claim_id):
    """Upload a document for a claim"""
    logger.info(f"UPLOAD DOCUMENT ENDPOINT HIT for claim_id: {claim_id}")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    claim = Claim.query.filter_by(id=claim_id, user_id=user.id).first()
    if not claim:
        return jsonify({'error': 'Claim not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"{claim.claim_number}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
    
    if app.config['USE_LOCAL_STORAGE']:
        upload_path = os.path.join(app.config['LOCAL_STORAGE_PATH'], 'documents')
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        document_url = f"/api/documents/{unique_filename}"
    else:
        # Azure Blob Storage integration
        try:
            from azure.storage.blob import BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(app.config['AZURE_STORAGE_CONNECTION_STRING'])
            container_client = blob_service_client.get_container_client(app.config['AZURE_STORAGE_CONTAINER'])
            blob_client = container_client.get_blob_client(unique_filename)
            blob_client.upload_blob(file)
            document_url = blob_client.url
        except ImportError:
            logger.error("Azure Storage SDK not installed")
            return jsonify({'error': 'Document storage not configured'}), 500
    
    current_docs = claim.documents or []
    if not isinstance(current_docs, list):
        current_docs = []
    
    current_docs.append({
        'filename': filename,
        'url': document_url,
        'uploaded_at': datetime.utcnow().isoformat()
    })
    
    claim.documents = current_docs
    db.session.commit()
    
    return jsonify({
        'message': 'Document uploaded successfully',
        'document_url': document_url,
        'documents': current_docs
    }), 200

@app.route('/api/documents/<path:filename>', methods=['GET'])
def get_document(filename):
    """Retrieve a document"""
    if not app.config['USE_LOCAL_STORAGE']:
        return jsonify({'error': 'Document storage not available'}), 404
    
    file_path = os.path.join(app.config['LOCAL_STORAGE_PATH'], 'documents', filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'Document not found'}), 404
    
    return send_file(file_path)

# ==================== Dashboard ====================
@app.route('/api/dashboard', methods=['OPTIONS'])
def handle_dashboard_options():
    """Handle OPTIONS requests for dashboard endpoint"""
    return '', 200

@app.route('/api/dashboard', methods=['GET'])
@requires_auth
def get_dashboard():
    """Get dashboard summary for authenticated user"""
    logger.info("GET DASHBOARD ENDPOINT HIT")
    
    auth0_id = request.user.get('sub')
    user = User.query.filter_by(auth0_id=auth0_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get counts
    active_policies = Policy.query.filter_by(user_id=user.id, status='Active').count()
    pending_quotes = Quote.query.filter_by(user_id=user.id, status='Pending').count()
    open_claims = Claim.query.filter_by(user_id=user.id, status='Submitted').count()
    
    # Get recent items
    recent_policies = Policy.query.filter_by(user_id=user.id)\
        .order_by(Policy.created_at.desc())\
        .limit(5).all()
    
    recent_quotes = Quote.query.filter_by(user_id=user.id)\
        .order_by(Quote.created_at.desc())\
        .limit(5).all()
    
    recent_claims = Claim.query.filter_by(user_id=user.id)\
        .order_by(Claim.filing_date.desc())\
        .limit(5).all()
    
    return jsonify({
        'summary': {
            'active_policies': active_policies,
            'pending_quotes': pending_quotes,
            'open_claims': open_claims
        },
        'recent_policies': [{
            'id': p.id,
            'policy_number': p.policy_number,
            'product_name': p.product.name,
            'premium_amount': p.premium_amount,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        } for p in recent_policies],
        'recent_quotes': [{
            'id': q.id,
            'quote_number': q.quote_number,
            'product_name': q.product.name,
            'calculated_price': q.calculated_price,
            'status': q.status,
            'created_at': q.created_at.isoformat()
        } for q in recent_quotes],
        'recent_claims': [{
            'id': c.id,
            'claim_number': c.claim_number,
            'policy_number': c.policy.policy_number,
            'claim_amount': c.claim_amount,
            'status': c.status,
            'filing_date': c.filing_date.isoformat()
        } for c in recent_claims]
    })

print("\n" + "="*60)
print("REGISTERED ROUTES - VERIFY ALL ENDPOINTS ARE LISTED")
print("="*60)
api_routes = []
for rule in app.url_map.iter_rules():
    if '/api/' in str(rule):
        api_routes.append(f"{rule.endpoint:30} {rule.methods} -> {rule}")

for route in sorted(api_routes):
    print(route)

print("="*60)
print(f"Total API routes: {len(api_routes)}")
print("="*60 + "\n")

# Add startup complete message
logger.info("="*60)
logger.info("APPLICATION STARTUP COMPLETE")
logger.info(f"Total API routes registered: {len(api_routes)}")
logger.info("="*60)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    print(f"\n{'='*50}")
    print(f"Starting Insurance API Server")
    print(f"{'='*50}")
    print(f"Environment: {app.config.get('ENV', 'production')}")
    print(f"Port: {port}")
    print(f"Debug mode: {debug}")
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
    if '@' in db_uri:
        db_display = db_uri.split('@')[0].split(':')[0] + '://***:***@' + db_uri.split('@')[1]
    else:
        db_display = db_uri
    print(f"Database: {db_display}")
    print(f"CORS origins: {app.config.get('CORS_ORIGINS', [])}")
    print(f"{'='*50}\n")
    
    try:
        logger.info(f"Starting server on 0.0.0.0:{port} (debug={debug})")
        app.run(debug=debug, host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\n✗ Server failed to start: {e}")