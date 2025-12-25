"""
Project CRUD System with Soft Delete, Archiving, and Role-Based Access
Implements full project lifecycle with tenant isolation and hierarchical data access
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
from dataclasses import dataclass, field

# ============================================================================
# Enums for Project Management
# ============================================================================

class ProjectStatus(Enum):
    """Project status states"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"  # Soft delete

class ProjectVisibility(Enum):
    """Project visibility levels"""
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Project:
    """Project model with soft delete and archiving support"""
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    status: ProjectStatus
    visibility: ProjectVisibility
    owner_id: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'visibility': self.visibility.value,
            'owner_id': self.owner_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'metadata': self.metadata
        }

@dataclass
class ProjectMember:
    """Project member with role-based access"""
    id: str
    project_id: str
    user_id: str
    role: str  # From RBAC system
    added_by: str
    added_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat()
        }

# ============================================================================
# Project Service
# ============================================================================

class ProjectService:
    """Service layer for project management"""
    
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.members: Dict[str, List[ProjectMember]] = {}  # project_id -> members
    
    def create_project(
        self,
        organization_id: str,
        name: str,
        owner_id: str,
        created_by: str,
        description: Optional[str] = None,
        visibility: ProjectVisibility = ProjectVisibility.TEAM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Project:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        project = Project(
            id=project_id,
            organization_id=organization_id,
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
            visibility=visibility,
            owner_id=owner_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        self.projects[project_id] = project
        
        # Automatically add owner as member with owner role
        self.add_member(project_id, owner_id, "owner", created_by)
        
        return project
    
    def get_project(self, project_id: str, include_deleted: bool = False) -> Optional[Project]:
        """Get project by ID"""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # Filter deleted projects unless explicitly requested
        if not include_deleted and project.status == ProjectStatus.DELETED:
            return None
        
        return project
    
    def update_project(
        self,
        project_id: str,
        user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[ProjectVisibility] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Project]:
        """Update project details"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        if name:
            project.name = name
        if description is not None:
            project.description = description
        if visibility:
            project.visibility = visibility
        if metadata:
            project.metadata.update(metadata)
        
        project.updated_at = datetime.utcnow()
        return project
    
    def archive_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Archive a project (can be unarchived)"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        project.status = ProjectStatus.ARCHIVED
        project.archived_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        return project
    
    def unarchive_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Unarchive a project"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        if project.status == ProjectStatus.ARCHIVED:
            project.status = ProjectStatus.ACTIVE
            project.archived_at = None
            project.updated_at = datetime.utcnow()
        
        return project
    
    def soft_delete_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Soft delete a project (can be restored)"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        project.status = ProjectStatus.DELETED
        project.deleted_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        return project
    
    def restore_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Restore a soft-deleted project"""
        project = self.get_project(project_id, include_deleted=True)
        if not project or project.status != ProjectStatus.DELETED:
            return None
        
        project.status = ProjectStatus.ACTIVE
        project.deleted_at = None
        project.updated_at = datetime.utcnow()
        return project
    
    def hard_delete_project(self, project_id: str) -> bool:
        """Permanently delete a project"""
        if project_id in self.projects:
            del self.projects[project_id]
            if project_id in self.members:
                del self.members[project_id]
            return True
        return False
    
    def add_member(
        self,
        project_id: str,
        user_id: str,
        role: str,
        added_by: str
    ) -> Optional[ProjectMember]:
        """Add a member to a project"""
        project = self.get_project(project_id)
        if not project:
            return None
        
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=user_id,
            role=role,
            added_by=added_by,
            added_at=datetime.utcnow()
        )
        
        if project_id not in self.members:
            self.members[project_id] = []
        
        self.members[project_id].append(member)
        return member
    
    def remove_member(self, project_id: str, user_id: str) -> bool:
        """Remove a member from a project"""
        if project_id not in self.members:
            return False
        
        self.members[project_id] = [
            m for m in self.members[project_id] if m.user_id != user_id
        ]
        return True
    
    def get_project_members(self, project_id: str) -> List[ProjectMember]:
        """Get all members of a project"""
        return self.members.get(project_id, [])
    
    def is_project_member(self, project_id: str, user_id: str) -> bool:
        """Check if user is a project member"""
        project_members = self.members.get(project_id, [])
        return any(m.user_id == user_id for m in project_members)
    
    def get_user_projects(
        self,
        organization_id: str,
        user_id: str,
        include_archived: bool = False,
        include_deleted: bool = False
    ) -> List[Project]:
        """Get all projects for a user in an organization"""
        user_projects = []
        
        for project in self.projects.values():
            # Filter by organization
            if project.organization_id != organization_id:
                continue
            
            # Filter by status
            if not include_deleted and project.status == ProjectStatus.DELETED:
                continue
            if not include_archived and project.status == ProjectStatus.ARCHIVED:
                continue
            
            # Check if user has access based on visibility and membership
            if project.visibility == ProjectVisibility.ORGANIZATION:
                user_projects.append(project)
            elif project.visibility == ProjectVisibility.TEAM:
                if self.is_project_member(project.id, user_id):
                    user_projects.append(project)
            elif project.visibility == ProjectVisibility.PRIVATE:
                if project.owner_id == user_id:
                    user_projects.append(project)
        
        return user_projects
    
    def get_organization_projects(
        self,
        organization_id: str,
        include_archived: bool = False,
        include_deleted: bool = False
    ) -> List[Project]:
        """Get all projects for an organization (admin view)"""
        org_projects = []
        
        for project in self.projects.values():
            if project.organization_id != organization_id:
                continue
            
            if not include_deleted and project.status == ProjectStatus.DELETED:
                continue
            if not include_archived and project.status == ProjectStatus.ARCHIVED:
                continue
            
            org_projects.append(project)
        
        return org_projects
    
    def get_project_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get statistics for projects in an organization"""
        org_projects = [p for p in self.projects.values() if p.organization_id == organization_id]
        
        return {
            'total': len(org_projects),
            'active': sum(1 for p in org_projects if p.status == ProjectStatus.ACTIVE),
            'archived': sum(1 for p in org_projects if p.status == ProjectStatus.ARCHIVED),
            'deleted': sum(1 for p in org_projects if p.status == ProjectStatus.DELETED),
            'by_visibility': {
                'private': sum(1 for p in org_projects if p.visibility == ProjectVisibility.PRIVATE),
                'team': sum(1 for p in org_projects if p.visibility == ProjectVisibility.TEAM),
                'organization': sum(1 for p in org_projects if p.visibility == ProjectVisibility.ORGANIZATION)
            }
        }

# ============================================================================
# Initialize Service - Now exported to downstream blocks
# ============================================================================

# Create shared service instance
shared_project_service = ProjectService()

print("✅ Project CRUD System initialized")
print("\nFeatures:")
print("  • Create, read, update projects")
print("  • Soft delete with restore capability")
print("  • Archive/unarchive projects")
print("  • Role-based member management")
print("  • Tenant isolation (organization-scoped)")
print("  • Hierarchical access (private/team/org visibility)")
print("  • Project statistics and reporting")
print("\nExported: ProjectService, ProjectStatus, ProjectVisibility, Project, ProjectMember, shared_project_service")
