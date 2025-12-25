from authlib.integrations.requests_client import OAuth2Session
from typing import Dict as OAuthDict, Optional as OAuthOptional
import secrets

# OAuth Configuration - In production, use environment variables
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"
GITHUB_CLIENT_ID = "your_github_client_id"
GITHUB_CLIENT_SECRET = "your_github_client_secret"

REDIRECT_URI = "http://localhost:8000/auth/callback"

class OAuthManager:
    """Manages OAuth 2.0 authentication flows for Google and GitHub"""
    
    def __init__(self):
        self.providers = {
            'google': {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'authorize_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile'
            },
            'github': {
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'authorize_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'userinfo_url': 'https://api.github.com/user',
                'scope': 'user:email'
            }
        }
        self.state_storage = {}  # In production, use Redis or database
    
    def generate_authorization_url(self, provider: str) -> tuple[str, str]:
        """Generate OAuth authorization URL with state parameter"""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        config = self.providers[provider]
        
        # Create OAuth2 session
        client = OAuth2Session(
            client_id=config['client_id'],
            redirect_uri=REDIRECT_URI,
            scope=config['scope']
        )
        
        # Generate authorization URL with state
        authorization_url, state = client.create_authorization_url(config['authorize_url'])
        
        # Store state for CSRF protection
        self.state_storage[state] = provider
        
        return authorization_url, state
    
    def exchange_code_for_token(self, provider: str, code: str, state: str) -> OAuthDict:
        """Exchange authorization code for access token"""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Verify state for CSRF protection
        if state not in self.state_storage or self.state_storage[state] != provider:
            raise ValueError("Invalid state parameter - possible CSRF attack")
        
        config = self.providers[provider]
        
        # Create OAuth2 session
        client = OAuth2Session(
            client_id=config['client_id'],
            redirect_uri=REDIRECT_URI
        )
        
        # Exchange code for token
        token = client.fetch_token(
            config['token_url'],
            code=code,
            client_secret=config['client_secret']
        )
        
        # Clean up state
        del self.state_storage[state]
        
        return token
    
    def get_user_info(self, provider: str, access_token: str) -> OAuthDict:
        """Fetch user information using access token"""
        if provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        config = self.providers[provider]
        
        # Create authenticated session
        client = OAuth2Session(token={'access_token': access_token})
        
        # Fetch user info
        response = client.get(config['userinfo_url'])
        response.raise_for_status()
        
        user_data = response.json()
        
        # Normalize user data across providers
        if provider == 'google':
            return {
                'provider': 'google',
                'provider_user_id': user_data['id'],
                'email': user_data['email'],
                'name': user_data.get('name'),
                'picture': user_data.get('picture')
            }
        elif provider == 'github':
            return {
                'provider': 'github',
                'provider_user_id': str(user_data['id']),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('avatar_url')
            }
        
        return user_data


# Initialize OAuth manager
oauth_manager = OAuthManager()

print("🌐 OAuth Manager initialized")
print(f"✓ Supported providers: Google, GitHub")
print(f"✓ Redirect URI: {REDIRECT_URI}")
print(f"✓ CSRF protection enabled with state parameter")
print("\n⚠️  Note: Configure actual client IDs and secrets in production")
