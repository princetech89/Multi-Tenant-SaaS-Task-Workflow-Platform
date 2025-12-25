import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class AuthenticationSystem:
    """Complete authentication system integrating JWT, OAuth, and session management"""
    
    def __init__(self, jwt_manager, oauth_manager, session_manager):
        self.jwt_manager = jwt_manager
        self.oauth_manager = oauth_manager
        self.session_manager = session_manager
    
    # === Standard Login/Registration ===
    
    def register_user(self, user_id: str, email: str, additional_claims: Optional[Dict] = None) -> Dict:
        """Register new user and create initial session"""
        access_token, refresh_token = self.jwt_manager.generate_token_pair(
            user_id, email, additional_claims
        )
        
        session_id = self.session_manager.create_session(
            user_id, email, access_token, refresh_token,
            metadata={'auth_method': 'standard', 'created': str(datetime.utcnow())}
        )
        
        return {
            'user_id': user_id,
            'email': email,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_id': session_id,
            'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def login_user(self, user_id: str, email: str) -> Dict:
        """Login existing user and create session"""
        return self.register_user(user_id, email)
    
    # === OAuth Flow ===
    
    def initiate_oauth_flow(self, provider: str) -> Dict:
        """Start OAuth flow - returns authorization URL"""
        auth_url, state = self.oauth_manager.generate_authorization_url(provider)
        
        return {
            'authorization_url': auth_url,
            'state': state,
            'provider': provider
        }
    
    def complete_oauth_flow(self, provider: str, code: str, state: str) -> Dict:
        """Complete OAuth flow after callback"""
        # Exchange code for OAuth access token
        oauth_token = self.oauth_manager.exchange_code_for_token(provider, code, state)
        
        # Get user info from provider
        user_info = self.oauth_manager.get_user_info(provider, oauth_token['access_token'])
        
        # Generate our JWT tokens
        user_id = f"{provider}_{user_info['provider_user_id']}"
        email = user_info['email']
        
        access_token, refresh_token = self.jwt_manager.generate_token_pair(
            user_id, email, {'oauth_provider': provider}
        )
        
        # Create session
        session_id = self.session_manager.create_session(
            user_id, email, access_token, refresh_token,
            metadata={
                'auth_method': 'oauth',
                'provider': provider,
                'oauth_user_info': user_info
            }
        )
        
        return {
            'user_id': user_id,
            'email': email,
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_id': session_id,
            'provider': provider
        }
    
    # === Token Operations ===
    
    def validate_request(self, access_token: str) -> Dict:
        """Validate access token from request"""
        # Check if token is blacklisted
        if self.session_manager.is_token_blacklisted(access_token):
            raise ValueError("Token has been revoked")
        
        # Validate token
        payload = self.jwt_manager.validate_access_token(access_token)
        
        return payload
    
    def refresh_tokens(self, refresh_token: str, session_id: str) -> Dict:
        """Refresh expired access token"""
        # Validate session
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError("Invalid or expired session")
        
        # Check if token is blacklisted
        if self.session_manager.is_token_blacklisted(refresh_token):
            raise ValueError("Refresh token has been revoked")
        
        # Rotate tokens
        new_access_token, new_refresh_token = self.jwt_manager.rotate_tokens(
            refresh_token, session['email']
        )
        
        # Update session
        self.session_manager.update_session_tokens(
            session_id, new_access_token, new_refresh_token
        )
        
        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session"""
        return self.session_manager.delete_session(session_id)
    
    # === Session Management ===
    
    def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user"""
        return self.session_manager.get_user_sessions(user_id)
    
    def cleanup_sessions(self) -> int:
        """Clean up expired sessions"""
        return self.session_manager.cleanup_expired_sessions()


# Initialize complete authentication system
auth_system = AuthenticationSystem(jwt_manager, oauth_manager, session_manager)

print("🔒 Complete Authentication System Ready")
print("=" * 50)
print("\n✅ Features Available:")
print("  • JWT token generation (access + refresh)")
print("  • Token validation and rotation")
print("  • OAuth 2.0 integration (Google, GitHub)")
print("  • Session management with expiration")
print("  • Token revocation/blacklisting")
print("  • CSRF protection")
print("\n📋 System Configuration:")
print(f"  • Access token lifetime: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
print(f"  • Refresh token lifetime: {REFRESH_TOKEN_EXPIRE_DAYS} days")
print(f"  • Session timeout: 24 hours")
print(f"  • Algorithm: {ALGORITHM}")
print("\n✓ Ready for end-to-end authentication flows")
