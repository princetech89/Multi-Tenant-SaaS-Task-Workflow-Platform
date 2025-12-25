"""
API Route-Level RBAC Guards
Decorator-based permission enforcement for API endpoints
"""
from typing import Dict, List, Optional, Callable, Any, Set
from functools import wraps
import json
from enum import Enum

# ============================================================================
# COPY RBAC DEFINITIONS (since we can't import between blocks)
# ============================================================================

class Role(str, Enum):
    """User roles in hierarchical order (highest to lowest privilege)"""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class Resource(str, Enum):
    """Resources in the system"""
    ORGANIZATION = "organization"
    USER = "user"
    PROJECT = "project"
    TASK = "task"
    SUBTASK = "subtask"
    COMMENT = "comment"
    ATTACHMENT = "attachment"
    ACTIVITY = "activity"
    NOTIFICATION = "notification"

class Action(str, Enum):
    """Actions that can be performed on resources"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ASSIGN = "assign"
    INVITE = "invite"
    REMOVE = "remove"
    MANAGE_ROLES = "manage_roles"
    MANAGE_BILLING = "manage_billing"
    EXPORT = "export"

ROLE_HIERARCHY = {
    Role.OWNER: [Role.OWNER, Role.ADMIN, Role.MANAGER, Role.MEMBER, Role.VIEWER],
    Role.ADMIN: [Role.ADMIN, Role.MANAGER, Role.MEMBER, Role.VIEWER],
    Role.MANAGER: [Role.MANAGER, Role.MEMBER, Role.VIEWER],
    Role.MEMBER: [Role.MEMBER, Role.VIEWER],
    Role.VIEWER: [Role.VIEWER]
}

PERMISSION_MATRIX: Dict[Role, Dict[Resource, Set[Action]]] = {
    Role.OWNER: {
        Resource.ORGANIZATION: {Action.READ, Action.UPDATE, Action.DELETE, Action.MANAGE_BILLING},
        Resource.USER: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.INVITE, Action.REMOVE, Action.MANAGE_ROLES},
        Resource.PROJECT: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN, Action.EXPORT},
        Resource.TASK: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN, Action.EXPORT},
        Resource.SUBTASK: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN},
        Resource.COMMENT: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE},
        Resource.ATTACHMENT: {Action.CREATE, Action.READ, Action.DELETE},
        Resource.ACTIVITY: {Action.READ, Action.EXPORT},
        Resource.NOTIFICATION: {Action.READ, Action.UPDATE, Action.DELETE},
    },
    Role.ADMIN: {
        Resource.ORGANIZATION: {Action.READ, Action.UPDATE},
        Resource.USER: {Action.CREATE, Action.READ, Action.UPDATE, Action.INVITE, Action.REMOVE, Action.MANAGE_ROLES},
        Resource.PROJECT: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN, Action.EXPORT},
        Resource.TASK: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN, Action.EXPORT},
        Resource.SUBTASK: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN},
        Resource.COMMENT: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE},
        Resource.ATTACHMENT: {Action.CREATE, Action.READ, Action.DELETE},
        Resource.ACTIVITY: {Action.READ, Action.EXPORT},
        Resource.NOTIFICATION: {Action.READ, Action.UPDATE, Action.DELETE},
    },
    Role.MANAGER: {
        Resource.ORGANIZATION: {Action.READ},
        Resource.USER: {Action.READ, Action.INVITE},
        Resource.PROJECT: {Action.CREATE, Action.READ, Action.UPDATE, Action.ASSIGN, Action.EXPORT},
        Resource.TASK: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN, Action.EXPORT},
        Resource.SUBTASK: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE, Action.ASSIGN},
        Resource.COMMENT: {Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE},
        Resource.ATTACHMENT: {Action.CREATE, Action.READ, Action.DELETE},
        Resource.ACTIVITY: {Action.READ},
        Resource.NOTIFICATION: {Action.READ, Action.UPDATE, Action.DELETE},
    },
    Role.MEMBER: {
        Resource.ORGANIZATION: {Action.READ},
        Resource.USER: {Action.READ},
        Resource.PROJECT: {Action.READ},
        Resource.TASK: {Action.CREATE, Action.READ, Action.UPDATE},
        Resource.SUBTASK: {Action.CREATE, Action.READ, Action.UPDATE},
        Resource.COMMENT: {Action.CREATE, Action.READ, Action.UPDATE},
        Resource.ATTACHMENT: {Action.CREATE, Action.READ},
        Resource.ACTIVITY: {Action.READ},
        Resource.NOTIFICATION: {Action.READ, Action.UPDATE, Action.DELETE},
    },
    Role.VIEWER: {
        Resource.ORGANIZATION: {Action.READ},
        Resource.USER: {Action.READ},
        Resource.PROJECT: {Action.READ},
        Resource.TASK: {Action.READ},
        Resource.SUBTASK: {Action.READ},
        Resource.COMMENT: {Action.READ},
        Resource.ATTACHMENT: {Action.READ},
        Resource.ACTIVITY: {Action.READ},
        Resource.NOTIFICATION: {Action.READ, Action.UPDATE},
    },
}

class PermissionChecker:
    """Checks if a user with a specific role has permission to perform an action"""
    
    def __init__(self, permission_matrix: Dict[Role, Dict[Resource, Set[Action]]]):
        self.permission_matrix = permission_matrix
    
    def has_permission(
        self,
        user_role: Role,
        resource: Resource,
        action: Action,
        resource_owner_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        role_permissions = self.permission_matrix.get(user_role, {})
        resource_actions = role_permissions.get(resource, set())
        has_basic_permission = action in resource_actions
        
        if action in {Action.UPDATE, Action.DELETE} and resource_owner_id and user_id:
            if resource_owner_id == user_id:
                return Action.READ in resource_actions
        
        return has_basic_permission
    
    def get_allowed_actions(self, user_role: Role, resource: Resource) -> Set[Action]:
        role_permissions = self.permission_matrix.get(user_role, {})
        return role_permissions.get(resource, set())
    
    def can_manage_user_role(self, actor_role: Role, target_role: Role) -> bool:
        actor_hierarchy = ROLE_HIERARCHY.get(actor_role, [])
        return target_role in actor_hierarchy and target_role != actor_role

permission_checker = PermissionChecker(PERMISSION_MATRIX)

# ============================================================================
# MOCK REQUEST/RESPONSE FOR DEMONSTRATION
# ============================================================================

class MockRequest:
    """Mock request object for demonstration"""
    def __init__(self, user_id: str, organization_id: str, role: str, headers: dict = None):
        self.user_id = user_id
        self.organization_id = organization_id
        self.role = role
        self.headers = headers or {}
        self.body = {}

class MockResponse:
    """Mock response object for demonstration"""
    def __init__(self, status_code: int, body: dict):
        self.status_code = status_code
        self.body = body

# ============================================================================
# PERMISSION DECORATORS
# ============================================================================

def require_permission(resource: Resource, action: Action):
    """
    Decorator to enforce permission checks on API routes.
    
    Usage:
        @require_permission(Resource.PROJECT, Action.CREATE)
        def create_project(request):
            # Only users with project:create permission can access
            return {"status": "success"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: MockRequest, *args, **kwargs) -> MockResponse:
            user_role = Role(request.role)
            
            has_perm = permission_checker.has_permission(
                user_role=user_role,
                resource=resource,
                action=action
            )
            
            if not has_perm:
                return MockResponse(
                    status_code=403,
                    body={
                        "error": "Forbidden",
                        "message": f"User with role '{user_role.value}' does not have permission to {action.value} {resource.value}",
                        "required_permission": f"{resource.value}:{action.value}"
                    }
                )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def require_role(min_role: Role):
    """
    Decorator to enforce minimum role requirements on API routes.
    
    Usage:
        @require_role(Role.ADMIN)
        def admin_dashboard(request):
            # Only admins and owners can access
            return {"status": "success"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: MockRequest, *args, **kwargs) -> MockResponse:
            user_role = Role(request.role)
            
            role_hierarchy = [Role.OWNER, Role.ADMIN, Role.MANAGER, Role.MEMBER, Role.VIEWER]
            
            if role_hierarchy.index(user_role) > role_hierarchy.index(min_role):
                return MockResponse(
                    status_code=403,
                    body={
                        "error": "Forbidden",
                        "message": f"This endpoint requires at least '{min_role.value}' role. Your role: '{user_role.value}'",
                        "required_role": min_role.value,
                        "your_role": user_role.value
                    }
                )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator

def require_ownership(resource: Resource):
    """
    Decorator to enforce ownership checks - user must own the resource.
    
    Usage:
        @require_ownership(Resource.TASK)
        def update_own_task(request, resource_owner_id):
            # Only the task creator can access
            return {"status": "success"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: MockRequest, resource_owner_id: str, *args, **kwargs) -> MockResponse:
            if request.user_id != resource_owner_id:
                return MockResponse(
                    status_code=403,
                    body={
                        "error": "Forbidden",
                        "message": f"You can only modify your own {resource.value}",
                        "resource": resource.value
                    }
                )
            
            return func(request, resource_owner_id, *args, **kwargs)
        
        return wrapper
    return decorator

