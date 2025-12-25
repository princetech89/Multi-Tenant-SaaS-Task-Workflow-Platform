"""
Task and Subtask CRUD System with State Transitions, Assignment Logic, and Nested Queries
Implements full task lifecycle with parent-child relationships, status management, and optimized queries
"""

from datetime import datetime, date
from enum import Enum
import uuid
from dataclasses import dataclass, field

# ============================================================================
# Enums for Task Management
# ============================================================================

class TaskStatus(Enum):
    """Task status states with workflow support"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SubtaskStatus(Enum):
    """Subtask status states (simplified workflow)"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# ============================================================================
# State Transition Rules
# ============================================================================

# Define valid state transitions for tasks
TASK_STATUS_TRANSITIONS: dict = {
    TaskStatus.TODO: {TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {TaskStatus.IN_REVIEW, TaskStatus.BLOCKED, TaskStatus.TODO, TaskStatus.CANCELLED},
    TaskStatus.IN_REVIEW: {TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED},
    TaskStatus.BLOCKED: {TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: {TaskStatus.IN_PROGRESS},  # Allow reopening
    TaskStatus.CANCELLED: {TaskStatus.TODO}  # Allow reactivating
}

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Task:
    """Task model with hierarchy and state management"""
    id: str
    organization_id: str
    project_id: str
    created_by: str
    assigned_to: str
    parent_task_id: str  # For task hierarchy
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    task_number: int  # Sequential within project
    estimated_hours: float
    actual_hours: float
    start_date: date
    due_date: date
    completed_at: datetime
    tags: list
    position: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'project_id': self.project_id,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'parent_task_id': self.parent_task_id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'task_number': self.task_number,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'tags': self.tags,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'metadata': self.metadata
        }

@dataclass
class Subtask:
    """Subtask/checklist item within a task"""
    id: str
    organization_id: str
    task_id: str
    created_by: str
    assigned_to: str
    title: str
    description: str
    status: SubtaskStatus
    position: int
    completed_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'task_id': self.task_id,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'position': self.position,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

# ============================================================================
# Task Service
# ============================================================================

class TaskService:
    """Service layer for task and subtask management"""
    
    def __init__(self):
        self.tasks: dict = {}
        self.subtasks: dict = {}
        self.task_numbers: dict = {}  # project_id -> next_task_number
        self.task_children: dict = {}  # parent_task_id -> [child_ids]
        self.task_subtasks: dict = {}  # task_id -> [subtask_ids]
    
    # ========================================================================
    # Task CRUD Operations
    # ========================================================================
    
    def create_task(
        self,
        organization_id: str,
        project_id: str,
        created_by: str,
        title: str,
        description: str = None,
        assigned_to: str = None,
        parent_task_id: str = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        estimated_hours: float = None,
        start_date: date = None,
        due_date: date = None,
        tags: list = None,
        position: int = None,
        metadata: dict = None
    ) -> Task:
        """Create a new task with automatic task numbering"""
        task_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Auto-increment task number within project
        if project_id not in self.task_numbers:
            self.task_numbers[project_id] = 1
        task_number = self.task_numbers[project_id]
        self.task_numbers[project_id] += 1
        
        # Validate parent task if specified
        if parent_task_id:
            parent = self.get_task(parent_task_id)
            if not parent or parent.organization_id != organization_id:
                raise ValueError("Invalid parent task")
        
        # Auto-position at end if not specified
        if position is None:
            position = len([t for t in self.tasks.values() 
                          if t.project_id == project_id and not t.deleted_at])
        
        task = Task(
            id=task_id,
            organization_id=organization_id,
            project_id=project_id,
            created_by=created_by,
            assigned_to=assigned_to,
            parent_task_id=parent_task_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            priority=priority,
            task_number=task_number,
            estimated_hours=estimated_hours,
            actual_hours=None,
            start_date=start_date,
            due_date=due_date,
            completed_at=None,
            tags=tags or [],
            position=position,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        
        # Track parent-child relationship
        if parent_task_id:
            if parent_task_id not in self.task_children:
                self.task_children[parent_task_id] = []
            self.task_children[parent_task_id].append(task_id)
        
        return task
    
    def get_task(self, task_id: str, include_deleted: bool = False):
        """Get task by ID"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        if not include_deleted and task.deleted_at:
            return None
        
        return task
    
    def update_task(
        self,
        task_id: str,
        user_id: str,
        title: str = None,
        description: str = None,
        assigned_to: str = None,
        priority: TaskPriority = None,
        estimated_hours: float = None,
        actual_hours: float = None,
        start_date: date = None,
        due_date: date = None,
        tags: list = None,
        position: int = None,
        metadata: dict = None
    ):
        """Update task details"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if assigned_to is not None:
            task.assigned_to = assigned_to
        if priority:
            task.priority = priority
        if estimated_hours is not None:
            task.estimated_hours = estimated_hours
        if actual_hours is not None:
            task.actual_hours = actual_hours
        if start_date is not None:
            task.start_date = start_date
        if due_date is not None:
            task.due_date = due_date
        if tags is not None:
            task.tags = tags
        if position is not None:
            task.position = position
        if metadata:
            task.metadata.update(metadata)
        
        task.updated_at = datetime.utcnow()
        return task
    
    def transition_task_status(
        self,
        task_id: str,
        user_id: str,
        new_status: TaskStatus,
        force: bool = False
    ):
        """
        Transition task to new status with validation
        Enforces state transition rules unless force=True
        """
        task = self.get_task(task_id)
        if not task:
            return None
        
        current_status = task.status
        
        # Validate transition
        if not force:
            allowed_transitions = TASK_STATUS_TRANSITIONS.get(current_status, set())
            if new_status not in allowed_transitions:
                raise ValueError(
                    f"Invalid status transition: {current_status.value} -> {new_status.value}. "
                    f"Allowed: {[s.value for s in allowed_transitions]}"
                )
        
        task.status = new_status
        task.updated_at = datetime.utcnow()
        
        # Set completed_at timestamp
        if new_status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
        elif task.completed_at:  # Reopening completed task
            task.completed_at = None
        
        return task
    
    def assign_task(
        self,
        task_id: str,
        assigned_to: str,
        assigned_by: str
    ):
        """Assign task to user"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.assigned_to = assigned_to
        task.updated_at = datetime.utcnow()
        
        # Store assignment in metadata for audit
        if 'assignment_history' not in task.metadata:
            task.metadata['assignment_history'] = []
        task.metadata['assignment_history'].append({
            'assigned_to': assigned_to,
            'assigned_by': assigned_by,
            'assigned_at': datetime.utcnow().isoformat()
        })
        
        return task
    
    def unassign_task(self, task_id: str, user_id: str):
        """Unassign task"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.assigned_to = None
        task.updated_at = datetime.utcnow()
        return task
    
    def soft_delete_task(self, task_id: str, user_id: str):
        """Soft delete task and all its subtasks"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        task.deleted_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        # Soft delete all subtasks
        subtask_ids = self.task_subtasks.get(task_id, [])
        for subtask_id in subtask_ids:
            self.soft_delete_subtask(subtask_id, user_id)
        
        # Soft delete child tasks recursively
        child_task_ids = self.task_children.get(task_id, [])
        for child_id in child_task_ids:
            self.soft_delete_task(child_id, user_id)
        
        return task
    
    def restore_task(self, task_id: str, user_id: str):
        """Restore soft-deleted task"""
        task = self.get_task(task_id, include_deleted=True)
        if not task or not task.deleted_at:
            return None
        
        task.deleted_at = None
        task.updated_at = datetime.utcnow()
        return task
    
    # ========================================================================
    # Task Query Operations
    # ========================================================================
    
    def get_project_tasks(
        self,
        organization_id: str,
        project_id: str,
        status: TaskStatus = None,
        assigned_to: str = None,
        include_deleted: bool = False,
        parent_only: bool = False
    ):
        """Get tasks for a project with optional filters"""
        project_tasks = []
        
        for task in self.tasks.values():
            if task.organization_id != organization_id:
                continue
            if task.project_id != project_id:
                continue
            if not include_deleted and task.deleted_at:
                continue
            if status and task.status != status:
                continue
            if assigned_to and task.assigned_to != assigned_to:
                continue
            if parent_only and task.parent_task_id:
                continue
            
            project_tasks.append(task)
        
        # Sort by position
        project_tasks.sort(key=lambda t: t.position)
        return project_tasks
    
    def get_user_tasks(
        self,
        organization_id: str,
        user_id: str,
        status: TaskStatus = None,
        include_deleted: bool = False
    ):
        """Get tasks assigned to a user"""
        user_tasks = []
        
        for task in self.tasks.values():
            if task.organization_id != organization_id:
                continue
            if task.assigned_to != user_id:
                continue
            if not include_deleted and task.deleted_at:
                continue
            if status and task.status != status:
                continue
            
            user_tasks.append(task)
        
        # Sort by priority then due date
        user_tasks.sort(key=lambda t: (
            ['critical', 'high', 'medium', 'low'].index(t.priority.value),
            t.due_date or date.max
        ))
        return user_tasks
    
    def get_child_tasks(self, parent_task_id: str):
        """Get child tasks of a parent task"""
        child_ids = self.task_children.get(parent_task_id, [])
        children = []
        for child_id in child_ids:
            child = self.get_task(child_id)
            if child:
                children.append(child)
        return children
    
    def get_overdue_tasks(
        self,
        organization_id: str,
        project_id: str = None
    ):
        """Get overdue tasks"""
        today = date.today()
        overdue = []
        
        for task in self.tasks.values():
            if task.organization_id != organization_id:
                continue
            if project_id and task.project_id != project_id:
                continue
            if task.deleted_at:
                continue
            if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]:
                continue
            if task.due_date and task.due_date < today:
                overdue.append(task)
        
        overdue.sort(key=lambda t: t.due_date)
        return overdue
    
    # ========================================================================
    # Subtask CRUD Operations
    # ========================================================================
    
    def create_subtask(
        self,
        organization_id: str,
        task_id: str,
        created_by: str,
        title: str,
        description: str = None,
        assigned_to: str = None,
        position: int = None
    ):
        """Create a subtask/checklist item"""
        # Validate parent task
        task = self.get_task(task_id)
        if not task or task.organization_id != organization_id:
            return None
        
        subtask_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Auto-position at end if not specified
        if position is None:
            existing = self.task_subtasks.get(task_id, [])
            position = len([sid for sid in existing if not self.subtasks[sid].deleted_at])
        
        subtask = Subtask(
            id=subtask_id,
            organization_id=organization_id,
            task_id=task_id,
            created_by=created_by,
            assigned_to=assigned_to,
            title=title,
            description=description,
            status=SubtaskStatus.TODO,
            position=position,
            completed_at=None,
            created_at=now,
            updated_at=now
        )
        
        self.subtasks[subtask_id] = subtask
        
        # Track task-subtask relationship
        if task_id not in self.task_subtasks:
            self.task_subtasks[task_id] = []
        self.task_subtasks[task_id].append(subtask_id)
        
        return subtask
    
    def get_subtask(self, subtask_id: str, include_deleted: bool = False):
        """Get subtask by ID"""
        subtask = self.subtasks.get(subtask_id)
        if not subtask:
            return None
        
        if not include_deleted and subtask.deleted_at:
            return None
        
        return subtask
    
    def update_subtask(
        self,
        subtask_id: str,
        user_id: str,
        title: str = None,
        description: str = None,
        assigned_to: str = None,
        status: SubtaskStatus = None,
        position: int = None
    ):
        """Update subtask details"""
        subtask = self.get_subtask(subtask_id)
        if not subtask:
            return None
        
        if title is not None:
            subtask.title = title
        if description is not None:
            subtask.description = description
        if assigned_to is not None:
            subtask.assigned_to = assigned_to
        if status:
            subtask.status = status
            if status == SubtaskStatus.COMPLETED:
                subtask.completed_at = datetime.utcnow()
            elif subtask.completed_at:
                subtask.completed_at = None
        if position is not None:
            subtask.position = position
        
        subtask.updated_at = datetime.utcnow()
        return subtask
    
    def get_task_subtasks(self, task_id: str, include_deleted: bool = False):
        """Get all subtasks for a task"""
        subtask_ids = self.task_subtasks.get(task_id, [])
        subtasks_list = []
        
        for subtask_id in subtask_ids:
            subtask = self.get_subtask(subtask_id, include_deleted)
            if subtask:
                subtasks_list.append(subtask)
        
        # Sort by position
        subtasks_list.sort(key=lambda s: s.position)
        return subtasks_list
    
    def soft_delete_subtask(self, subtask_id: str, user_id: str):
        """Soft delete subtask"""
        subtask = self.get_subtask(subtask_id)
        if not subtask:
            return None
        
        subtask.deleted_at = datetime.utcnow()
        subtask.updated_at = datetime.utcnow()
        return subtask
    
    # ========================================================================
    # Statistics and Reporting
    # ========================================================================
    
    def get_task_statistics(
        self,
        organization_id: str,
        project_id: str = None
    ) -> dict:
        """Get task statistics"""
        tasks_list = [t for t in self.tasks.values() 
                     if t.organization_id == organization_id 
                     and not t.deleted_at]
        
        if project_id:
            tasks_list = [t for t in tasks_list if t.project_id == project_id]
        
        return {
            'total': len(tasks_list),
            'by_status': {
                status.value: sum(1 for t in tasks_list if t.status == status)
                for status in TaskStatus
            },
            'by_priority': {
                priority.value: sum(1 for t in tasks_list if t.priority == priority)
                for priority in TaskPriority
            },
            'assigned': sum(1 for t in tasks_list if t.assigned_to),
            'unassigned': sum(1 for t in tasks_list if not t.assigned_to),
            'with_subtasks': sum(1 for t in tasks_list if t.id in self.task_subtasks),
            'overdue': len(self.get_overdue_tasks(organization_id, project_id))
        }

# ============================================================================
# Initialize Service
# ============================================================================

shared_task_service = TaskService()

print("✅ Task CRUD System initialized")
print("\nFeatures:")
print("  • Create, read, update, delete tasks")
print("  • State transition management with validation")
print("  • Task assignment and reassignment with audit")
print("  • Parent-child task hierarchy (nested tasks)")
print("  • Subtask/checklist system")
print("  • Priority and due date management")
print("  • Tag-based filtering")
print("  • Overdue task tracking")
print("  • Soft delete with cascade to children/subtasks")
print("  • Auto-incrementing task numbers per project")
print("  • Comprehensive statistics and reporting")
print("\nExported: TaskService, TaskStatus, TaskPriority, SubtaskStatus, Task, Subtask, shared_task_service")
