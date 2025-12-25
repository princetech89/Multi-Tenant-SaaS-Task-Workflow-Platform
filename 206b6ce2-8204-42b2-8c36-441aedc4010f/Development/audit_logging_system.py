"""
Event-Driven Activity Logging System with Immutable Audit Records
Complete implementation with pagination, filtering, real-time feed generation
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from collections import defaultdict

# ============================================================================
# AUDIT LOG MODELS - Event-Driven Architecture
# ============================================================================

class EntityType(str, Enum):
    """Entity types that can be audited"""
    ORGANIZATION = "organization"
    MEMBER = "member"
    INVITATION = "invitation"
    ROLE = "role"
    SETTINGS = "settings"
    PROJECT = "project"
    TASK = "task"

class ActionType(str, Enum):
    """Types of actions that can be logged"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    INVITE = "invite"
    ACCEPT = "accept"
    REVOKE = "revoke"
    ASSIGN = "assign"
    REMOVE = "remove"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    EXPORT = "export"
    ARCHIVE = "archive"
    RESTORE = "restore"

class AuditLog:
    """Immutable audit log entry - event-driven design"""
    
    def __init__(
        self,
        log_id: str,
        organization_id: str,
        user_id: str,
        entity_type: EntityType,
        entity_id: str,
        action: ActionType,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        timestamp: datetime = None
    ):
        # Immutable properties - set once at creation
        self._log_id = log_id
        self._organization_id = organization_id
        self._user_id = user_id
        self._entity_type = entity_type
        self._entity_id = entity_id
        self._action = action
        self._old_values = old_values or {}
        self._new_values = new_values or {}
        self._metadata = metadata or {}
        self._ip_address = ip_address
        self._user_agent = user_agent
        self._timestamp = timestamp or datetime.utcnow()
    
    # Read-only properties
    @property
    def log_id(self) -> str:
        return self._log_id
    
    @property
    def organization_id(self) -> str:
        return self._organization_id
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def entity_type(self) -> EntityType:
        return self._entity_type
    
    @property
    def entity_id(self) -> str:
        return self._entity_id
    
    @property
    def action(self) -> ActionType:
        return self._action
    
    @property
    def old_values(self) -> Dict:
        return self._old_values.copy()
    
    @property
    def new_values(self) -> Dict:
        return self._new_values.copy()
    
    @property
    def metadata(self) -> Dict:
        return self._metadata.copy()
    
    @property
    def ip_address(self) -> Optional[str]:
        return self._ip_address
    
    @property
    def user_agent(self) -> Optional[str]:
        return self._user_agent
    
    @property
    def timestamp(self) -> datetime:
        return self._timestamp
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'log_id': self.log_id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'entity_type': self.entity_type.value,
            'entity_id': self.entity_id,
            'action': self.action.value,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'metadata': self.metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat()
        }
    
    def get_changes(self) -> Dict[str, tuple]:
        """Get dictionary of changes (old_value, new_value)"""
        changes = {}
        all_keys = set(self._old_values.keys()) | set(self._new_values.keys())
        
        for key in all_keys:
            old_val = self._old_values.get(key)
            new_val = self._new_values.get(key)
            if old_val != new_val:
                changes[key] = (old_val, new_val)
        
        return changes
    
    def format_summary(self) -> str:
        """Format a human-readable summary"""
        changes = self.get_changes()
        change_summary = ", ".join([f"{k}: {v[0]} → {v[1]}" for k, v in changes.items()])
        
        return (
            f"{self.action.value.upper()} {self.entity_type.value} "
            f"(ID: {self.entity_id[:8]}...) "
            f"by user {self.user_id[:8]}... "
            f"at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} "
            f"| Changes: {change_summary if change_summary else 'N/A'}"
        )

# ============================================================================
# PAGINATION SUPPORT
# ============================================================================

class PaginationResult:
    """Paginated result set"""
    
    def __init__(
        self,
        items: List[AuditLog],
        page: int,
        page_size: int,
        total_items: int,
        has_next: bool,
        has_prev: bool
    ):
        self.items = items
        self.page = page
        self.page_size = page_size
        self.total_items = total_items
        self.total_pages = (total_items + page_size - 1) // page_size
        self.has_next = has_next
        self.has_prev = has_prev
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'items': [item.to_dict() for item in self.items],
            'page': self.page,
            'page_size': self.page_size,
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_prev': self.has_prev
        }

# ============================================================================
# ACTIVITY FEED - Real-Time Updates
# ============================================================================