def require_organization():
    """
    Decorator to enforce organization membership.
    All requests must include valid organization context.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(request: MockRequest, *args, **kwargs) -> MockResponse:
            if not request.organization_id:
                return MockResponse(
                    status_code=400,
                    body={
                        "error": "Bad Request",
                        "message": "Organization ID is required"
                    }
                )
            
            return func(request, *args, **kwargs)
        
        return wrapper
    return decorator

# ============================================================================
# EXAMPLE API ROUTE IMPLEMENTATIONS
# ============================================================================

# Organization Management Routes
@require_organization()
@require_permission(Resource.ORGANIZATION, Action.UPDATE)
def update_organization(request: MockRequest) -> MockResponse:
    """Update organization settings - requires organization:update permission"""
    return MockResponse(200, {
        "message": "Organization updated successfully",
        "organization_id": request.organization_id
    })

@require_organization()
@require_permission(Resource.ORGANIZATION, Action.DELETE)
def delete_organization(request: MockRequest) -> MockResponse:
    """Delete organization - only OWNER can do this"""
    return MockResponse(200, {
        "message": "Organization deleted successfully",
        "organization_id": request.organization_id
    })

# User Management Routes
@require_organization()
@require_permission(Resource.USER, Action.INVITE)
def invite_user(request: MockRequest) -> MockResponse:
    """Invite user to organization - requires user:invite permission"""
    return MockResponse(200, {
        "message": "User invited successfully",
        "invited_by": request.user_id
    })

@require_organization()
@require_permission(Resource.USER, Action.MANAGE_ROLES)
def change_user_role(request: MockRequest) -> MockResponse:
    """Change user role - requires user:manage_roles permission"""
    return MockResponse(200, {
        "message": "User role updated successfully"
    })

# Project Management Routes
@require_organization()
@require_permission(Resource.PROJECT, Action.CREATE)
def create_project(request: MockRequest) -> MockResponse:
    """Create new project - requires project:create permission"""
    return MockResponse(201, {
        "message": "Project created successfully",
        "created_by": request.user_id
    })

@require_organization()
@require_permission(Resource.PROJECT, Action.DELETE)
def delete_project(request: MockRequest) -> MockResponse:
    """Delete project - requires project:delete permission"""
    return MockResponse(200, {
        "message": "Project deleted successfully"
    })

# Task Management Routes
@require_organization()
@require_permission(Resource.TASK, Action.CREATE)
def create_task(request: MockRequest) -> MockResponse:
    """Create new task - requires task:create permission"""
    return MockResponse(201, {
        "message": "Task created successfully",
        "created_by": request.user_id
    })

@require_organization()
@require_permission(Resource.TASK, Action.ASSIGN)
def assign_task(request: MockRequest) -> MockResponse:
    """Assign task to user - requires task:assign permission"""
    return MockResponse(200, {
        "message": "Task assigned successfully"
    })

@require_organization()
@require_permission(Resource.TASK, Action.DELETE)
def delete_task(request: MockRequest) -> MockResponse:
    """Delete task - requires task:delete permission"""
    return MockResponse(200, {
        "message": "Task deleted successfully"
    })

# Read-only routes
@require_organization()
@require_permission(Resource.PROJECT, Action.READ)
def get_projects(request: MockRequest) -> MockResponse:
    """Get all projects - requires project:read permission"""
    return MockResponse(200, {
        "message": "Projects retrieved successfully",
        "role": request.role
    })

@require_organization()
@require_permission(Resource.TASK, Action.READ)
def get_tasks(request: MockRequest) -> MockResponse:
    """Get all tasks - requires task:read permission"""
    return MockResponse(200, {
        "message": "Tasks retrieved successfully",
        "role": request.role
    })

# ============================================================================
# ROUTE REGISTRY
# ============================================================================

route_registry = {
    # Organization routes
    "PUT /api/organizations/:id": update_organization,
    "DELETE /api/organizations/:id": delete_organization,
    
    # User routes
    "POST /api/users/invite": invite_user,
    "PUT /api/users/:id/role": change_user_role,
    
    # Project routes
    "POST /api/projects": create_project,
    "DELETE /api/projects/:id": delete_project,
    "GET /api/projects": get_projects,
    
    # Task routes
    "POST /api/tasks": create_task,
    "PUT /api/tasks/:id/assign": assign_task,
    "DELETE /api/tasks/:id": delete_task,
    "GET /api/tasks": get_tasks,
}

# ============================================================================
# TEST API ROUTES WITH DIFFERENT ROLES
# ============================================================================

print("=" * 100)
print("API ROUTE-LEVEL RBAC GUARDS - TESTING")
print("=" * 100)
print()

# Test users with different roles
test_users = [
    MockRequest("user-1", "org-123", "owner"),
    MockRequest("user-2", "org-123", "admin"),
    MockRequest("user-3", "org-123", "manager"),
    MockRequest("user-4", "org-123", "member"),
    MockRequest("user-5", "org-123", "viewer"),
]

# Test scenarios
test_scenarios = [
    ("DELETE /api/organizations/:id", "delete_organization", [True, False, False, False, False]),
    ("POST /api/users/invite", "invite_user", [True, True, True, False, False]),
    ("PUT /api/users/:id/role", "change_user_role", [True, True, False, False, False]),
    ("POST /api/projects", "create_project", [True, True, True, False, False]),
    ("DELETE /api/projects/:id", "delete_project", [True, True, False, False, False]),
    ("POST /api/tasks", "create_task", [True, True, True, True, False]),
    ("DELETE /api/tasks/:id", "delete_task", [True, True, True, False, False]),
    ("GET /api/projects", "get_projects", [True, True, True, True, True]),
    ("GET /api/tasks", "get_tasks", [True, True, True, True, True]),
]

for route_path, route_name, expected_results in test_scenarios:
    print(f"\n{'='*100}")
    print(f"ROUTE: {route_path}")
    print('='*100)
    
    route_func = route_registry.get(route_path)
    if route_func:
        for i, user in enumerate(test_users):
            response = route_func(user)
            is_success = response.status_code < 400
            expected = expected_results[i]
            status = "✅" if is_success == expected else "❌"
            
            result_icon = "✓" if is_success else "✗"
            print(f"{status} {user.role:10s} → {result_icon} {response.status_code} (expected: {'success' if expected else 'denied'})")

print("\n" + "=" * 100)
print("✅ API Route Guards Implemented Successfully")
print("=" * 100)
print()
print("INTEGRATION NOTES:")
print("- Use @require_permission(resource, action) for specific permission checks")
print("- Use @require_role(min_role) for minimum role requirements")
print("- Use @require_ownership(resource) for ownership-based access")
print("- Use @require_organization() to enforce organization context")
print("- All decorators return 403 Forbidden with detailed error messages")
print("- Guards are composable - stack multiple decorators as needed")
