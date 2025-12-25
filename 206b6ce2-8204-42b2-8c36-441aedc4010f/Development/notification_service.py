"""
Notification Service with Event Listeners
Decoupled notification system for task assignments, status changes, and due dates
with user-specific delivery channels
"""

from typing import List, Optional, Any, Callable
from datetime import datetime, date, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid

# ============================================================================
# Notification Enums
# ============================================================================

class NotificationType(Enum):
    """Types of notifications"""
    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    TASK_COMMENTED = "task_commented"
    TASK_UPDATED = "task_updated"
    SUBTASK_COMPLETED = "subtask_completed"
    MENTION = "mention"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(Enum):
    """Delivery channels for notifications"""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEBHOOK = "webhook"

class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

# ============================================================================
# Event System
# ============================================================================

class EventType(Enum):
    """Workflow events that trigger notifications"""
    TASK_CREATED = "task_created"
    TASK_ASSIGNED = "task_assigned"
    TASK_UNASSIGNED = "task_unassigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_COMMENTED = "task_commented"
    SUBTASK_CREATED = "subtask_created"
    SUBTASK_COMPLETED = "subtask_completed"
    DUE_DATE_APPROACHING = "due_date_approaching"
    DUE_DATE_PASSED = "due_date_passed"

@dataclass
class WorkflowEvent:
    """Event object passed to listeners"""
    event_type: EventType
    organization_id: str
    user_id: str  # User who triggered the event
    entity_type: str  # "task", "subtask", "project"
    entity_id: str
    timestamp: datetime
    data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

# ============================================================================
# Notification Models
# ============================================================================

@dataclass
class Notification:
    """Notification record"""
    id: str
    organization_id: str
    user_id: str  # Recipient
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    channels: List[NotificationChannel]
    entity_type: str
    entity_id: str
    action_url: Optional[str]
    status: NotificationStatus
    created_at: datetime
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'notification_type': self.notification_type.value,
            'priority': self.priority.value,
            'title': self.title,
            'message': self.message,
            'channels': [c.value for c in self.channels],
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'action_url': self.action_url,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'metadata': self.metadata
        }