class ActivityFeedItem:
    """Activity feed item for real-time display"""
    
    def __init__(self, audit_log: AuditLog, user_name: str = None, user_avatar: str = None):
        self.log = audit_log
        self.user_name = user_name or f"User {audit_log.user_id[:8]}"
        self.user_avatar = user_avatar
    
    def to_feed_format(self) -> dict:
        """Format for activity feed display"""
        return {
            'id': self.log.log_id,
            'timestamp': self.log.timestamp.isoformat(),
            'user': {
                'id': self.log.user_id,
                'name': self.user_name,
                'avatar': self.user_avatar
            },
            'action': self.log.action.value,
            'entity_type': self.log.entity_type.value,
            'entity_id': self.log.entity_id,
            'summary': self._generate_summary(),
            'changes': self.log.get_changes(),
            'metadata': self.log.metadata
        }
    
    def _generate_summary(self) -> str:
        """Generate human-readable summary"""
        action = self.log.action.value
        entity = self.log.entity_type.value
        
        if action == 'create':
            return f"{self.user_name} created a new {entity}"
        elif action == 'update':
            changes = self.log.get_changes()
            if changes:
                change_list = [k for k in changes.keys()]
                return f"{self.user_name} updated {entity} ({', '.join(change_list[:2])})"
            return f"{self.user_name} updated {entity}"
        elif action == 'delete':
            return f"{self.user_name} deleted {entity}"
        elif action == 'invite':
            email = self.log.new_values.get('email', 'someone')
            return f"{self.user_name} invited {email}"
        elif action == 'assign':
            return f"{self.user_name} assigned {entity}"
        else:
            return f"{self.user_name} {action}d {entity}"

# ============================================================================
# ENHANCED AUDIT SERVICE - Event-Driven with Pagination
# ============================================================================

