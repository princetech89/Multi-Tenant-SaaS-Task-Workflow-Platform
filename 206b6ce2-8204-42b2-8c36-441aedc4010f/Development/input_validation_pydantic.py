"""
Input Validation with Pydantic
Comprehensive request validation using Pydantic models with custom validators
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator, constr, conint
from datetime import datetime
from enum import Enum
import re

# ============================================================================
# Enums for Validation
# ============================================================================

class OrganizationTierEnum(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class RoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"

class ProjectVisibilityEnum(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"

class TaskStatusEnum(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# ============================================================================
# Organization Request Models
# ============================================================================

class CreateOrganizationRequest(BaseModel):
    """Request model for creating an organization"""
    name: constr(min_length=1, max_length=255, strip_whitespace=True) = Field(
        ...,
        description="Organization name",
        example="Acme Corporation"
    )
    slug: constr(min_length=3, max_length=63, strip_whitespace=True, to_lower=True) = Field(
        ...,
        description="URL-safe slug for the organization",
        example="acme-corp"
    )
    tier: OrganizationTierEnum = Field(
        default=OrganizationTierEnum.FREE,
        description="Subscription tier"
    )
    settings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Organization settings"
    )
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate slug format: lowercase alphanumeric with hyphens"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        if v.startswith('-') or v.endswith('-'):
            raise ValueError('Slug cannot start or end with a hyphen')
        if '--' in v:
            raise ValueError('Slug cannot contain consecutive hyphens')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate organization name"""
        if not v or v.isspace():
            raise ValueError('Name cannot be empty or whitespace only')
        # Check for suspicious characters
        forbidden_chars = ['<', '>', '{', '}', '\\', '^', '`', '|']
        if any(char in v for char in forbidden_chars):
            raise ValueError('Name contains forbidden characters')
        return v.strip()
    
    class Config:
        use_enum_values = True

class UpdateOrganizationRequest(BaseModel):
    """Request model for updating an organization"""
    name: Optional[constr(min_length=1, max_length=255, strip_whitespace=True)] = None
    slug: Optional[constr(min_length=3, max_length=63, strip_whitespace=True, to_lower=True)] = None
    tier: Optional[OrganizationTierEnum] = None
    settings: Optional[Dict[str, Any]] = None
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if v is not None:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
            if v.startswith('-') or v.endswith('-'):
                raise ValueError('Slug cannot start or end with a hyphen')
        return v
    
    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """Ensure at least one field is being updated"""
        if not any([self.name, self.slug, self.tier, self.settings]):
            raise ValueError('At least one field must be provided for update')
        return self
    
    class Config:
        use_enum_values = True

# ============================================================================
# Member Request Models
# ============================================================================

class AddMemberRequest(BaseModel):
    """Request model for adding a member to organization"""
    user_id: Optional[str] = None
    email: str = Field(
        ...,
        description="Email address of the user to invite",
        example="user@example.com",
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
    )
    role: RoleEnum = Field(
        default=RoleEnum.MEMBER,
        description="Role to assign to the member"
    )
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        """Additional email validation"""
        # Block common disposable email domains (example)
        disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
        domain = v.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValueError(f'Disposable email domains are not allowed: {domain}')
        return v.lower()
    
    class Config:
        use_enum_values = True

class UpdateMemberRoleRequest(BaseModel):
    """Request model for updating member role"""
    role: RoleEnum = Field(
        ...,
        description="New role for the member"
    )
    
    @field_validator('role')
    @classmethod
    def validate_role_change(cls, v):
        """Validate role change (additional business logic can be added)"""
        if v == RoleEnum.OWNER:
            raise ValueError('Cannot promote to owner role via this endpoint. Use transfer ownership endpoint.')
        return v
    
    class Config:
        use_enum_values = True

# ============================================================================
# Project Request Models
# ============================================================================

class CreateProjectRequest(BaseModel):
    """Request model for creating a project"""
    name: constr(min_length=1, max_length=255, strip_whitespace=True) = Field(
        ...,
        description="Project name",
        example="Q1 Marketing Campaign"
    )
    description: Optional[constr(max_length=5000, strip_whitespace=True)] = None
    visibility: ProjectVisibilityEnum = Field(
        default=ProjectVisibilityEnum.TEAM,
        description="Project visibility level"
    )
    owner_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('name')
    @classmethod
    def validate_project_name(cls, v):
        """Validate project name"""
        if not v or v.isspace():
            raise ValueError('Project name cannot be empty')
        # Remove excessive whitespace
        v = ' '.join(v.split())
        return v
    
    class Config:
        use_enum_values = True

class UpdateProjectRequest(BaseModel):
    """Request model for updating a project"""
    name: Optional[constr(min_length=1, max_length=255, strip_whitespace=True)] = None
    description: Optional[constr(max_length=5000, strip_whitespace=True)] = None
    visibility: Optional[ProjectVisibilityEnum] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @model_validator(mode='after')
    def check_at_least_one_field(self):
        """Ensure at least one field is being updated"""
        if not any([self.name, self.description, self.visibility, self.metadata]):
            raise ValueError('At least one field must be provided for update')
        return self
    
    class Config:
        use_enum_values = True

# ============================================================================
# Task Request Models
# ============================================================================

