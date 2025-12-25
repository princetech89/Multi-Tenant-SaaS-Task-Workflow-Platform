"""
Organization Invitation System with Token Management
Complete system for user invitations with secure tokens, expiration, and role assignment
"""
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import hashlib
import json

# ============================================================================
# INVITATION TOKEN MANAGER
# ============================================================================

class InvitationStatus(str, Enum):
    """Status of an invitation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"

class Role(str, Enum):
    """User roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class InvitationToken:
    """Represents an invitation token"""
    
    def __init__(
        self,
        invitation_id: str,
        organization_id: str,
        email: str,
        role: Role,
        invited_by: str,
        token: str,
        expires_at: datetime,
        created_at: datetime,
        status: InvitationStatus = InvitationStatus.PENDING
    ):
        self.invitation_id = invitation_id
        self.organization_id = organization_id
        self.email = email
        self.role = role
        self.invited_by = invited_by
        self.token = token
        self.expires_at = expires_at
        self.created_at = created_at
        self.status = status
        self.accepted_at = None
        self.metadata = {}
    
    def is_valid(self) -> bool:
        """Check if invitation is valid"""
        return (
            self.status == InvitationStatus.PENDING and
            datetime.utcnow() < self.expires_at
        )
    
    def is_expired(self) -> bool:
        """Check if invitation is expired"""
        return datetime.utcnow() >= self.expires_at
    
    def accept(self, user_id: str):
        """Mark invitation as accepted"""
        if not self.is_valid():
            raise ValueError("Cannot accept invalid or expired invitation")
        
        self.status = InvitationStatus.ACCEPTED
        self.accepted_at = datetime.utcnow()
        self.metadata['accepted_by_user_id'] = user_id
    
    def revoke(self):
        """Revoke the invitation"""
        if self.status == InvitationStatus.ACCEPTED:
            raise ValueError("Cannot revoke accepted invitation")
        
        self.status = InvitationStatus.REVOKED
        self.metadata['revoked_at'] = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'invitation_id': self.invitation_id,
            'organization_id': self.organization_id,
            'email': self.email,
            'role': self.role.value,
            'invited_by': self.invited_by,
            'token': self.token,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'is_valid': self.is_valid(),
            'is_expired': self.is_expired(),
            'metadata': self.metadata
        }

