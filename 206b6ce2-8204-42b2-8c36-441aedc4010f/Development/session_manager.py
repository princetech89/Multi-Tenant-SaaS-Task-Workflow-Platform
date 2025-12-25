import secrets
from datetime import datetime, timedelta
from typing import Dict as SessionDict, Optional as SessionOptional

class SessionManager:
    """Manages user sessions with secure session IDs and expiration"""
    
    def __init__(self, session_timeout_hours: int = 24):
        self.sessions = {}  # In production, use Redis or database
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.blacklisted_tokens = set()  # For token revocation
    
    def create_session(self, user_id: str, email: str, access_token: str, 
                      refresh_token: str, metadata: SessionOptional[SessionDict] = None) -> str:
        """Create a new session and return session ID"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'email': email,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'expires_at': datetime.utcnow() + self.session_timeout,
            'metadata': metadata or {}
        }
        
        self.sessions[session_id] = session_data
        return session_id
    
    def get_session(self, session_id: str) -> SessionOptional[SessionDict]:
        """Retrieve session data if valid"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session expired
        if datetime.utcnow() > session['expires_at']:
            self.delete_session(session_id)
            return None
        
        # Update last activity
        session['last_activity'] = datetime.utcnow()
        return session
    
    def update_session_tokens(self, session_id: str, access_token: str, 
                             refresh_token: str) -> bool:
        """Update tokens in existing session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Blacklist old tokens
        self.blacklisted_tokens.add(session['access_token'])
        self.blacklisted_tokens.add(session['refresh_token'])
        
        # Update with new tokens
        session['access_token'] = access_token
        session['refresh_token'] = refresh_token
        session['last_activity'] = datetime.utcnow()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session (logout)"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Blacklist tokens on logout
            self.blacklisted_tokens.add(session['access_token'])
            self.blacklisted_tokens.add(session['refresh_token'])
            
            del self.sessions[session_id]
            return True
        return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token has been revoked"""
        return token in self.blacklisted_tokens
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions and return count"""
        now = datetime.utcnow()
        expired = [sid for sid, session in self.sessions.items() 
                  if now > session['expires_at']]
        
        for session_id in expired:
            self.delete_session(session_id)
        
        return len(expired)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)
    
    def get_user_sessions(self, user_id: str) -> list:
        """Get all active sessions for a user"""
        return [session for session in self.sessions.values() 
                if session['user_id'] == user_id]


# Initialize session manager
session_manager = SessionManager(session_timeout_hours=24)

print("📋 Session Manager initialized")
print(f"✓ Session timeout: 24 hours")
print(f"✓ Token blacklist enabled for revocation")
print(f"✓ Active sessions: {session_manager.get_active_sessions_count()}")
