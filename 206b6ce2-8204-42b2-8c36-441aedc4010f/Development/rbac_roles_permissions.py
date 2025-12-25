"""
Role-Based Access Control (RBAC) System
Defines roles, permissions matrix, and permission checking logic
"""
from typing import Dict, List, Set, Optional
from enum import Enum

# ============================================================================
# ROLE DEFINITIONS
# ============================================================================

class Role(str, Enum):
    """User roles in hierarchical order (highest to lowest privilege)"""
    OWNER = "owner"           # Full control, can delete org, manage billing
    ADMIN = "admin"           # Full operational control, cannot delete org
    MANAGER = "manager"       # Can manage projects and team members
    MEMBER = "member"         # Can work on assigned tasks and projects
    VIEWER = "viewer"         # Read-only access

# Role hierarchy - higher roles inherit lower role permissions
ROLE_HIERARCHY = {
    Role.OWNER: [Role.OWNER, Role.ADMIN, Role.MANAGER, Role.MEMBER, Role.VIEWER],
    Role.ADMIN: [Role.ADMIN, Role.MANAGER, Role.MEMBER, Role.VIEWER],
    Role.MANAGER: [Role.MANAGER, Role.MEMBER, Role.VIEWER],
    Role.MEMBER: [Role.MEMBER, Role.VIEWER],
    Role.VIEWER: [Role.VIEWER]
}

# ============================================================================
# RESOURCE AND ACTION DEFINITIONS
# ============================================================================

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

# ============================================================================
# PERMISSION MATRIX
# Defines which roles can perform which actions on which resources
# ============================================================================

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

# ============================================================================
# PERMISSION CHECKER
# ============================================================================

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
        """
        Check if a user has permission to perform an action on a resource.
        
        Args:
            user_role: The role of the user attempting the action
            resource: The resource being accessed
            action: The action being performed
            resource_owner_id: Optional - ID of the resource owner (for ownership checks)
            user_id: Optional - ID of the current user (for ownership checks)
            
        Returns:
            True if permission is granted, False otherwise
        """
        # Get permissions for this role
        role_permissions = self.permission_matrix.get(user_role, {})
        resource_actions = role_permissions.get(resource, set())
        
        # Check if action is allowed for this role and resource
        has_basic_permission = action in resource_actions
        
        # Special case: users can always update/delete their own content
        if action in {Action.UPDATE, Action.DELETE} and resource_owner_id and user_id:
            if resource_owner_id == user_id:
                # Check if user has at least read permission
                return Action.READ in resource_actions
        
        return has_basic_permission
    
    def get_allowed_actions(self, user_role: Role, resource: Resource) -> Set[Action]:
        """Get all actions a role can perform on a resource"""
        role_permissions = self.permission_matrix.get(user_role, {})
        return role_permissions.get(resource, set())
    
    def can_manage_user_role(self, actor_role: Role, target_role: Role) -> bool:
        """
        Check if an actor can manage (assign/change) a target role.
        Rule: You can only manage roles that are lower in hierarchy than yours.
        """
        actor_hierarchy = ROLE_HIERARCHY.get(actor_role, [])
        # Can manage if target role is in actor's hierarchy but not equal to actor's role
        return target_role in actor_hierarchy and target_role != actor_role

# ============================================================================
# INSTANTIATE PERMISSION CHECKER
# ============================================================================

permission_checker = PermissionChecker(PERMISSION_MATRIX)

# ============================================================================
# DISPLAY PERMISSION MATRIX
# ============================================================================

print("=" * 100)
print("RBAC PERMISSION MATRIX")
print("=" * 100)
print()

for role in Role:
    print(f"\n{'='*100}")
    print(f"ROLE: {role.value.upper()}")
    print('='*100)
    
    if role in PERMISSION_MATRIX:
        permissions = PERMISSION_MATRIX[role]
        for resource in Resource:
            if resource in permissions:
                actions = permissions[resource]
                actions_str = ", ".join(sorted([a.value for a in actions]))
                print(f"  {resource.value:20s} → {actions_str}")
    print()

# ============================================================================
# PERMISSION CHECKER EXAMPLES
# ============================================================================

print("\n" + "=" * 100)
print("PERMISSION CHECKER EXAMPLES")
print("=" * 100)

test_cases = [
    (Role.OWNER, Resource.ORGANIZATION, Action.DELETE, True),
    (Role.ADMIN, Resource.ORGANIZATION, Action.DELETE, False),
    (Role.MANAGER, Resource.PROJECT, Action.CREATE, True),
    (Role.MEMBER, Resource.TASK, Action.DELETE, False),
    (Role.MEMBER, Resource.TASK, Action.UPDATE, True),
    (Role.VIEWER, Resource.TASK, Action.UPDATE, False),
    (Role.VIEWER, Resource.PROJECT, Action.READ, True),
    (Role.ADMIN, Resource.USER, Action.MANAGE_ROLES, True),
    (Role.MANAGER, Resource.USER, Action.MANAGE_ROLES, False),
    (Role.OWNER, Resource.ORGANIZATION, Action.MANAGE_BILLING, True),
]

print()
for role, resource, action, expected in test_cases:
    result = permission_checker.has_permission(role, resource, action)
    status = "✅" if result == expected else "❌"
    print(f"{status} {role.value:10s} can {'✓' if result else '✗'} {action.value:15s} on {resource.value:15s} (expected: {expected})")

# ============================================================================
# ROLE HIERARCHY TESTS
# ============================================================================

print("\n" + "=" * 100)
print("ROLE MANAGEMENT HIERARCHY")
print("=" * 100)
print()

role_management_tests = [
    (Role.OWNER, Role.ADMIN, True),
    (Role.OWNER, Role.OWNER, False),
    (Role.ADMIN, Role.MANAGER, True),
    (Role.ADMIN, Role.OWNER, False),
    (Role.MANAGER, Role.MEMBER, True),
    (Role.MEMBER, Role.MANAGER, False),
]

for actor, target, expected in role_management_tests:
    result = permission_checker.can_manage_user_role(actor, target)
    status = "✅" if result == expected else "❌"
    print(f"{status} {actor.value:10s} can {'✓' if result else '✗'} manage {target.value:10s} role (expected: {expected})")

print("\n" + "=" * 100)
print("✅ RBAC System Initialized Successfully")
print("=" * 100)
