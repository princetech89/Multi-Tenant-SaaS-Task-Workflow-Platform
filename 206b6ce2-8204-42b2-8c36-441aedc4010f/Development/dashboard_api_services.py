"""
Optimized Dashboard API Services with Aggregated Metrics and Role-Aware Filtering
Provides fast read-optimized endpoints for real-time organizational insights
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
from dataclasses import dataclass
import uuid

# ============================================================================
# Dashboard Metrics Models
# ============================================================================

@dataclass
class OrganizationDashboard:
    """Complete organization dashboard metrics"""
    organization_id: str
    timestamp: datetime
    
    # Project metrics
    total_projects: int
    active_projects: int
    archived_projects: int
    projects_by_visibility: Dict[str, int]
    
    # Task metrics
    total_tasks: int
    tasks_by_status: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    overdue_tasks: int
    assigned_tasks: int
    unassigned_tasks: int
    
    # Activity metrics
    recent_activity_count: int
    total_audit_logs: int
    active_users_today: int
    actions_by_type: Dict[str, int]
    
    # User metrics
    total_members: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'timestamp': self.timestamp.isoformat(),
            'projects': {
                'total': self.total_projects,
                'active': self.active_projects,
                'archived': self.archived_projects,
                'by_visibility': self.projects_by_visibility
            },
            'tasks': {
                'total': self.total_tasks,
                'by_status': self.tasks_by_status,
                'by_priority': self.tasks_by_priority,
                'overdue': self.overdue_tasks,
                'assigned': self.assigned_tasks,
                'unassigned': self.unassigned_tasks
            },
            'activity': {
                'recent_count': self.recent_activity_count,
                'total_logs': self.total_audit_logs,
                'active_users_today': self.active_users_today,
                'actions_by_type': self.actions_by_type
            },
            'members': {
                'total': self.total_members
            }
        }

@dataclass
class ProjectDashboard:
    """Project-specific dashboard metrics"""
    project_id: str
    organization_id: str
    timestamp: datetime
    
    # Project details
    project_name: str
    project_status: str
    project_visibility: str
    
    # Task metrics
    total_tasks: int
    tasks_by_status: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    overdue_tasks: int
    completion_rate: float
    
    # Activity metrics
    recent_activity_count: int
    last_activity_date: Optional[datetime]
    
    # Member metrics
    total_members: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_id': self.project_id,
            'organization_id': self.organization_id,
            'timestamp': self.timestamp.isoformat(),
            'project': {
                'name': self.project_name,
                'status': self.project_status,
                'visibility': self.project_visibility
            },
            'tasks': {
                'total': self.total_tasks,
                'by_status': self.tasks_by_status,
                'by_priority': self.tasks_by_priority,
                'overdue': self.overdue_tasks,
                'completion_rate': self.completion_rate
            },
            'activity': {
                'recent_count': self.recent_activity_count,
                'last_activity': self.last_activity_date.isoformat() if self.last_activity_date else None
            },
            'members': {
                'total': self.total_members
            }
        }

@dataclass
class UserDashboard:
    """User-specific dashboard metrics"""
    user_id: str
    organization_id: str
    timestamp: datetime
    
    # Task metrics
    assigned_tasks: int
    tasks_by_status: Dict[str, int]
    tasks_by_priority: Dict[str, int]
    overdue_tasks: int
    due_soon_tasks: int  # Due within 3 days
    
    # Activity metrics
    recent_activity_count: int
    
    # Project metrics
    accessible_projects: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'timestamp': self.timestamp.isoformat(),
            'tasks': {
                'assigned': self.assigned_tasks,
                'by_status': self.tasks_by_status,
                'by_priority': self.tasks_by_priority,
                'overdue': self.overdue_tasks,
                'due_soon': self.due_soon_tasks
            },
            'activity': {
                'recent_count': self.recent_activity_count
            },
            'projects': {
                'accessible': self.accessible_projects
            }
        }

@dataclass
class RecentActivityItem:
    """Recent activity item for dashboard feeds"""
    activity_id: str
    timestamp: datetime
    user_id: str
    user_name: str
    action: str
    entity_type: str
    entity_id: str
    summary: str
    project_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.activity_id,
            'timestamp': self.timestamp.isoformat(),
            'user': {
                'id': self.user_id,
                'name': self.user_name
            },
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'summary': self.summary,
            'project_id': self.project_id
        }

# ============================================================================
# Dashboard Service - Read-Optimized APIs
# ============================================================================

class DashboardService:
    """
    Service for generating dashboard metrics and insights
    Optimized for fast reads with role-aware data filtering
    """
    
    def __init__(self, project_service, task_service, audit_service):
        self.project_service = project_service
        self.task_service = task_service
        self.audit_service = audit_service
        
        # Cache for dashboard metrics (in production would use Redis)
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes
    
    # ========================================================================
    # Organization Dashboard APIs
    # ========================================================================
    
    def get_organization_dashboard(
        self,
        organization_id: str,
        use_cache: bool = True
    ) -> OrganizationDashboard:
        """
        Get complete organization dashboard with aggregated metrics
        Admin-level view with all projects and tasks
        """
        cache_key = f"org_dashboard:{organization_id}"
        
        if use_cache and cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.utcnow() - cached_time).seconds < self._cache_ttl:
                return cached_data
        
        # Get project statistics
        project_stats = self.project_service.get_project_stats(organization_id)
        
        # Get task statistics
        task_stats = self.task_service.get_task_statistics(organization_id)
        
        # Get audit statistics for recent activity
        today = datetime.utcnow()
        start_of_today = datetime(today.year, today.month, today.day)
        audit_stats = self.audit_service.get_statistics(
            organization_id,
            start_date=start_of_today
        )
        
        # Get recent activity count (last 24 hours)
        recent_logs = self.audit_service.get_organization_logs_paginated(
            organization_id,
            page=1,
            page_size=100,
            start_date=datetime.utcnow() - timedelta(hours=24)
        )
        
        dashboard = OrganizationDashboard(
            organization_id=organization_id,
            timestamp=datetime.utcnow(),
            total_projects=project_stats['total'],
            active_projects=project_stats['active'],
            archived_projects=project_stats['archived'],
            projects_by_visibility=project_stats['by_visibility'],
            total_tasks=task_stats['total'],
            tasks_by_status=task_stats['by_status'],
            tasks_by_priority=task_stats['by_priority'],
            overdue_tasks=task_stats['overdue'],
            assigned_tasks=task_stats['assigned'],
            unassigned_tasks=task_stats['unassigned'],
            recent_activity_count=recent_logs.total_items,
            total_audit_logs=audit_stats['total_logs'],
            active_users_today=audit_stats['total_users_active'],
            actions_by_type=audit_stats['actions_by_type'],
            total_members=0  # Would come from member service
        )
        
        # Cache the result
        if use_cache:
            self._cache[cache_key] = (dashboard, datetime.utcnow())
        
        return dashboard
    
    def get_organization_recent_activity(
        self,
        organization_id: str,
        limit: int = 20,
        user_names: Optional[Dict[str, str]] = None
    ) -> List[RecentActivityItem]:
        """
        Get recent activity for organization dashboard
        Returns formatted activity items ready for display
        """
        user_names = user_names or {}
        
        # Get recent audit logs
        logs_result = self.audit_service.get_organization_logs_paginated(
            organization_id,
            page=1,
            page_size=limit
        )
        
        activity_items = []
        for log in logs_result.items:
            user_name = user_names.get(log.user_id, f"User {log.user_id[:8]}")
            
            # Generate summary based on action and entity
            summary = self._generate_activity_summary(log, user_name)
            
            # Extract project_id from metadata if available
            project_id = log.metadata.get('project_id') if log.metadata else None
            
            activity_items.append(RecentActivityItem(
                activity_id=log.log_id,
                timestamp=log.timestamp,
                user_id=log.user_id,
                user_name=user_name,
                action=log.action.value,
                entity_type=log.entity_type.value,
                entity_id=log.entity_id,
                summary=summary,
                project_id=project_id
            ))
        
        return activity_items
    
    # ========================================================================
    # Project Dashboard APIs
    # ========================================================================
    
    def get_project_dashboard(
        self,
        project_id: str,
        organization_id: str,
        use_cache: bool = True
    ) -> Optional[ProjectDashboard]:
        """
        Get project-specific dashboard with task summaries and activity
        Filtered for project members
        """
        cache_key = f"project_dashboard:{project_id}"
        
        if use_cache and cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.utcnow() - cached_time).seconds < self._cache_ttl:
                return cached_data
        
        # Get project details
        project = self.project_service.get_project(project_id)
        if not project or project.organization_id != organization_id:
            return None
        
        # Get task statistics for this project
        task_stats = self.task_service.get_task_statistics(organization_id, project_id)
        
        # Calculate completion rate
        total = task_stats['total']
        completed = task_stats['by_status'].get('completed', 0)
        completion_rate = (completed / total * 100) if total > 0 else 0.0
        
        # Get recent project activity
        project_activity = self.audit_service.get_project_activity_feed(
            project_id,
            page=1,
            page_size=10
        )
        
        # Get last activity date
        last_activity_date = None
        if project_activity.items:
            last_activity_date = project_activity.items[0].timestamp
        
        # Get project members count
        members = self.project_service.get_project_members(project_id)
        
        dashboard = ProjectDashboard(
            project_id=project_id,
            organization_id=organization_id,
            timestamp=datetime.utcnow(),
            project_name=project.name,
            project_status=project.status.value,
            project_visibility=project.visibility.value,
            total_tasks=task_stats['total'],
            tasks_by_status=task_stats['by_status'],
            tasks_by_priority=task_stats['by_priority'],
            overdue_tasks=task_stats['overdue'],
            completion_rate=completion_rate,
            recent_activity_count=project_activity.total_items,
            last_activity_date=last_activity_date,
            total_members=len(members)
        )
        
        # Cache the result
        if use_cache:
            self._cache[cache_key] = (dashboard, datetime.utcnow())
        
        return dashboard
    
    def get_project_recent_activity(
        self,
        project_id: str,
        limit: int = 20,
        user_names: Optional[Dict[str, str]] = None
    ) -> List[RecentActivityItem]:
        """
        Get recent activity for a specific project
        Returns formatted activity items
        """
        user_names = user_names or {}
        
        # Get project activity logs
        logs_result = self.audit_service.get_project_activity_feed(
            project_id,
            page=1,
            page_size=limit
        )
        
        activity_items = []
        for log in logs_result.items:
            user_name = user_names.get(log.user_id, f"User {log.user_id[:8]}")
            summary = self._generate_activity_summary(log, user_name)
            
            activity_items.append(RecentActivityItem(
                activity_id=log.log_id,
                timestamp=log.timestamp,
                user_id=log.user_id,
                user_name=user_name,
                action=log.action.value,
                entity_type=log.entity_type.value,
                entity_id=log.entity_id,
                summary=summary,
                project_id=project_id
            ))
        
        return activity_items
    
    # ========================================================================
    # User Dashboard APIs (Role-Aware)
    # ========================================================================
    
    def get_user_dashboard(
        self,
        user_id: str,
        organization_id: str
    ) -> UserDashboard:
        """
        Get user-specific dashboard with assigned tasks and accessible projects
        Role-aware filtering based on user permissions
        """
        # Get user's assigned tasks
        user_tasks = self.task_service.get_user_tasks(organization_id, user_id)
        
        # Count tasks by status
        tasks_by_status = {}
        tasks_by_priority = {}
        overdue_count = 0
        due_soon_count = 0
        
        today = date.today()
        soon_threshold = today + timedelta(days=3)
        
        for task in user_tasks:
            # Count by status
            status = task.status.value
            tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
            
            # Count by priority
            priority = task.priority.value
            tasks_by_priority[priority] = tasks_by_priority.get(priority, 0) + 1
            
            # Check if overdue
            if task.due_date and task.due_date < today and task.status.value not in ['completed', 'cancelled']:
                overdue_count += 1
            
            # Check if due soon
            if task.due_date and today <= task.due_date <= soon_threshold and task.status.value not in ['completed', 'cancelled']:
                due_soon_count += 1
        
        # Get user's accessible projects
        accessible_projects = self.project_service.get_user_projects(
            organization_id,
            user_id,
            include_archived=False,
            include_deleted=False
        )
        
        # Get user's recent activity
        user_activity = self.audit_service.get_organization_logs_paginated(
            organization_id,
            page=1,
            page_size=20,
            user_id=user_id,
            start_date=datetime.utcnow() - timedelta(days=7)
        )
        
        return UserDashboard(
            user_id=user_id,
            organization_id=organization_id,
            timestamp=datetime.utcnow(),
            assigned_tasks=len(user_tasks),
            tasks_by_status=tasks_by_status,
            tasks_by_priority=tasks_by_priority,
            overdue_tasks=overdue_count,
            due_soon_tasks=due_soon_count,
            recent_activity_count=user_activity.total_items,
            accessible_projects=len(accessible_projects)
        )
    
    def get_user_accessible_projects(
        self,
        user_id: str,
        organization_id: str,
        include_archived: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get list of projects accessible to a user with basic metrics
        Role-aware based on project visibility and membership
        """
        projects = self.project_service.get_user_projects(
            organization_id,
            user_id,
            include_archived=include_archived,
            include_deleted=False
        )
        
        project_summaries = []
        for project in projects:
            # Get task count for this project
            project_tasks = self.task_service.get_project_tasks(
                organization_id,
                project.id,
                include_deleted=False
            )
            
            # Calculate quick metrics
            total_tasks = len(project_tasks)
            completed_tasks = sum(1 for t in project_tasks if t.status.value == 'completed')
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            project_summaries.append({
                'id': project.id,
                'name': project.name,
                'status': project.status.value,
                'visibility': project.visibility.value,
                'owner_id': project.owner_id,
                'created_at': project.created_at.isoformat(),
                'metrics': {
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'completion_rate': round(completion_rate, 1)
                }
            })
        
        return project_summaries
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _generate_activity_summary(self, log, user_name: str) -> str:
        """Generate human-readable activity summary"""
        action = log.action.value
        entity = log.entity_type.value
        
        if action == 'create':
            return f"{user_name} created a new {entity}"
        elif action == 'update':
            changes = log.get_changes()
            if changes:
                change_list = list(changes.keys())[:2]
                return f"{user_name} updated {entity} ({', '.join(change_list)})"
            return f"{user_name} updated {entity}"
        elif action == 'delete':
            return f"{user_name} deleted {entity}"
        elif action == 'assign':
            return f"{user_name} assigned {entity}"
        elif action == 'archive':
            return f"{user_name} archived {entity}"
        else:
            return f"{user_name} {action}d {entity}"
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """Clear dashboard cache"""
        if cache_key:
            self._cache.pop(cache_key, None)
        else:
            self._cache.clear()

# ============================================================================
# Initialize Service
# ============================================================================

print("✅ Dashboard API Services initialized")
print()
print("Features:")
print("  • Organization-wide dashboard with aggregated metrics")
print("  • Project-specific dashboards with task summaries")
print("  • User-specific dashboards with role-aware filtering")
print("  • Real-time activity feeds for org, project, and user")
print("  • Fast read-optimized queries with caching")
print("  • Automatic metric calculations (completion rates, overdue tasks)")
print("  • Recent activity with human-readable summaries")
print()
print("Exported: DashboardService, OrganizationDashboard, ProjectDashboard, UserDashboard, RecentActivityItem")
