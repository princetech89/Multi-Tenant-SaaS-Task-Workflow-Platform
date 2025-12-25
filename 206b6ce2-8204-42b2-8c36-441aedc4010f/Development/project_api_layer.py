"""
Project API Layer with RBAC Integration
Implements REST API endpoints with role-based access control and tenant isolation
"""

from typing import Dict, List, Optional, Any

# ============================================================================
# Project API with RBAC and Tenant Isolation
# ============================================================================

class ProjectAPI:
    """API layer for project management with RBAC integration"""
    
    def __init__(self, service):
        self.service = service
    
    # ========================================================================
    # CREATE Operations
    # ========================================================================
    
    def create_project(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new project
        Required: organization_id, name, owner_id, created_by
        Optional: description, visibility, metadata
        """
        # Extract request data
        organization_id = request.get('organization_id')
        user_id = request.get('user_id')  # From JWT token
        
        # Tenant isolation: user must belong to organization
        if not self._validate_organization_access(user_id, organization_id):
            return {
                'success': False,
                'error': 'Access denied: user not in organization',
                'code': 403
            }
        
        # Get visibility enum from string
        visibility_str = request.get('visibility', 'team')
        visibility = getattr(ProjectVisibility, visibility_str.upper(), ProjectVisibility.TEAM)
        
        # Create project
        project = self.service.create_project(
            organization_id=organization_id,
            name=request['name'],
            owner_id=request.get('owner_id', user_id),
            created_by=user_id,
            description=request.get('description'),
            visibility=visibility,
            metadata=request.get('metadata')
        )
        
        return {
            'success': True,
            'project': project.to_dict(),
            'code': 201
        }
    
    # ========================================================================
    # READ Operations
    # ========================================================================
    
    def get_project(
        self,
        project_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Get project by ID with access control
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        # Check access based on visibility
        if not self._check_project_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: insufficient permissions',
                'code': 403
            }
        
        return {
            'success': True,
            'project': project.to_dict(),
            'code': 200
        }
    
    def list_user_projects(
        self,
        user_id: str,
        organization_id: str,
        include_archived: bool = False
    ) -> Dict[str, Any]:
        """
        List all projects accessible to a user
        """
        projects = self.service.get_user_projects(
            organization_id=organization_id,
            user_id=user_id,
            include_archived=include_archived,
            include_deleted=False
        )
        
        return {
            'success': True,
            'projects': [p.to_dict() for p in projects],
            'count': len(projects),
            'code': 200
        }
    
    def list_organization_projects(
        self,
        organization_id: str,
        user_id: str,
        user_role: str,
        include_archived: bool = False
    ) -> Dict[str, Any]:
        """
        List all projects in organization (admin/owner only)
        """
        # Only admins and owners can view all org projects
        if user_role not in ['owner', 'admin']:
            return {
                'success': False,
                'error': 'Access denied: requires admin or owner role',
                'code': 403
            }
        
        projects = self.service.get_organization_projects(
            organization_id=organization_id,
            include_archived=include_archived,
            include_deleted=False
        )
        
        return {
            'success': True,
            'projects': [p.to_dict() for p in projects],
            'count': len(projects),
            'code': 200
        }
    
    # ========================================================================
    # UPDATE Operations
    # ========================================================================
    
    def update_project(
        self,
        project_id: str,
        user_id: str,
        organization_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update project details
        Requires: project member with appropriate role
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        # Check if user can update (owner or admin)
        if not self._check_project_update_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner or admin role',
                'code': 403
            }
        
        # Convert visibility string to enum if provided
        visibility = None
        if 'visibility' in updates and updates['visibility']:
            visibility = getattr(ProjectVisibility, updates['visibility'].upper(), None)
        
        # Update project
        updated_project = self.service.update_project(
            project_id=project_id,
            user_id=user_id,
            name=updates.get('name'),
            description=updates.get('description'),
            visibility=visibility,
            metadata=updates.get('metadata')
        )
        
        return {
            'success': True,
            'project': updated_project.to_dict(),
            'code': 200
        }
    
    # ========================================================================
    # ARCHIVE Operations
    # ========================================================================
    
    def archive_project(
        self,
        project_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Archive a project (can be unarchived)
        Requires: project owner or organization admin
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        # Check permissions
        if not self._check_project_delete_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner role',
                'code': 403
            }
        
        archived_project = self.service.archive_project(project_id, user_id)
        
        return {
            'success': True,
            'project': archived_project.to_dict(),
            'message': 'Project archived successfully',
            'code': 200
        }
    
    def unarchive_project(
        self,
        project_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Unarchive a project
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation and permission checks
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        if not self._check_project_delete_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner role',
                'code': 403
            }
        
        unarchived_project = self.service.unarchive_project(project_id, user_id)
        
        return {
            'success': True,
            'project': unarchived_project.to_dict(),
            'message': 'Project unarchived successfully',
            'code': 200
        }
    
    # ========================================================================
    # DELETE Operations (Soft Delete)
    # ========================================================================
    
    def delete_project(
        self,
        project_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Soft delete a project (can be restored)
        Requires: project owner or organization admin
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        # Check permissions
        if not self._check_project_delete_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner role',
                'code': 403
            }
        
        deleted_project = self.service.soft_delete_project(project_id, user_id)
        
        return {
            'success': True,
            'project': deleted_project.to_dict(),
            'message': 'Project deleted successfully (can be restored)',
            'code': 200
        }
    
    def restore_project(
        self,
        project_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        Restore a soft-deleted project
        """
        project = self.service.get_project(project_id, include_deleted=True)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation and permission checks
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        if not self._check_project_delete_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner role',
                'code': 403
            }
        
        restored_project = self.service.restore_project(project_id, user_id)
        
        if not restored_project:
            return {
                'success': False,
                'error': 'Project cannot be restored',
                'code': 400
            }
        
        return {
            'success': True,
            'project': restored_project.to_dict(),
            'message': 'Project restored successfully',
            'code': 200
        }
    
    # ========================================================================
    # MEMBER Management
    # ========================================================================
    
    def add_project_member(
        self,
        project_id: str,
        user_id: str,
        organization_id: str,
        new_member_id: str,
        role: str
    ) -> Dict[str, Any]:
        """
        Add a member to a project
        Requires: project owner or admin
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        # Check permissions
        if not self._check_project_update_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner or admin role',
                'code': 403
            }
        
        # Add member
        member = self.service.add_member(project_id, new_member_id, role, user_id)
        
        return {
            'success': True,
            'member': member.to_dict(),
            'code': 201
        }
    
    def remove_project_member(
        self,
        project_id: str,
        user_id: str,
        organization_id: str,
        member_id: str
    ) -> Dict[str, Any]:
        """
        Remove a member from a project
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation and permission checks
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        if not self._check_project_update_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: requires owner or admin role',
                'code': 403
            }
        
        # Cannot remove project owner
        if member_id == project.owner_id:
            return {
                'success': False,
                'error': 'Cannot remove project owner',
                'code': 400
            }
        
        success = self.service.remove_member(project_id, member_id)
        
        return {
            'success': success,
            'message': 'Member removed successfully' if success else 'Member not found',
            'code': 200 if success else 404
        }
    
    def list_project_members(
        self,
        project_id: str,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """
        List all members of a project
        """
        project = self.service.get_project(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found',
                'code': 404
            }
        
        # Tenant isolation
        if project.organization_id != organization_id:
            return {
                'success': False,
                'error': 'Access denied: cross-organization access',
                'code': 403
            }
        
        # Check access
        if not self._check_project_access(project, user_id):
            return {
                'success': False,
                'error': 'Access denied: not a project member',
                'code': 403
            }
        
        members = self.service.get_project_members(project_id)
        
        return {
            'success': True,
            'members': [m.to_dict() for m in members],
            'count': len(members),
            'code': 200
        }
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    def get_project_statistics(
        self,
        organization_id: str,
        user_id: str,
        user_role: str
    ) -> Dict[str, Any]:
        """
        Get project statistics for organization
        """
        # Only admins and owners can view stats
        if user_role not in ['owner', 'admin']:
            return {
                'success': False,
                'error': 'Access denied: requires admin or owner role',
                'code': 403
            }
        
        stats = self.service.get_project_stats(organization_id)
        
        return {
            'success': True,
            'statistics': stats,
            'code': 200
        }
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _validate_organization_access(self, user_id: str, organization_id: str) -> bool:
        """Validate user has access to organization"""
        # In production, check against organization membership
        # For now, assume valid if both provided
        return user_id and organization_id
    
    def _check_project_access(self, project, user_id: str) -> bool:
        """Check if user can access project based on visibility"""
        # Organization-wide visibility
        if project.visibility.value == 'organization':
            return True
        
        # Team visibility - must be member
        if project.visibility.value == 'team':
            return self.service.is_project_member(project.id, user_id)
        
        # Private visibility - must be owner
        if project.visibility.value == 'private':
            return project.owner_id == user_id
        
        return False
    
    def _check_project_update_access(self, project, user_id: str) -> bool:
        """Check if user can update project"""
        # Owner can always update
        if project.owner_id == user_id:
            return True
        
        # Check if user is admin member
        members = self.service.get_project_members(project.id)
        for member in members:
            if member.user_id == user_id and member.role in ['admin', 'owner']:
                return True
        
        return False
    
    def _check_project_delete_access(self, project, user_id: str) -> bool:
        """Check if user can delete/archive project"""
        # Only owner can delete/archive
        return project.owner_id == user_id

# ============================================================================
# Initialize API with service from upstream
# ============================================================================

project_api_instance = ProjectAPI(shared_project_service)

print("✅ Project API Layer initialized")
print("\nAPI Endpoints:")
print("  CREATE:")
print("    • POST /projects - Create project")
print("    • POST /projects/{id}/members - Add member")
print("\n  READ:")
print("    • GET /projects/{id} - Get project")
print("    • GET /projects/user - List user's projects")
print("    • GET /projects/organization - List org projects (admin)")
print("    • GET /projects/{id}/members - List members")
print("    • GET /projects/statistics - Get stats (admin)")
print("\n  UPDATE:")
print("    • PUT /projects/{id} - Update project")
print("\n  ARCHIVE:")
print("    • POST /projects/{id}/archive - Archive project")
print("    • POST /projects/{id}/unarchive - Unarchive project")
print("\n  DELETE:")
print("    • DELETE /projects/{id} - Soft delete project")
print("    • POST /projects/{id}/restore - Restore deleted project")
print("    • DELETE /projects/{id}/members/{member_id} - Remove member")