class AuditService:
    """Service for managing audit logs with event-driven architecture"""
    
    def __init__(self):
        # Immutable audit log storage
        self.logs: Dict[str, AuditLog] = {}
        
        # Indexes for efficient querying
        self.org_logs: Dict[str, List[str]] = defaultdict(list)
        self.user_logs: Dict[str, List[str]] = defaultdict(list)
        self.entity_logs: Dict[str, List[str]] = defaultdict(list)
        self.project_logs: Dict[str, List[str]] = defaultdict(list)
        self.task_logs: Dict[str, List[str]] = defaultdict(list)
        
        # Event subscribers for real-time updates
        self.subscribers: List[callable] = []
    
    def subscribe(self, callback: callable):
        """Subscribe to audit log events"""
        self.subscribers.append(callback)
    
    def _notify_subscribers(self, log: AuditLog):
        """Notify subscribers of new audit log"""
        for callback in self.subscribers:
            try:
                callback(log)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def log_action(
        self,
        organization_id: str,
        user_id: str,
        entity_type: EntityType,
        entity_id: str,
        action: ActionType,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> AuditLog:
        """
        Log an action to the immutable audit trail
        
        Returns:
            Created audit log entry (immutable)
        """
        log_id = str(uuid.uuid4())
        
        # Create immutable audit log
        audit_log = AuditLog(
            log_id=log_id,
            organization_id=organization_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Store log (immutable)
        self.logs[log_id] = audit_log
        
        # Index by organization
        self.org_logs[organization_id].append(log_id)
        
        # Index by user
        self.user_logs[user_id].append(log_id)
        
        # Index by entity
        entity_key = f"{entity_type.value}:{entity_id}"
        self.entity_logs[entity_key].append(log_id)
        
        # Index by project
        if project_id:
            self.project_logs[project_id].append(log_id)
        
        # Index by task
        if task_id:
            self.task_logs[task_id].append(log_id)
        
        # Notify subscribers (event-driven)
        self._notify_subscribers(audit_log)
        
        return audit_log
    
    def get_organization_logs_paginated(
        self,
        organization_id: str,
        page: int = 1,
        page_size: int = 50,
        entity_type: Optional[EntityType] = None,
        action: Optional[ActionType] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        task_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> PaginationResult:
        """Get paginated audit logs with comprehensive filtering"""
        
        # Start with organization logs
        log_ids = self.org_logs.get(organization_id, [])
        logs = [self.logs[lid] for lid in log_ids]
        
        # Apply filters
        if entity_type:
            logs = [log for log in logs if log.entity_type == entity_type]
        
        if action:
            logs = [log for log in logs if log.action == action]
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if project_id:
            project_log_ids = set(self.project_logs.get(project_id, []))
            logs = [log for log in logs if log.log_id in project_log_ids]
        
        if task_id:
            task_log_ids = set(self.task_logs.get(task_id, []))
            logs = [log for log in logs if log.log_id in task_log_ids]
        
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]
        
        # Sort by timestamp descending
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        
        # Pagination
        total_items = len(logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_logs = logs[start_idx:end_idx]
        
        return PaginationResult(
            items=paginated_logs,
            page=page,
            page_size=page_size,
            total_items=total_items,
            has_next=end_idx < total_items,
            has_prev=page > 1
        )
    
    def get_project_activity_feed(
        self,
        project_id: str,
        page: int = 1,
        page_size: int = 20,
        user_names: Optional[Dict[str, str]] = None
    ) -> PaginationResult:
        """Get activity feed for a specific project"""
        log_ids = self.project_logs.get(project_id, [])
        logs = [self.logs[lid] for lid in log_ids]
        
        # Sort by timestamp descending
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        
        # Pagination
        total_items = len(logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_logs = logs[start_idx:end_idx]
        
        return PaginationResult(
            items=paginated_logs,
            page=page,
            page_size=page_size,
            total_items=total_items,
            has_next=end_idx < total_items,
            has_prev=page > 1
        )
    
    def get_task_activity_feed(
        self,
        task_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> PaginationResult:
        """Get activity feed for a specific task"""
        log_ids = self.task_logs.get(task_id, [])
        logs = [self.logs[lid] for lid in log_ids]
        
        # Sort by timestamp descending
        logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        
        # Pagination
        total_items = len(logs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_logs = logs[start_idx:end_idx]
        
        return PaginationResult(
            items=paginated_logs,
            page=page,
            page_size=page_size,
            total_items=total_items,
            has_next=end_idx < total_items,
            has_prev=page > 1
        )
    
    def generate_activity_feed(
        self,
        logs: List[AuditLog],
        user_names: Optional[Dict[str, str]] = None
    ) -> List[dict]:
        """Generate activity feed from audit logs"""
        user_names = user_names or {}
        feed_items = []
        
        for log in logs:
            user_name = user_names.get(log.user_id, f"User {log.user_id[:8]}")
            feed_item = ActivityFeedItem(log, user_name=user_name)
            feed_items.append(feed_item.to_feed_format())
        
        return feed_items
    
    def get_statistics(
        self,
        organization_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get audit statistics for an organization"""
        result = self.get_organization_logs_paginated(
            organization_id,
            page=1,
            page_size=100000,
            start_date=start_date,
            end_date=end_date
        )
        logs = result.items
        
        # Count by action type
        actions_by_type = defaultdict(int)
        for log in logs:
            actions_by_type[log.action.value] += 1
        
        # Count by entity type
        actions_by_entity = defaultdict(int)
        for log in logs:
            actions_by_entity[log.entity_type.value] += 1
        
        # Count by user
        actions_by_user = defaultdict(int)
        for log in logs:
            actions_by_user[log.user_id] += 1
        
        # Get most active users
        most_active_users = sorted(
            actions_by_user.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'organization_id': organization_id,
            'total_logs': len(logs),
            'date_range': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'actions_by_type': dict(actions_by_type),
            'actions_by_entity': dict(actions_by_entity),
            'total_users_active': len(actions_by_user),
            'most_active_users': [
                {'user_id': user_id, 'action_count': count}
                for user_id, count in most_active_users
            ]
        }
    
    def export_logs(
        self,
        organization_id: str,
        format: str = 'json',
        filters: Optional[dict] = None
    ) -> str:
        """Export audit logs in specified format"""
        filters = filters or {}
        result = self.get_organization_logs_paginated(
            organization_id,
            page=1,
            page_size=100000,
            **filters
        )
        logs = result.items
        
        if format == 'json':
            return json.dumps([log.to_dict() for log in logs], indent=2)
        elif format == 'csv':
            lines = ['log_id,timestamp,user_id,entity_type,entity_id,action,ip_address']
            for log in logs:
                lines.append(
                    f"{log.log_id},{log.timestamp.isoformat()},{log.user_id},"
                    f"{log.entity_type.value},{log.entity_id},{log.action.value},"
                    f"{log.ip_address or 'N/A'}"
                )
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported format: {format}")

# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def log_project_create(
    audit_service: AuditService,
    org_id: str,
    user_id: str,
    project_id: str,
    project_data: dict
):
    """Helper to log project creation"""
    return audit_service.log_action(
        organization_id=org_id,
        user_id=user_id,
        entity_type=EntityType.PROJECT,
        entity_id=project_id,
        action=ActionType.CREATE,
        new_values=project_data,
        project_id=project_id
    )

def log_task_create(
    audit_service: AuditService,
    org_id: str,
    user_id: str,
    task_id: str,
    project_id: str,
    task_data: dict
):
    """Helper to log task creation"""
    return audit_service.log_action(
        organization_id=org_id,
        user_id=user_id,
        entity_type=EntityType.TASK,
        entity_id=task_id,
        action=ActionType.CREATE,
        new_values=task_data,
        project_id=project_id,
        task_id=task_id
    )

# ============================================================================
# DEMONSTRATION - Event-Driven Activity Logging
# ============================================================================

print("=" * 100)
print("EVENT-DRIVEN ACTIVITY LOGGING WITH IMMUTABLE AUDIT RECORDS")
print("=" * 100)
print()

# Initialize audit service
event_audit_svc = AuditService()

# Event subscriber for real-time notifications
def audit_event_subscriber(log: AuditLog):
    print(f"  🔔 EVENT: {log.action.value} on {log.entity_type.value} by {log.user_id[:8]}...")

event_audit_svc.subscribe(audit_event_subscriber)

# Test data
org_id = str(uuid.uuid4())
user1_id = str(uuid.uuid4())
user2_id = str(uuid.uuid4())
project1_id = str(uuid.uuid4())
project2_id = str(uuid.uuid4())

print("🎯 EVENT-DRIVEN LOGGING - Project & Task Activities")
print("-" * 100)

# Log project creation
log_project_create(
    event_audit_svc, org_id, user1_id, project1_id,
    {'name': 'Website Redesign', 'status': 'active'}
)

# Log multiple task activities
for i in range(15):
    task_id = str(uuid.uuid4())
    log_task_create(
        event_audit_svc, org_id, user1_id if i % 2 == 0 else user2_id,
        task_id, project1_id,
        {'title': f'Task {i+1}', 'status': 'todo', 'priority': 'medium'}
    )

# Log another project
log_project_create(
    event_audit_svc, org_id, user2_id, project2_id,
    {'name': 'Mobile App', 'status': 'planning'}
)

print()
print("📄 PAGINATION - Organization Activity Feed")
print("-" * 100)

# Get first page
page1 = event_audit_svc.get_organization_logs_paginated(
    org_id, page=1, page_size=5
)
print(f"Page 1 of {page1.total_pages} (Total: {page1.total_items} logs)")
print(f"Has next: {page1.has_next}, Has prev: {page1.has_prev}")
print()
for log in page1.items:
    print(f"  • {log.format_summary()}")

print()

# Get second page
page2 = event_audit_svc.get_organization_logs_paginated(
    org_id, page=2, page_size=5
)
print(f"Page 2 of {page2.total_pages}")
print(f"Has next: {page2.has_next}, Has prev: {page2.has_prev}")
print()
for log in page2.items:
    print(f"  • {log.format_summary()}")

print()
print("🔍 FILTERING - Project-Specific Activity")
print("-" * 100)

project1_feed = event_audit_svc.get_project_activity_feed(
    project1_id, page=1, page_size=10
)
print(f"Project 1 Activity: {project1_feed.total_items} total logs")
print(f"Showing page {project1_feed.page} of {project1_feed.total_pages}")
print()
for log in project1_feed.items[:5]:
    print(f"  • {log.format_summary()}")

print()
print("📊 REAL-TIME ACTIVITY FEED GENERATION")
print("-" * 100)

user_names = {user1_id: "Alice", user2_id: "Bob"}
feed_items = event_audit_svc.generate_activity_feed(
    project1_feed.items[:5], user_names
)

for item in feed_items:
    print(f"  {item['user']['name']}: {item['summary']}")
    print(f"    → {item['timestamp']}")
    print()

print()
print("🎯 FILTERING BY ENTITY TYPE")
print("-" * 100)

task_logs = event_audit_svc.get_organization_logs_paginated(
    org_id,
    page=1,
    page_size=5,
    entity_type=EntityType.TASK
)
print(f"Task activities: {task_logs.total_items} total")
for log in task_logs.items:
    print(f"  • {log.format_summary()}")

print()
print("🎯 FILTERING BY ACTION TYPE")
print("-" * 100)

create_logs = event_audit_svc.get_organization_logs_paginated(
    org_id,
    page=1,
    page_size=5,
    action=ActionType.CREATE
)
print(f"Create actions: {create_logs.total_items} total")

print()
print("📈 AUDIT STATISTICS")
print("-" * 100)

stats = event_audit_svc.get_statistics(org_id)
print(f"Total audit logs: {stats['total_logs']}")
print(f"Total active users: {stats['total_users_active']}")
print()
print("Actions by type:")
for action_type, count in stats['actions_by_type'].items():
    print(f"  {action_type}: {count}")
print()
print("Actions by entity:")
for entity_type, count in stats['actions_by_entity'].items():
    print(f"  {entity_type}: {count}")

print()
print("=" * 100)
print("✅ Event-Driven Activity Logging Implemented Successfully")
print("=" * 100)
print()
print("KEY FEATURES:")
print("✓ Immutable audit records - properties are read-only after creation")
print("✓ Event-driven architecture with subscriber pattern")
print("✓ Comprehensive pagination support for efficient querying")
print("✓ Multi-dimensional filtering (project, task, user, entity, action, date)")
print("✓ Real-time activity feed generation")
print("✓ Project-specific and task-specific activity tracking")
print("✓ Complete audit trail with timestamp ordering")
print("✓ Export capabilities (JSON, CSV)")
print("✓ Statistics and analytics")