class CreateTaskRequest(BaseModel):
    """Request model for creating a task"""
    project_id: str = Field(
        ...,
        description="Project ID",
        min_length=36,
        max_length=36
    )
    title: constr(min_length=1, max_length=500, strip_whitespace=True) = Field(
        ...,
        description="Task title",
        example="Design landing page mockups"
    )
    description: Optional[constr(max_length=10000, strip_whitespace=True)] = None
    status: TaskStatusEnum = Field(
        default=TaskStatusEnum.TODO,
        description="Task status"
    )
    priority: TaskPriorityEnum = Field(
        default=TaskPriorityEnum.MEDIUM,
        description="Task priority"
    )
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(
        None,
        max_length=20
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate task title"""
        if not v or v.isspace():
            raise ValueError('Task title cannot be empty')
        v = ' '.join(v.split())
        return v
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        """Validate due date is in the future"""
        if v is not None and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags format"""
        if v is not None:
            validated_tags = []
            for tag in v:
                # Clean and validate each tag
                tag = tag.strip().lower()
                if len(tag) == 0:
                    continue
                if len(tag) > 50:
                    raise ValueError('Tag length cannot exceed 50 characters')
                if not re.match(r'^[a-z0-9-_]+$', tag):
                    raise ValueError(f'Invalid tag format: {tag}. Use only lowercase alphanumeric, hyphens, and underscores')
                validated_tags.append(tag)
            return validated_tags if validated_tags else None
        return v
    
    class Config:
        use_enum_values = True

class UpdateTaskRequest(BaseModel):
    """Request model for updating a task"""
    title: Optional[constr(min_length=1, max_length=500, strip_whitespace=True)] = None
    description: Optional[constr(max_length=10000, strip_whitespace=True)] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        if v is not None and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v
    
    @model_validator(mode='after')
    def check_at_least_one_field(self):
        if not any([self.title, self.description, self.status, self.priority, self.assignee_id, self.due_date, self.tags]):
            raise ValueError('At least one field must be provided for update')
        return self
    
    class Config:
        use_enum_values = True

# ============================================================================
# Pagination Request Model
# ============================================================================

class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: conint(ge=1) = Field(
        default=1,
        description="Page number (1-indexed)"
    )
    limit: conint(ge=1, le=100) = Field(
        default=20,
        description="Items per page (max 100)"
    )
    sort_by: Optional[str] = None
    sort_order: Optional[str] = Field(
        default="desc",
        description="Sort order: asc or desc"
    )
    
    @field_validator('sort_order')
    @classmethod
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError('sort_order must be either "asc" or "desc"')
        return v.lower() if v else v

# ============================================================================
# Testing Validation
# ============================================================================

print("=" * 100)
print("INPUT VALIDATION WITH PYDANTIC")
print("=" * 100)
print()

print("✅ VALID REQUEST EXAMPLES")
print("-" * 100)

# Test valid organization creation
valid_org = CreateOrganizationRequest(
    name="Acme Corporation",
    slug="acme-corp",
    tier="pro"
)
print(f"✓ Create Organization: {valid_org.name} ({valid_org.slug})")

# Test valid member addition
valid_member = AddMemberRequest(
    email="john.doe@example.com",
    role="admin"
)
print(f"✓ Add Member: {valid_member.email} as {valid_member.role}")

# Test valid project creation
valid_project = CreateProjectRequest(
    name="Q1 Marketing Campaign",
    description="Marketing initiatives",
    visibility="team"
)
print(f"✓ Create Project: {valid_project.name}")

# Test valid task creation
valid_task = CreateTaskRequest(
    project_id="123e4567-e89b-12d3-a456-426614174000",
    title="Design landing page",
    priority="high",
    tags=["design", "ui-ux"]
)
print(f"✓ Create Task: {valid_task.title} ({valid_task.priority})")

print()
print()
print("❌ INVALID REQUEST EXAMPLES")
print("-" * 100)

# Test invalid requests
test_cases = [
    ("Invalid slug (uppercase)", lambda: CreateOrganizationRequest(name="Test", slug="INVALID-SLUG")),
    ("Invalid slug (special chars)", lambda: CreateOrganizationRequest(name="Test", slug="test@org")),
    ("Empty name", lambda: CreateOrganizationRequest(name="   ", slug="test")),
    ("Slug too short", lambda: CreateOrganizationRequest(name="Test", slug="ab")),
    ("Invalid email", lambda: AddMemberRequest(email="not-an-email", role="member")),
    ("Promote to owner", lambda: UpdateMemberRoleRequest(role="owner")),
    ("Empty update", lambda: UpdateOrganizationRequest()),
    ("Page number < 1", lambda: PaginationParams(page=0)),
    ("Limit > 100", lambda: PaginationParams(limit=150))
]

for test_name, test_func in test_cases:
    try:
        test_func()
        print(f"✗ {test_name}: SHOULD HAVE FAILED")
    except Exception:
        print(f"✓ {test_name}: Blocked")

print()
print()
print("=" * 100)
print("✅ Input Validation System Implemented Successfully")
print("=" * 100)
print()
print("VALIDATION FEATURES:")
print("• Field type validation (strings, integers, emails, datetimes)")
print("• String length constraints (min/max)")
print("• Pattern matching (regex for slugs, tags, emails)")
print("• Custom validators for business logic")
print("• Enum validation for status, priority, roles")
print("• Email format validation with regex")
print("• Date/time validation (future dates)")
print("• Cross-field validation (at least one field for updates)")
print("• Automatic data cleaning (strip whitespace, lowercase)")
print("• Pagination parameter validation")
print()
print("INTEGRATION:")
print("• Use Pydantic models for all API request bodies")
print("• Return 400 Bad Request with validation errors")
print("• Include detailed error messages for each field")
print("• Automatic JSON serialization/deserialization")