class InvitationManager:
    """Manages organization invitations"""
    
    def __init__(self, token_expiry_hours: int = 72):
        self.token_expiry_hours = token_expiry_hours
        self.invitations: Dict[str, InvitationToken] = {}
        self.email_to_invitations: Dict[str, List[str]] = {}
        self.org_to_invitations: Dict[str, List[str]] = {}
    
    def generate_secure_token(self) -> str:
        """Generate a cryptographically secure invitation token"""
        # Generate 32 bytes of random data and convert to hex
        return secrets.token_urlsafe(32)
    
    def create_invitation(
        self,
        organization_id: str,
        email: str,
        role: Role,
        invited_by: str,
        custom_message: Optional[str] = None
    ) -> InvitationToken:
        """
        Create a new invitation token
        
        Args:
            organization_id: Organization to invite user to
            email: Email address of the invitee
            role: Role to assign to the user
            invited_by: User ID of the person sending the invitation
            custom_message: Optional custom message to include
        
        Returns:
            InvitationToken object
        """
        # Check if user already has pending invitation
        existing = self.get_pending_invitation_by_email(organization_id, email)
        if existing:
            raise ValueError(f"User {email} already has a pending invitation to this organization")
        
        invitation_id = str(uuid.uuid4())
        token = self.generate_secure_token()
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(hours=self.token_expiry_hours)
        
        invitation = InvitationToken(
            invitation_id=invitation_id,
            organization_id=organization_id,
            email=email.lower(),
            role=role,
            invited_by=invited_by,
            token=token,
            expires_at=expires_at,
            created_at=created_at
        )
        
        if custom_message:
            invitation.metadata['custom_message'] = custom_message
        
        # Store invitation
        self.invitations[invitation_id] = invitation
        
        # Index by email
        if email not in self.email_to_invitations:
            self.email_to_invitations[email] = []
        self.email_to_invitations[email].append(invitation_id)
        
        # Index by organization
        if organization_id not in self.org_to_invitations:
            self.org_to_invitations[organization_id] = []
        self.org_to_invitations[organization_id].append(invitation_id)
        
        return invitation
    
    def get_invitation_by_token(self, token: str) -> Optional[InvitationToken]:
        """Get invitation by token"""
        for invitation in self.invitations.values():
            if invitation.token == token:
                return invitation
        return None
    
    def get_invitation_by_id(self, invitation_id: str) -> Optional[InvitationToken]:
        """Get invitation by ID"""
        return self.invitations.get(invitation_id)
    
    def get_pending_invitation_by_email(
        self,
        organization_id: str,
        email: str
    ) -> Optional[InvitationToken]:
        """Get pending invitation for email in organization"""
        invitation_ids = self.email_to_invitations.get(email.lower(), [])
        
        for invitation_id in invitation_ids:
            invitation = self.invitations[invitation_id]
            if (invitation.organization_id == organization_id and
                invitation.status == InvitationStatus.PENDING):
                return invitation
        
        return None
    
    def get_organization_invitations(
        self,
        organization_id: str,
        status_filter: Optional[InvitationStatus] = None
    ) -> List[InvitationToken]:
        """Get all invitations for an organization"""
        invitation_ids = self.org_to_invitations.get(organization_id, [])
        invitations = [self.invitations[inv_id] for inv_id in invitation_ids]
        
        if status_filter:
            invitations = [inv for inv in invitations if inv.status == status_filter]
        
        return sorted(invitations, key=lambda x: x.created_at, reverse=True)
    
    def accept_invitation(self, token: str, user_id: str) -> InvitationToken:
        """Accept an invitation"""
        invitation = self.get_invitation_by_token(token)
        
        if not invitation:
            raise ValueError("Invalid invitation token")
        
        if not invitation.is_valid():
            if invitation.is_expired():
                invitation.status = InvitationStatus.EXPIRED
                raise ValueError("Invitation has expired")
            raise ValueError(f"Invitation is {invitation.status.value}")
        
        invitation.accept(user_id)
        return invitation
    
    def revoke_invitation(self, invitation_id: str) -> InvitationToken:
        """Revoke an invitation"""
        invitation = self.get_invitation_by_id(invitation_id)
        
        if not invitation:
            raise ValueError("Invitation not found")
        
        invitation.revoke()
        return invitation
    
    def cleanup_expired_invitations(self, organization_id: Optional[str] = None) -> int:
        """Mark expired invitations and return count"""
        count = 0
        
        invitations_to_check = []
        if organization_id:
            invitation_ids = self.org_to_invitations.get(organization_id, [])
            invitations_to_check = [self.invitations[inv_id] for inv_id in invitation_ids]
        else:
            invitations_to_check = list(self.invitations.values())
        
        for invitation in invitations_to_check:
            if (invitation.status == InvitationStatus.PENDING and
                invitation.is_expired()):
                invitation.status = InvitationStatus.EXPIRED
                count += 1
        
        return count
    
    def get_invitation_stats(self, organization_id: str) -> dict:
        """Get invitation statistics for organization"""
        invitations = self.get_organization_invitations(organization_id)
        
        stats = {
            'total': len(invitations),
            'pending': sum(1 for inv in invitations if inv.status == InvitationStatus.PENDING),
            'accepted': sum(1 for inv in invitations if inv.status == InvitationStatus.ACCEPTED),
            'expired': sum(1 for inv in invitations if inv.status == InvitationStatus.EXPIRED),
            'revoked': sum(1 for inv in invitations if inv.status == InvitationStatus.REVOKED),
            'by_role': {}
        }
        
        for invitation in invitations:
            role = invitation.role.value
            if role not in stats['by_role']:
                stats['by_role'][role] = 0
            stats['by_role'][role] += 1
        
        return stats

# ============================================================================
# DEMONSTRATION
# ============================================================================

print("=" * 100)
print("ORGANIZATION INVITATION SYSTEM WITH SECURE TOKENS")
print("=" * 100)
print()

# Initialize invitation manager
invitation_mgr = InvitationManager(token_expiry_hours=72)