@dataclass
class UserNotificationPreferences:
    """User preferences for notification delivery"""
    user_id: str
    organization_id: str
    
    # Channel preferences per notification type
    preferences: dict = field(default_factory=dict)
    
    # Global settings
    enabled: bool = True
    quiet_hours_start: Optional[int] = None  # Hour (0-23)
    quiet_hours_end: Optional[int] = None
    
    # Digest settings
    digest_enabled: bool = False
    digest_frequency: str = "daily"  # daily, weekly
    
    def get_channels(self, notification_type: NotificationType) -> List[NotificationChannel]:
        """Get enabled channels for a notification type"""
        if not self.enabled:
            return []
        
        # Return user preferences or default to in-app
        return self.preferences.get(notification_type, [NotificationChannel.IN_APP])
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is in quiet hours"""
        if self.quiet_hours_start is None or self.quiet_hours_end is None:
            return False
        
        current_hour = datetime.utcnow().hour
        return self.quiet_hours_start <= current_hour < self.quiet_hours_end

# ============================================================================
# Event Listener System
# ============================================================================

class EventListener:
    """Base class for event listeners"""
    
    def __init__(self, event_types: List[EventType]):
        self.event_types = event_types
    
    def should_handle(self, event: WorkflowEvent) -> bool:
        """Check if this listener should handle the event"""
        return event.event_type in self.event_types
    
    def handle(self, event: WorkflowEvent) -> None:
        """Handle the event - override in subclass"""
        raise NotImplementedError

# ============================================================================
# Notification Service
# ============================================================================

class NotificationService:
    """Service for managing notifications and event listeners"""
    
    def __init__(self):
        self.notifications: dict = {}
        self.user_preferences: dict = {}
        self.listeners: List[EventListener] = []
        
        # Index for fast queries
        self.user_notifications: dict = {}  # user_id -> [notification_ids]
        
        # Register default listeners
        self._register_default_listeners()
    
    def _register_default_listeners(self):
        """Register default notification listeners"""
        
        # Task assignment listener
        assignment_listener = TaskAssignmentListener(self)
        self.register_listener(assignment_listener)
        
        # Status change listener
        status_listener = TaskStatusChangeListener(self)
        self.register_listener(status_listener)
        
        # Due date listener
        due_date_listener = DueDateListener(self)
        self.register_listener(due_date_listener)
    
    # ========================================================================
    # Event Listener Management
    # ========================================================================
    
    def register_listener(self, listener: EventListener):
        """Register an event listener"""
        self.listeners.append(listener)
    
    def unregister_listener(self, listener: EventListener):
        """Unregister an event listener"""
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def emit_event(self, event: WorkflowEvent):
        """Emit an event to all registered listeners"""
        for listener in self.listeners:
            if listener.should_handle(event):
                try:
                    listener.handle(event)
                except Exception as e:
                    print(f"Error in listener {listener.__class__.__name__}: {e}")
    
    # ========================================================================
    # User Preferences
    # ========================================================================
    
    def set_user_preferences(
        self,
        user_id: str,
        organization_id: str,
        preferences: Optional[dict] = None,
        enabled: bool = True,
        quiet_hours_start: Optional[int] = None,
        quiet_hours_end: Optional[int] = None,
        digest_enabled: bool = False,
        digest_frequency: str = "daily"
    ) -> UserNotificationPreferences:
        """Set user notification preferences"""
        pref_key = f"{organization_id}:{user_id}"
        
        if pref_key in self.user_preferences:
            prefs = self.user_preferences[pref_key]
            if preferences:
                prefs.preferences = preferences
            prefs.enabled = enabled
            prefs.quiet_hours_start = quiet_hours_start
            prefs.quiet_hours_end = quiet_hours_end
            prefs.digest_enabled = digest_enabled
            prefs.digest_frequency = digest_frequency
        else:
            prefs = UserNotificationPreferences(
                user_id=user_id,
                organization_id=organization_id,
                preferences=preferences or {},
                enabled=enabled,
                quiet_hours_start=quiet_hours_start,
                quiet_hours_end=quiet_hours_end,
                digest_enabled=digest_enabled,
                digest_frequency=digest_frequency
            )
            self.user_preferences[pref_key] = prefs
        
        return prefs
    
    def get_user_preferences(
        self,
        user_id: str,
        organization_id: str
    ) -> UserNotificationPreferences:
        """Get user notification preferences"""
        pref_key = f"{organization_id}:{user_id}"
        
        if pref_key not in self.user_preferences:
            # Create default preferences
            return self.set_user_preferences(user_id, organization_id)
        
        return self.user_preferences[pref_key]
    
    # ========================================================================
    # Notification CRUD
    # ========================================================================
    
    def create_notification(
        self,
        organization_id: str,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        entity_type: str,
        entity_id: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: Optional[str] = None,
        channels: Optional[List[NotificationChannel]] = None,
        metadata: Optional[dict] = None
    ) -> Notification:
        """Create a new notification"""
        notification_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Get user preferences for channels
        if channels is None:
            prefs = self.get_user_preferences(user_id, organization_id)
            channels = prefs.get_channels(notification_type)
        
        notification = Notification(
            id=notification_id,
            organization_id=organization_id,
            user_id=user_id,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            channels=channels,
            entity_type=entity_type,
            entity_id=entity_id,
            action_url=action_url,
            status=NotificationStatus.PENDING,
            created_at=now,
            sent_at=None,
            read_at=None,
            metadata=metadata or {}
        )
        
        self.notifications[notification_id] = notification
        
        # Index by user
        if user_id not in self.user_notifications:
            self.user_notifications[user_id] = []
        self.user_notifications[user_id].append(notification_id)
        
        # Auto-send notification
        self._send_notification(notification)
        
        return notification
    
    def _send_notification(self, notification: Notification):
        """Send notification through configured channels"""
        # Check quiet hours
        prefs = self.get_user_preferences(notification.user_id, notification.organization_id)
        if prefs.is_quiet_hours() and notification.priority != NotificationPriority.URGENT:
            # Queue for later delivery
            notification.metadata['queued_for_quiet_hours'] = True
            return
        
        # Simulate sending through channels
        for channel in notification.channels:
            if channel == NotificationChannel.IN_APP:
                # In-app notifications are immediately available
                pass
            elif channel == NotificationChannel.EMAIL:
                # Would integrate with email service
                notification.metadata[f'{channel.value}_sent'] = True
            elif channel == NotificationChannel.PUSH:
                # Would integrate with push notification service
                notification.metadata[f'{channel.value}_sent'] = True
            elif channel == NotificationChannel.SMS:
                # Would integrate with SMS service
                notification.metadata[f'{channel.value}_sent'] = True
            elif channel == NotificationChannel.WEBHOOK:
                # Would call webhook URL
                notification.metadata[f'{channel.value}_sent'] = True
        
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID"""
        return self.notifications.get(notification_id)
    
    def mark_as_read(self, notification_id: str) -> Optional[Notification]:
        """Mark notification as read"""
        notification = self.get_notification(notification_id)
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
        return notification
    
    def mark_all_as_read(self, user_id: str, organization_id: str):
        """Mark all notifications as read for a user"""
        notification_ids = self.user_notifications.get(user_id, [])
        for notif_id in notification_ids:
            notification = self.notifications[notif_id]
            if notification.organization_id == organization_id and notification.status != NotificationStatus.READ:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.utcnow()
    
    # ========================================================================
    # Query Operations
    # ========================================================================
    
    def get_user_notifications(
        self,
        user_id: str,
        organization_id: str,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        notification_ids = self.user_notifications.get(user_id, [])
        notifications_list = []
        
        for notif_id in notification_ids:
            notification = self.notifications[notif_id]
            
            if notification.organization_id != organization_id:
                continue
            if unread_only and notification.status == NotificationStatus.READ:
                continue
            if notification_type and notification.notification_type != notification_type:
                continue
            
            notifications_list.append(notification)
        
        # Sort by created_at descending
        notifications_list.sort(key=lambda n: n.created_at, reverse=True)
        return notifications_list[:limit]
    
    def get_unread_count(self, user_id: str, organization_id: str) -> int:
        """Get count of unread notifications"""
        return len([n for n in self.get_user_notifications(user_id, organization_id, unread_only=True)])
    
    def get_notifications_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        organization_id: str
    ) -> List[Notification]:
        """Get all notifications for an entity"""
        entity_notifications = []
        
        for notification in self.notifications.values():
            if (notification.organization_id == organization_id and
                notification.entity_type == entity_type and
                notification.entity_id == entity_id):
                entity_notifications.append(notification)
        
        entity_notifications.sort(key=lambda n: n.created_at, reverse=True)
        return entity_notifications

