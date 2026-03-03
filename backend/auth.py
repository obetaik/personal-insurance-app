import json
from functools import wraps
from urllib.request import urlopen
import logging
from flask import request, jsonify
from jose import jwt
import os

# Set up logging
logger = logging.getLogger(__name__)

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    auth = request.headers.get('Authorization', None)
    logger.debug(f"Auth header: {auth}")
    
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected'
        }, 401)

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer"'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be Bearer token'
        }, 401)

    token = parts[1]
    logger.debug(f"Token extracted: {token[:20]}...")
    return token

def requires_auth(f):
    """Determines if the Access Token is valid"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            
            # Check if we should skip auth (for development)
            skip_auth = os.environ.get('SKIP_AUTH', 'false').lower() == 'true'
            logger.info(f"SKIP_AUTH: {skip_auth}")
            
            if skip_auth:
                logger.info("⚠️ Skipping Auth0 validation - using mock user")
                request.user = {
                    'sub': 'auth0|test123',
                    'email': 'test@example.com',
                    'name': 'Test User'
                }
                return f(*args, **kwargs)
            
            # Get environment variables
            auth0_domain = os.environ.get('AUTH0_DOMAIN')
            auth0_audience = os.environ.get('AUTH0_API_AUDIENCE')
            auth0_algorithms = os.environ.get('AUTH0_ALGORITHMS', 'RS256').split(',')
            
            logger.info(f"Auth0 Domain: {auth0_domain}")
            logger.info(f"Auth0 Audience: {auth0_audience}")
            logger.info(f"Auth0 Algorithms: {auth0_algorithms}")
            
            if not auth0_domain or not auth0_audience:
                logger.error("Missing Auth0 configuration")
                raise AuthError({
                    'code': 'configuration_error',
                    'description': 'Auth0 not properly configured'
                }, 500)
            
            # Get JWKS
            jwks_url = f'https://{auth0_domain}/.well-known/jwks.json'
            logger.info(f"Fetching JWKS from: {jwks_url}")
            
            try:
                jsonurl = urlopen(jwks_url)
                jwks = json.loads(jsonurl.read())
                logger.info(f"JWKS fetched, found {len(jwks.get('keys', []))} keys")
            except Exception as e:
                logger.error(f"Failed to fetch JWKS: {e}")
                raise AuthError({
                    'code': 'jwks_error',
                    'description': f'Failed to fetch JWKS: {str(e)}'
                }, 500)
            
            # Get token header
            try:
                unverified_header = jwt.get_unverified_header(token)
                logger.info(f"Token header: kid={unverified_header.get('kid')}, alg={unverified_header.get('alg')}")
            except Exception as e:
                logger.error(f"Failed to parse token header: {e}")
                raise AuthError({
                    'code': 'invalid_token',
                    'description': f'Invalid token header: {str(e)}'
                }, 401)
            
            # Find matching key
            rsa_key = {}
            for key in jwks.get('keys', []):
                if key.get('kid') == unverified_header.get('kid'):
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    logger.info(f"✅ Found matching key with kid: {key['kid']}")
                    break
            
            if not rsa_key:
                logger.error(f"❌ No matching key found for kid: {unverified_header.get('kid')}")
                raise AuthError({
                    'code': 'invalid_header',
                    'description': 'Unable to find appropriate key'
                }, 401)
            
            # Validate the token
            try:
                logger.info("Attempting to decode token...")
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=auth0_algorithms,
                    audience=auth0_audience,
                    issuer=f'https://{auth0_domain}/'
                )
                
                logger.info(f"✅ Token validated successfully for user: {payload.get('sub')}")
                logger.debug(f"Token payload: {payload}")
                
                request.user = payload
                
            except jwt.ExpiredSignatureError:
                logger.error("❌ Token expired")
                raise AuthError({
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 401)
            except jwt.JWTClaimsError as e:
                logger.error(f"❌ JWT Claims Error: {e}")
                raise AuthError({
                    'code': 'invalid_claims',
                    'description': f'Incorrect claims: {str(e)}'
                }, 401)
            except Exception as e:
                logger.error(f"❌ Token validation error: {e}")
                raise AuthError({
                    'code': 'invalid_header',
                    'description': f'Unable to parse authentication token: {str(e)}'
                }, 400)
            
            return f(*args, **kwargs)
            
        except AuthError as ex:
            logger.error(f"AuthError: {ex.error} - Status: {ex.status_code}")
            return jsonify(ex.error), ex.status_code
    
    return decorated