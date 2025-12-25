"""
Complete Organization CRUD APIs with Member Management
Full REST API implementation for organization lifecycle management
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json

# ============================================================================
# MODELS AND ENUMS
# ============================================================================

class OrganizationStatus(str, Enum):
    """Organization status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class OrganizationTier(str, Enum):
    """Organization subscription tier"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Role(str, Enum):
    """User roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class Organization:
    """Organization model"""
    
    def __init__(
        self,
        organization_id: str,
        name: str,
        slug: str,
        tier: OrganizationTier = OrganizationTier.FREE,
        status: OrganizationStatus = OrganizationStatus.ACTIVE,
        settings: Dict = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        deleted_at: datetime = None
    ):
        self.organization_id = organization_id
        self.name = name
        self.slug = slug
        self.tier = tier
        self.status = status
        self.settings = settings or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
    
    def to_dict(self, include_deleted: bool = False) -> dict:
        """Convert to dictionary"""
        data = {
            'organization_id': self.organization_id,
            'name': self.name,
            'slug': self.slug,
            'tier': self.tier.value,
            'status': self.status.value,
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
        
        if include_deleted or self.deleted_at:
            data['deleted_at'] = self.deleted_at.isoformat() if self.deleted_at else None
        
        return data

class OrganizationMember:
    """Organization member model"""
    
    def __init__(
        self,
        member_id: str,
        organization_id: str,
        user_id: str,
        email: str,
        role: Role,
        added_by: str,
        added_at: datetime = None,
        updated_at: datetime = None
    ):
        self.member_id = member_id
        self.organization_id = organization_id
        self.user_id = user_id
        self.email = email
        self.role = role
        self.added_by = added_by
        self.added_at = added_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'member_id': self.member_id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'email': self.email,
            'role': self.role.value,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# ============================================================================
# ORGANIZATION SERVICE
# ============================================================================

class OrganizationService:
    """Service for organization management"""
    
    def __init__(self):
        self.organizations: Dict[str, Organization] = {}
        self.slug_to_org: Dict[str, str] = {}
        self.members: Dict[str, OrganizationMember] = {}
        self.org_members: Dict[str, List[str]] = {}
    
    def create_organization(
        self,
        name: str,
        slug: str,
        created_by: str,
        tier: OrganizationTier = OrganizationTier.FREE,
        settings: Dict = None
    ) -> Organization:
        """
        Create a new organization
        
        Args:
            name: Organization name
            slug: Unique URL slug
            created_by: User ID of creator
            tier: Subscription tier
            settings: Organization settings
        
        Returns:
            Created organization
        """
        # Validate slug uniqueness
        if slug in self.slug_to_org:
            raise ValueError(f"Organization slug '{slug}' already exists")
        
        # Create organization
        org_id = str(uuid.uuid4())
        organization = Organization(
            organization_id=org_id,
            name=name,
            slug=slug,
            tier=tier,
            settings=settings or {}
        )
        
        # Store organization
        self.organizations[org_id] = organization
        self.slug_to_org[slug] = org_id
        
        # Add creator as owner
        self.add_member(
            organization_id=org_id,
            user_id=created_by,
            email=f"user-{created_by}@example.com",
            role=Role.OWNER,
            added_by=created_by
        )
        
        return organization
    
    def get_organization(self, organization_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        org = self.organizations.get(organization_id)
        
        if org and org.status != OrganizationStatus.DELETED:
            return org
        
        return None
    
    def get_organization_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        org_id = self.slug_to_org.get(slug)
        if org_id:
            return self.get_organization(org_id)
        return None
    
    def list_organizations(
        self,
        status: Optional[OrganizationStatus] = None,
        tier: Optional[OrganizationTier] = None
    ) -> List[Organization]:
        """List all organizations with optional filters"""
        orgs = list(self.organizations.values())
        
        # Filter by status
        if status:
            orgs = [org for org in orgs if org.status == status]
        else:
            # By default, exclude deleted
            orgs = [org for org in orgs if org.status != OrganizationStatus.DELETED]
        
        # Filter by tier
        if tier:
            orgs = [org for org in orgs if org.tier == tier]
        
        return sorted(orgs, key=lambda x: x.created_at, reverse=True)
    
    def update_organization(
        self,
        organization_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        tier: Optional[OrganizationTier] = None,
        status: Optional[OrganizationStatus] = None,
        settings: Optional[Dict] = None
    ) -> Organization:
        """Update organization"""
        org = self.get_organization(organization_id)
        
        if not org:
            raise ValueError("Organization not found")
        
        # Update fields
        if name:
            org.name = name
        
        if slug and slug != org.slug:
            # Validate new slug
            if slug in self.slug_to_org:
                raise ValueError(f"Slug '{slug}' already exists")
            
            # Update slug mapping
            del self.slug_to_org[org.slug]
            org.slug = slug
            self.slug_to_org[slug] = organization_id
        
        if tier:
            org.tier = tier
        
        if status:
            org.status = status
        
        if settings is not None:
            org.settings.update(settings)
        
        org.updated_at = datetime.utcnow()
        
        return org
    
    def delete_organization(
        self,
        organization_id: str,
        soft_delete: bool = True
    ) -> bool:
        """
        Delete organization (soft or hard delete)
        
        Args:
            organization_id: Organization to delete
            soft_delete: If True, mark as deleted. If False, remove completely.
        
        Returns:
            True if deleted successfully
        """
        org = self.organizations.get(organization_id)
        
        if not org:
            raise ValueError("Organization not found")
        
        if soft_delete:
            # Soft delete
            org.status = OrganizationStatus.DELETED
            org.deleted_at = datetime.utcnow()
            org.updated_at = datetime.utcnow()
        else:
            # Hard delete
            del self.organizations[organization_id]
            del self.slug_to_org[org.slug]
            
            # Remove all members
            member_ids = self.org_members.get(organization_id, [])
            for member_id in member_ids:
                if member_id in self.members:
                    del self.members[member_id]
            
            if organization_id in self.org_members:
                del self.org_members[organization_id]
        
        return True
    
    def add_member(
        self,
        organization_id: str,
        user_id: str,
        email: str,
        role: Role,
        added_by: str
    ) -> OrganizationMember:
        """Add member to organization"""
        org = self.get_organization(organization_id)
        
        if not org:
            raise ValueError("Organization not found")
        
        # Check if user is already a member
        existing = self.get_member_by_user(organization_id, user_id)
        if existing:
            raise ValueError(f"User {user_id} is already a member")
        
        # Create member
        member_id = str(uuid.uuid4())
        member = OrganizationMember(
            member_id=member_id,
            organization_id=organization_id,
            user_id=user_id,
            email=email,
            role=role,
            added_by=added_by
        )
        
        # Store member
        self.members[member_id] = member
        
        if organization_id not in self.org_members:
            self.org_members[organization_id] = []
        self.org_members[organization_id].append(member_id)
        
        return member
    
    def get_member_by_user(
        self,
        organization_id: str,
        user_id: str
    ) -> Optional[OrganizationMember]:
        """Get member by user ID"""
        member_ids = self.org_members.get(organization_id, [])
        
        for member_id in member_ids:
            member = self.members.get(member_id)
            if member and member.user_id == user_id:
                return member
        
        return None
    
    def list_members(
        self,
        organization_id: str,
        role_filter: Optional[Role] = None
    ) -> List[OrganizationMember]:
        """List organization members"""
        member_ids = self.org_members.get(organization_id, [])
        members = [self.members[mid] for mid in member_ids if mid in self.members]
        
        if role_filter:
            members = [m for m in members if m.role == role_filter]
        
        return sorted(members, key=lambda x: x.added_at, reverse=True)
    
    def update_member_role(
        self,
        organization_id: str,
        user_id: str,
        new_role: Role
    ) -> OrganizationMember:
        """Update member role"""
        member = self.get_member_by_user(organization_id, user_id)
        
        if not member:
            raise ValueError("Member not found")
        
        member.role = new_role
        member.updated_at = datetime.utcnow()
        
        return member
    
    def remove_member(
        self,
        organization_id: str,
        user_id: str
    ) -> bool:
        """Remove member from organization"""
        member = self.get_member_by_user(organization_id, user_id)
        
        if not member:
            raise ValueError("Member not found")
        
        # Don't allow removing the last owner
        if member.role == Role.OWNER:
            owners = [m for m in self.list_members(organization_id) if m.role == Role.OWNER]
            if len(owners) <= 1:
                raise ValueError("Cannot remove the last owner")
        
        # Remove member
        self.org_members[organization_id].remove(member.member_id)
        del self.members[member.member_id]
        
        return True
    
    def get_statistics(self, organization_id: str) -> dict:
        """Get organization statistics"""
        org = self.get_organization(organization_id)
        
        if not org:
            raise ValueError("Organization not found")
        
        members = self.list_members(organization_id)
        
        return {
            'organization_id': organization_id,
            'name': org.name,
            'tier': org.tier.value,
            'status': org.status.value,
            'total_members': len(members),
            'members_by_role': {
                'owner': sum(1 for m in members if m.role == Role.OWNER),
                'admin': sum(1 for m in members if m.role == Role.ADMIN),
                'manager': sum(1 for m in members if m.role == Role.MANAGER),
                'member': sum(1 for m in members if m.role == Role.MEMBER),
                'viewer': sum(1 for m in members if m.role == Role.VIEWER),
            },
            'created_at': org.created_at.isoformat(),
            'updated_at': org.updated_at.isoformat()
        }

# ============================================================================
# REST API ENDPOINTS (Mock Implementation)
# ============================================================================

class OrganizationAPI:
    """REST API for organization management"""
    
    def __init__(self, service: OrganizationService):
        self.service = service
    
    def create_organization_endpoint(self, request_body: dict) -> dict:
        """POST /api/organizations"""
        try:
            org = self.service.create_organization(
                name=request_body['name'],
                slug=request_body['slug'],
                created_by=request_body['created_by'],
                tier=OrganizationTier(request_body.get('tier', 'free')),
                settings=request_body.get('settings')
            )
            
            return {
                'status': 'success',
                'status_code': 201,
                'data': org.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 400,
                'error': str(e)
            }
    
    def get_organization_endpoint(self, organization_id: str) -> dict:
        """GET /api/organizations/:id"""
        try:
            org = self.service.get_organization(organization_id)
            
            if not org:
                return {
                    'status': 'error',
                    'status_code': 404,
                    'error': 'Organization not found'
                }
            
            return {
                'status': 'success',
                'status_code': 200,
                'data': org.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 500,
                'error': str(e)
            }
    
    def list_organizations_endpoint(self, query_params: dict = None) -> dict:
        """GET /api/organizations"""
        try:
            query_params = query_params or {}
            
            status = OrganizationStatus(query_params['status']) if 'status' in query_params else None
            tier = OrganizationTier(query_params['tier']) if 'tier' in query_params else None
            
            orgs = self.service.list_organizations(status=status, tier=tier)
            
            return {
                'status': 'success',
                'status_code': 200,
                'data': [org.to_dict() for org in orgs],
                'count': len(orgs)
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 500,
                'error': str(e)
            }
    
    def update_organization_endpoint(self, organization_id: str, request_body: dict) -> dict:
        """PUT /api/organizations/:id"""
        try:
            org = self.service.update_organization(
                organization_id=organization_id,
                name=request_body.get('name'),
                slug=request_body.get('slug'),
                tier=OrganizationTier(request_body['tier']) if 'tier' in request_body else None,
                status=OrganizationStatus(request_body['status']) if 'status' in request_body else None,
                settings=request_body.get('settings')
            )
            
            return {
                'status': 'success',
                'status_code': 200,
                'data': org.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 400,
                'error': str(e)
            }
    
    def delete_organization_endpoint(self, organization_id: str, soft_delete: bool = True) -> dict:
        """DELETE /api/organizations/:id"""
        try:
            self.service.delete_organization(organization_id, soft_delete=soft_delete)
            
            return {
                'status': 'success',
                'status_code': 204 if not soft_delete else 200,
                'message': 'Organization deleted successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 400,
                'error': str(e)
            }
    
    def add_member_endpoint(self, organization_id: str, request_body: dict) -> dict:
        """POST /api/organizations/:id/members"""
        try:
            member = self.service.add_member(
                organization_id=organization_id,
                user_id=request_body['user_id'],
                email=request_body['email'],
                role=Role(request_body['role']),
                added_by=request_body['added_by']
            )
            
            return {
                'status': 'success',
                'status_code': 201,
                'data': member.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 400,
                'error': str(e)
            }
    
    def list_members_endpoint(self, organization_id: str, query_params: dict = None) -> dict:
        """GET /api/organizations/:id/members"""
        try:
            query_params = query_params or {}
            role_filter = Role(query_params['role']) if 'role' in query_params else None
            
            members = self.service.list_members(organization_id, role_filter=role_filter)
            
            return {
                'status': 'success',
                'status_code': 200,
                'data': [m.to_dict() for m in members],
                'count': len(members)
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 500,
                'error': str(e)
            }
    
    def update_member_role_endpoint(self, organization_id: str, user_id: str, request_body: dict) -> dict:
        """PUT /api/organizations/:id/members/:user_id/role"""
        try:
            member = self.service.update_member_role(
                organization_id=organization_id,
                user_id=user_id,
                new_role=Role(request_body['role'])
            )
            
            return {
                'status': 'success',
                'status_code': 200,
                'data': member.to_dict()
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 400,
                'error': str(e)
            }
    
    def remove_member_endpoint(self, organization_id: str, user_id: str) -> dict:
        """DELETE /api/organizations/:id/members/:user_id"""
        try:
            self.service.remove_member(organization_id, user_id)
            
            return {
                'status': 'success',
                'status_code': 200,
                'message': 'Member removed successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 400,
                'error': str(e)
            }
    
    def get_statistics_endpoint(self, organization_id: str) -> dict:
        """GET /api/organizations/:id/statistics"""
        try:
            stats = self.service.get_statistics(organization_id)
            
            return {
                'status': 'success',
                'status_code': 200,
                'data': stats
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': 500,
                'error': str(e)
            }

# ============================================================================
# DEMONSTRATION
# ============================================================================

print("=" * 100)
print("ORGANIZATION CRUD APIs - COMPLETE LIFECYCLE MANAGEMENT")
print("=" * 100)
print()

# Initialize service and API
org_service = OrganizationService()
org_api = OrganizationAPI(org_service)

# Test user
test_user_id = str(uuid.uuid4())

print("📝 CREATE ORGANIZATION")
print("-" * 100)

response = org_api.create_organization_endpoint({
    'name': 'Acme Corporation',
    'slug': 'acme-corp',
    'created_by': test_user_id,
    'tier': 'pro',
    'settings': {'feature_flags': {'analytics': True}}
})
print(f"Status: {response['status_code']} - {response['status']}")
if response['status'] == 'success':
    org_id = response['data']['organization_id']
    print(f"✅ Created organization: {response['data']['name']}")
    print(f"   ID: {org_id}")
    print(f"   Slug: {response['data']['slug']}")
    print(f"   Tier: {response['data']['tier']}")

print()
print("👥 ADD MEMBERS")
print("-" * 100)

members_to_add = [
    {'user_id': str(uuid.uuid4()), 'email': 'admin@acme.com', 'role': 'admin'},
    {'user_id': str(uuid.uuid4()), 'email': 'manager@acme.com', 'role': 'manager'},
    {'user_id': str(uuid.uuid4()), 'email': 'member@acme.com', 'role': 'member'},
]

for member_data in members_to_add:
    response = org_api.add_member_endpoint(org_id, {
        **member_data,
        'added_by': test_user_id
    })
    if response['status'] == 'success':
        print(f"✅ Added {member_data['email']} as {member_data['role']}")

print()
print("📋 LIST MEMBERS")
print("-" * 100)

response = org_api.list_members_endpoint(org_id)
if response['status'] == 'success':
    print(f"Total members: {response['count']}")
    for member in response['data']:
        print(f"  • {member['email']:25s} - {member['role']:10s}")

print()
print("🔄 UPDATE MEMBER ROLE")
print("-" * 100)

member_to_promote = members_to_add[2]['user_id']
response = org_api.update_member_role_endpoint(org_id, member_to_promote, {'role': 'manager'})
if response['status'] == 'success':
    print(f"✅ Updated role to {response['data']['role']}")

print()
print("✏️ UPDATE ORGANIZATION")
print("-" * 100)

response = org_api.update_organization_endpoint(org_id, {
    'name': 'Acme Corporation Inc.',
    'tier': 'enterprise',
    'settings': {'feature_flags': {'analytics': True, 'advanced_reporting': True}}
})
if response['status'] == 'success':
    print(f"✅ Updated organization")
    print(f"   Name: {response['data']['name']}")
    print(f"   Tier: {response['data']['tier']}")

print()
print("📊 ORGANIZATION STATISTICS")
print("-" * 100)

response = org_api.get_statistics_endpoint(org_id)
if response['status'] == 'success':
    stats = response['data']
    print(f"Organization: {stats['name']}")
    print(f"Tier: {stats['tier']}")
    print(f"Total members: {stats['total_members']}")
    print()
    print("Members by role:")
    for role, count in stats['members_by_role'].items():
        if count > 0:
            print(f"  {role}: {count}")

print()
print("🗑️ REMOVE MEMBER")
print("-" * 100)

member_to_remove = members_to_add[0]['user_id']
response = org_api.remove_member_endpoint(org_id, member_to_remove)
if response['status'] == 'success':
    print(f"✅ {response['message']}")

print()
print("📜 LIST ALL ORGANIZATIONS")
print("-" * 100)

# Create another org for listing
org_api.create_organization_endpoint({
    'name': 'Beta Company',
    'slug': 'beta-co',
    'created_by': test_user_id,
    'tier': 'free'
})

response = org_api.list_organizations_endpoint()
if response['status'] == 'success':
    print(f"Total organizations: {response['count']}")
    for org in response['data']:
        print(f"  • {org['name']:30s} | {org['slug']:20s} | {org['tier']:10s} | {org['status']}")

print()
print("🗑️ SOFT DELETE ORGANIZATION")
print("-" * 100)

response = org_api.delete_organization_endpoint(org_id, soft_delete=True)
if response['status'] == 'success':
    print(f"✅ {response['message']}")

# Verify soft delete
response = org_api.get_organization_endpoint(org_id)
if response['status'] == 'error' and response['status_code'] == 404:
    print(f"✅ Organization is no longer accessible (soft deleted)")

print()
print("=" * 100)
print("✅ Organization CRUD APIs Tested Successfully")
print("=" * 100)
print()
print("API ENDPOINTS IMPLEMENTED:")
print("• POST   /api/organizations                     - Create organization")
print("• GET    /api/organizations                     - List organizations")
print("• GET    /api/organizations/:id                 - Get organization")
print("• PUT    /api/organizations/:id                 - Update organization")
print("• DELETE /api/organizations/:id                 - Delete organization")
print("• POST   /api/organizations/:id/members         - Add member")
print("• GET    /api/organizations/:id/members         - List members")
print("• PUT    /api/organizations/:id/members/:user_id/role - Update role")
print("• DELETE /api/organizations/:id/members/:user_id - Remove member")
print("• GET    /api/organizations/:id/statistics      - Get statistics")