# ============================================================================
# Built-in Event Listeners
# ============================================================================

class TaskAssignmentListener(EventListener):
    """Listener for task assignment events"""
    
    def __init__(self, notification_service: NotificationService):
        super().__init__([EventType.TASK_ASSIGNED, EventType.TASK_UNASSIGNED])
        self.notification_service = notification_service
    
    def handle(self, event: WorkflowEvent):
        """Handle task assignment/unassignment"""
        if event.event_type == EventType.TASK_ASSIGNED:
            assigned_to = event.data.get('assigned_to')
            assigned_by = event.data.get('assigned_by')
            task_title = event.data.get('task_title', 'Untitled Task')
            task_number = event.data.get('task_number', 0)
            
            if assigned_to and assigned_to != assigned_by:
                # Notify the assignee
                self.notification_service.create_notification(
                    organization_id=event.organization_id,
                    user_id=assigned_to,
                    notification_type=NotificationType.TASK_ASSIGNED,
                    title="New Task Assignment",
                    message=f"You've been assigned to task #{task_number}: {task_title}",
                    entity_type="task",
                    entity_id=event.entity_id,
                    priority=NotificationPriority.NORMAL,
                    action_url=f"/tasks/{event.entity_id}",
                    metadata={
                        'assigned_by': assigned_by,
                        'task_number': task_number
                    }
                )

class TaskStatusChangeListener(EventListener):
    """Listener for task status changes"""
    
    def __init__(self, notification_service: NotificationService):
        super().__init__([EventType.TASK_STATUS_CHANGED])
        self.notification_service = notification_service
    
    def handle(self, event: WorkflowEvent):
        """Handle task status changes"""
        old_status = event.data.get('old_status')
        new_status = event.data.get('new_status')
        task_title = event.data.get('task_title', 'Untitled Task')
        task_number = event.data.get('task_number', 0)
        assigned_to = event.data.get('assigned_to')
        changed_by = event.user_id
        
        # Notify assignee if status changed by someone else
        if assigned_to and assigned_to != changed_by:
            priority = NotificationPriority.HIGH if new_status == 'completed' else NotificationPriority.NORMAL
            
            self.notification_service.create_notification(
                organization_id=event.organization_id,
                user_id=assigned_to,
                notification_type=NotificationType.TASK_STATUS_CHANGED,
                title="Task Status Updated",
                message=f"Task #{task_number}: {task_title} changed from {old_status} to {new_status}",
                entity_type="task",
                entity_id=event.entity_id,
                priority=priority,
                action_url=f"/tasks/{event.entity_id}",
                metadata={
                    'old_status': old_status,
                    'new_status': new_status,
                    'changed_by': changed_by
                }
            )

