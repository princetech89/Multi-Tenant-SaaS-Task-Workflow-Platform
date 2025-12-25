import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict as JWTDict, Optional as JWTOptional, Tuple as JWTTuple

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use environment variable
REFRESH_SECRET_KEY = secrets.token_urlsafe(32)
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"

class JWTTokenManager:
    """Manages JWT access and refresh tokens with secure generation and validation"""
    
    def __init__(self, secret_key: str, refresh_secret: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.refresh_secret = refresh_secret
        self.algorithm = algorithm
    
    def generate_access_token(self, user_id: str, email: str, additional_claims: JWTOptional[JWTDict] = None) -> str:
        """Generate JWT access token with short expiration"""
        payload = {
            'user_id': user_id,
            'email': email,
            'type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def generate_refresh_token(self, user_id: str) -> str:
        """Generate JWT refresh token with longer expiration"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            'jti': secrets.token_urlsafe(16)  # Unique token ID for revocation tracking
        }
        
        token = jwt.encode(payload, self.refresh_secret, algorithm=self.algorithm)
        return token
    
    def generate_token_pair(self, user_id: str, email: str, additional_claims: JWTOptional[JWTDict] = None) -> JWTTuple[str, str]:
        """Generate both access and refresh tokens"""
        access_token = self.generate_access_token(user_id, email, additional_claims)
        refresh_token = self.generate_refresh_token(user_id)
        return access_token, refresh_token
    
    def validate_access_token(self, token: str) -> JWTDict:
        """Validate access token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Access token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid access token: {str(e)}")
    
    def validate_refresh_token(self, token: str) -> JWTDict:
        """Validate refresh token and return payload"""
        try:
            payload = jwt.decode(token, self.refresh_secret, algorithms=[self.algorithm])
            
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def rotate_tokens(self, refresh_token: str, email: str) -> JWTTuple[str, str]:
        """Validate refresh token and generate new token pair"""
        payload = self.validate_refresh_token(refresh_token)
        user_id = payload['user_id']
        
        # Generate new token pair
        new_access_token, new_refresh_token = self.generate_token_pair(user_id, email)
        return new_access_token, new_refresh_token


# Initialize token manager
jwt_manager = JWTTokenManager(SECRET_KEY, REFRESH_SECRET_KEY, ALGORITHM)

print("🔐 JWT Token Manager initialized")
print(f"✓ Access token expiration: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
print(f"✓ Refresh token expiration: {REFRESH_TOKEN_EXPIRE_DAYS} days")
print(f"✓ Algorithm: {ALGORITHM}")
print(f"✓ Secret keys generated securely")