# Test organization and users
org_id = str(uuid.uuid4())
admin_user_id = str(uuid.uuid4())

print("📧 CREATING INVITATIONS")
print("-" * 100)

# Create invitations
invitations_created = []

try:
    inv1 = invitation_mgr.create_invitation(
        organization_id=org_id,
        email="alice@example.com",
        role=Role.ADMIN,
        invited_by=admin_user_id,
        custom_message="Welcome to our team!"
    )
    invitations_created.append(inv1)
    print(f"✅ Created invitation for alice@example.com as {inv1.role.value}")
    print(f"   Token: {inv1.token[:20]}...")
    print(f"   Expires: {inv1.expires_at.isoformat()}")
    
    inv2 = invitation_mgr.create_invitation(
        organization_id=org_id,
        email="bob@example.com",
        role=Role.MEMBER,
        invited_by=admin_user_id
    )
    invitations_created.append(inv2)
    print(f"✅ Created invitation for bob@example.com as {inv2.role.value}")
    
    inv3 = invitation_mgr.create_invitation(
        organization_id=org_id,
        email="charlie@example.com",
        role=Role.VIEWER,
        invited_by=admin_user_id
    )
    invitations_created.append(inv3)
    print(f"✅ Created invitation for charlie@example.com as {inv3.role.value}")

except Exception as e:
    print(f"❌ Error creating invitation: {e}")

print()
print("🔍 VALIDATING INVITATIONS")
print("-" * 100)

# Validate tokens
for inv in invitations_created:
    retrieved = invitation_mgr.get_invitation_by_token(inv.token)
    if retrieved:
        print(f"✅ Token validation successful for {inv.email}")
        print(f"   Valid: {retrieved.is_valid()}, Status: {retrieved.status.value}")
    else:
        print(f"❌ Token validation failed for {inv.email}")

print()
print("✓ ACCEPTING INVITATION")
print("-" * 100)

# Accept an invitation
try:
    user_id = str(uuid.uuid4())
    accepted_inv = invitation_mgr.accept_invitation(inv1.token, user_id)
    print(f"✅ Invitation accepted by {accepted_inv.email}")
    print(f"   User ID: {user_id}")
    print(f"   Role assigned: {accepted_inv.role.value}")
    print(f"   Accepted at: {accepted_inv.accepted_at.isoformat()}")
except Exception as e:
    print(f"❌ Error accepting invitation: {e}")

print()
print("⛔ REVOKING INVITATION")
print("-" * 100)

# Revoke an invitation
try:
    revoked_inv = invitation_mgr.revoke_invitation(inv3.invitation_id)
    print(f"✅ Invitation revoked for {revoked_inv.email}")
    print(f"   Status: {revoked_inv.status.value}")
except Exception as e:
    print(f"❌ Error revoking invitation: {e}")

print()
print("📊 INVITATION STATISTICS")
print("-" * 100)

stats = invitation_mgr.get_invitation_stats(org_id)
print(f"Total invitations: {stats['total']}")
print(f"Pending: {stats['pending']}")
print(f"Accepted: {stats['accepted']}")
print(f"Expired: {stats['expired']}")
print(f"Revoked: {stats['revoked']}")
print()
print("By role:")
for role, count in stats['by_role'].items():
    print(f"  {role}: {count}")

print()
print("📋 ALL INVITATIONS FOR ORGANIZATION")
print("-" * 100)

all_invitations = invitation_mgr.get_organization_invitations(org_id)
for inv in all_invitations:
    print(f"• {inv.email:30s} | Role: {inv.role.value:10s} | Status: {inv.status.value:10s} | Valid: {inv.is_valid()}")

print()
print("=" * 100)
print("✅ Invitation System Tested Successfully")
print("=" * 100)
print()
print("KEY FEATURES:")
print("• Secure token generation using secrets.token_urlsafe()")
print("• Configurable expiration time (default 72 hours)")
print("• Automatic expiration checking")
print("• Role assignment on invitation")
print("• Invitation revocation support")
print("• Duplicate invitation prevention")
print("• Organization-level invitation management")
print("• Custom messages support")
print("• Comprehensive statistics")