class DueDateListener(EventListener):
    """Listener for due date events"""
    
    def __init__(self, notification_service: NotificationService):
        super().__init__([EventType.DUE_DATE_APPROACHING, EventType.DUE_DATE_PASSED])
        self.notification_service = notification_service
    
    def handle(self, event: WorkflowEvent):
        """Handle due date approaching/overdue"""
        task_title = event.data.get('task_title', 'Untitled Task')
        task_number = event.data.get('task_number', 0)
        due_date = event.data.get('due_date')
        assigned_to = event.data.get('assigned_to')
        
        if not assigned_to:
            return
        
        if event.event_type == EventType.DUE_DATE_APPROACHING:
            self.notification_service.create_notification(
                organization_id=event.organization_id,
                user_id=assigned_to,
                notification_type=NotificationType.TASK_DUE_SOON,
                title="Task Due Soon",
                message=f"Task #{task_number}: {task_title} is due on {due_date}",
                entity_type="task",
                entity_id=event.entity_id,
                priority=NotificationPriority.HIGH,
                action_url=f"/tasks/{event.entity_id}",
                metadata={'due_date': due_date}
            )
        
        elif event.event_type == EventType.DUE_DATE_PASSED:
            self.notification_service.create_notification(
                organization_id=event.organization_id,
                user_id=assigned_to,
                notification_type=NotificationType.TASK_OVERDUE,
                title="Task Overdue",
                message=f"Task #{task_number}: {task_title} is now overdue (was due {due_date})",
                entity_type="task",
                entity_id=event.entity_id,
                priority=NotificationPriority.URGENT,
                action_url=f"/tasks/{event.entity_id}",
                metadata={'due_date': due_date}
            )

# ============================================================================
# Helper: Due Date Scanner
# ============================================================================

def scan_for_due_dates(
    notification_service: NotificationService,
    task_service,  # TaskService instance
    organization_id: str
):
    """
    Scan tasks for upcoming and overdue due dates
    Should be run periodically (e.g., daily cron job)
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Get all active tasks with due dates
    all_tasks = [t for t in task_service.tasks.values() 
                 if t.organization_id == organization_id 
                 and not t.deleted_at
                 and t.due_date
                 and t.status.value not in ['completed', 'cancelled']]
    
    for task in all_tasks:
        # Check if due tomorrow (approaching)
        if task.due_date == tomorrow:
            event = WorkflowEvent(
                event_type=EventType.DUE_DATE_APPROACHING,
                organization_id=organization_id,
                user_id="system",
                entity_type="task",
                entity_id=task.id,
                timestamp=datetime.utcnow(),
                data={
                    'task_title': task.title,
                    'task_number': task.task_number,
                    'due_date': task.due_date.isoformat(),
                    'assigned_to': task.assigned_to
                }
            )
            notification_service.emit_event(event)
        
        # Check if overdue
        elif task.due_date < today:
            event = WorkflowEvent(
                event_type=EventType.DUE_DATE_PASSED,
                organization_id=organization_id,
                user_id="system",
                entity_type="task",
                entity_id=task.id,
                timestamp=datetime.utcnow(),
                data={
                    'task_title': task.title,
                    'task_number': task.task_number,
                    'due_date': task.due_date.isoformat(),
                    'assigned_to': task.assigned_to
                }
            )
            notification_service.emit_event(event)

# ============================================================================
# Initialize Service
# ============================================================================

notification_service = NotificationService()

print("✅ Notification Service initialized")
print("\nFeatures:")
print("  • Event-driven architecture with listener pattern")
print("  • Decoupled from task system via events")
print("  • User-specific notification preferences")
print("  • Multiple delivery channels (in-app, email, push, SMS, webhook)")
print("  • Quiet hours support")
print("  • Priority-based delivery")
print("  • Task assignment notifications")
print("  • Status change notifications")
print("  • Due date warnings (approaching & overdue)")
print("  • Unread notification tracking")
print("  • Mark as read functionality")
print("\nExported: NotificationService, EventType, NotificationType, WorkflowEvent, notification_service, scan_for_due_dates")
