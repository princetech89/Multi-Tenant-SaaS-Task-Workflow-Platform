"""
Frontend UI Components for Notification Center
React components with real-time updates, filtering, and activity feed display
"""

# ============================================================================
# Notification Center UI - React Components
# ============================================================================

notification_center_component = """
import React, { useState, useEffect, useCallback } from 'react';
import { Bell, Filter, Check, CheckCheck, X, Search, Calendar, AlertCircle } from 'lucide-react';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [filters, setFilters] = useState({
    read_status: 'all',
    priorities: [],
    notification_types: [],
    search_query: ''
  });
  const [groupBy, setGroupBy] = useState('date'); // 'date', 'type', 'priority'
  const [wsConnection, setWsConnection] = useState(null);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    const ws = new WebSocket(`ws://api.example.com/ws/notifications?token=${token}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnection(ws);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'new_notification') {
        // Add new notification to list
        setNotifications(prev => [data.notification, ...prev]);
        setUnreadCount(prev => prev + 1);
        
        // Show browser notification
        if (Notification.permission === 'granted') {
          new Notification(data.notification.title, {
            body: data.notification.message,
            icon: '/notification-icon.png'
          });
        }
      } else if (data.type === 'notification_read') {
        // Update notification status
        setNotifications(prev =>
          prev.map(n => n.id === data.notification_id ? {...n, read: true} : n)
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  // Fetch notifications
  useEffect(() => {
    fetchNotifications();
  }, [filters, groupBy]);

  const fetchNotifications = async () => {
    const response = await fetch('/api/notifications/filtered', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ filters, group_by: groupBy })
    });
    
    const data = await response.json();
    setNotifications(data.notifications);
    setUnreadCount(data.unread_count);
  };

  const markAsRead = async (notificationId) => {
    await fetch(`/api/notifications/${notificationId}/read`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    setNotifications(prev =>
      prev.map(n => n.id === notificationId ? {...n, read_at: new Date().toISOString()} : n)
    );
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllAsRead = async () => {
    await fetch('/api/notifications/mark-all-read', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });
    
    setNotifications(prev => prev.map(n => ({...n, read_at: new Date().toISOString()})));
    setUnreadCount(0);
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      normal: 'bg-blue-100 text-blue-800 border-blue-300',
      low: 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[priority] || colors.normal;
  };

  const getNotificationIcon = (type) => {
    const icons = {
      task_assigned: '📋',
      task_due_soon: '⏰',
      task_overdue: '🚨',
      task_status_changed: '🔄',
      task_updated: '✏️',
      subtask_completed: '✅',
      mention: '💬'
    };
    return icons[type] || '🔔';
  };

  return (
    <div className=\"relative\">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className=\"relative p-2 rounded-lg hover:bg-gray-100 transition-colors\"
      >
        <Bell className=\"w-6 h-6 text-gray-700\" />
        {unreadCount > 0 && (
          <span className=\"absolute top-0 right-0 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full\">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <div className=\"absolute right-0 mt-2 w-96 max-h-[600px] bg-white rounded-lg shadow-2xl border border-gray-200 z-50\">
          {/* Header */}
          <div className=\"flex items-center justify-between p-4 border-b border-gray-200\">
            <h3 className=\"text-lg font-semibold text-gray-900\">Notifications</h3>
            <div className=\"flex items-center gap-2\">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className=\"text-sm text-blue-600 hover:text-blue-700 font-medium\"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className=\"p-1 hover:bg-gray-100 rounded\"
              >
                <X className=\"w-5 h-5 text-gray-500\" />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className=\"p-3 border-b border-gray-200 bg-gray-50\">
            <div className=\"flex items-center gap-2 mb-2\">
              <Search className=\"w-4 h-4 text-gray-400\" />
              <input
                type=\"text\"
                placeholder=\"Search notifications...\"
                value={filters.search_query}
                onChange={(e) => setFilters({...filters, search_query: e.target.value})}
                className=\"flex-1 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500\"
              />
            </div>
            
            <div className=\"flex items-center gap-2\">
              <select
                value={filters.read_status}
                onChange={(e) => setFilters({...filters, read_status: e.target.value})}
                className=\"text-sm border border-gray-300 rounded px-2 py-1\"
              >
                <option value=\"all\">All</option>
                <option value=\"unread\">Unread</option>
                <option value=\"read\">Read</option>
              </select>

              <select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value)}
                className=\"text-sm border border-gray-300 rounded px-2 py-1\"
              >
                <option value=\"date\">Group by Date</option>
                <option value=\"type\">Group by Type</option>
                <option value=\"priority\">Group by Priority</option>
              </select>
            </div>
          </div>

          {/* Notifications List */}
          <div className=\"overflow-y-auto max-h-96\">
            {notifications.length === 0 ? (
              <div className=\"p-8 text-center text-gray-500\">
                <Bell className=\"w-12 h-12 mx-auto mb-3 text-gray-300\" />
                <p>No notifications</p>
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors ${
                    !notification.read_at ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => {
                    if (!notification.read_at) markAsRead(notification.id);
                    if (notification.action_url) window.location.href = notification.action_url;
                  }}
                >
                  <div className=\"flex items-start gap-3\">
                    <span className=\"text-2xl\">{getNotificationIcon(notification.notification_type)}</span>
                    
                    <div className=\"flex-1 min-w-0\">
                      <div className=\"flex items-center justify-between mb-1\">
                        <h4 className=\"text-sm font-semibold text-gray-900 truncate\">
                          {notification.title}
                        </h4>
                        {!notification.read_at && (
                          <div className=\"w-2 h-2 bg-blue-500 rounded-full flex-shrink-0\" />
                        )}
                      </div>
                      
                      <p className=\"text-sm text-gray-600 mb-2\">{notification.message}</p>
                      
                      <div className=\"flex items-center gap-2\">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded border ${getPriorityColor(notification.priority)}`}>
                          {notification.priority}
                        </span>
                        <span className=\"text-xs text-gray-500\">
                          {new Date(notification.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className=\"p-3 border-t border-gray-200 bg-gray-50\">
            <a
              href=\"/notifications\"
              className=\"block text-center text-sm text-blue-600 hover:text-blue-700 font-medium\"
            >
              View all notifications
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter;
"""

# ============================================================================
# Activity Feed Component
# ============================================================================

activity_feed_component = """
import React, { useState, useEffect } from 'react';
import { Activity, Clock, User, CheckCircle, AlertCircle, TrendingUp } from 'lucide-react';

const ActivityFeed = ({ organizationId, projectId, taskId, userId }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'assignments', 'updates', 'alerts'
  const [timeframe, setTimeframe] = useState('today'); // 'today', 'week', 'month'

  useEffect(() => {
    fetchActivities();
  }, [filter, timeframe, organizationId, projectId, taskId, userId]);

  const fetchActivities = async () => {
    setLoading(true);
    
    const params = new URLSearchParams({
      filter,
      timeframe,
      ...(organizationId && { organization_id: organizationId }),
      ...(projectId && { project_id: projectId }),
      ...(taskId && { task_id: taskId }),
      ...(userId && { user_id: userId })
    });

    const response = await fetch(`/api/activity-feed?${params}`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
    });

    const data = await response.json();
    setActivities(data.feed);
    setLoading(false);
  };

  const getActivityIcon = (notificationType, priority) => {
    if (priority === 'urgent') return <AlertCircle className=\"w-5 h-5 text-red-500\" />;
    
    const icons = {
      task_assigned: <User className=\"w-5 h-5 text-blue-500\" />,
      task_status_changed: <CheckCircle className=\"w-5 h-5 text-green-500\" />,
      task_due_soon: <Clock className=\"w-5 h-5 text-orange-500\" />,
      task_updated: <TrendingUp className=\"w-5 h-5 text-purple-500\" />
    };
    
    return icons[notificationType] || <Activity className=\"w-5 h-5 text-gray-500\" />;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className=\"bg-white rounded-lg shadow-sm border border-gray-200\">
      {/* Header */}
      <div className=\"p-4 border-b border-gray-200\">
        <div className=\"flex items-center justify-between mb-3\">
          <h2 className=\"text-lg font-semibold text-gray-900 flex items-center gap-2\">
            <Activity className=\"w-5 h-5\" />
            Activity Feed
          </h2>
        </div>

        {/* Filters */}
        <div className=\"flex items-center gap-2\">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className=\"text-sm border border-gray-300 rounded px-3 py-1.5\"
          >
            <option value=\"all\">All Activity</option>
            <option value=\"assignments\">Assignments</option>
            <option value=\"updates\">Status Updates</option>
            <option value=\"alerts\">Alerts & Due Dates</option>
          </select>

          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className=\"text-sm border border-gray-300 rounded px-3 py-1.5\"
          >
            <option value=\"today\">Today</option>
            <option value=\"week\">This Week</option>
            <option value=\"month\">This Month</option>
            <option value=\"all\">All Time</option>
          </select>
        </div>
      </div>

      {/* Activity List */}
      <div className=\"divide-y divide-gray-100\">
        {loading ? (
          <div className=\"p-8 text-center text-gray-500\">
            <div className=\"animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2\" />
            <p>Loading activities...</p>
          </div>
        ) : activities.length === 0 ? (
          <div className=\"p-8 text-center text-gray-500\">
            <Activity className=\"w-12 h-12 mx-auto mb-3 text-gray-300\" />
            <p>No activity to display</p>
          </div>
        ) : (
          activities.map((activity) => (
            <div
              key={activity.id}
              className=\"p-4 hover:bg-gray-50 transition-colors\"
            >
              <div className=\"flex items-start gap-3\">
                {/* Icon */}
                <div className=\"flex-shrink-0 mt-1\">
                  {getActivityIcon(activity.notification_type, activity.priority)}
                </div>

                {/* Content */}
                <div className=\"flex-1 min-w-0\">
                  <div className=\"flex items-start justify-between gap-2 mb-1\">
                    <p className=\"text-sm font-medium text-gray-900\">
                      {activity.title}
                    </p>
                    <span className=\"text-xs text-gray-500 whitespace-nowrap\">
                      {formatTimestamp(activity.timestamp)}
                    </span>
                  </div>

                  <p className=\"text-sm text-gray-600 mb-2\">
                    {activity.message}
                  </p>

                  {/* Priority Badge */}
                  {activity.priority !== 'normal' && (
                    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded ${
                      activity.priority === 'urgent' ? 'bg-red-100 text-red-800' :
                      activity.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {activity.priority.toUpperCase()}
                    </span>
                  )}

                  {/* Action Link */}
                  {activity.action_url && (
                    <a
                      href={activity.action_url}
                      className=\"inline-block mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium\"
                    >
                      View details →
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Load More */}
      {activities.length > 0 && activities.length % 20 === 0 && (
        <div className=\"p-4 border-t border-gray-200 text-center\">
          <button
            onClick={() => fetchActivities()}
            className=\"text-sm text-blue-600 hover:text-blue-700 font-medium\"
          >
            Load more
          </button>
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;
"""

# ============================================================================
# Notification Settings Component
# ============================================================================

notification_settings_component = """
import React, { useState, useEffect } from 'react';
import { Bell, Mail, Smartphone, Globe, Clock } from 'lucide-react';

const NotificationSettings = () => {
  const [settings, setSettings] = useState({
    enabled: true,
    quiet_hours_start: null,
    quiet_hours_end: null,
    channels: {
      task_assigned: ['in_app', 'email'],
      task_due_soon: ['in_app', 'email', 'push'],
      task_overdue: ['in_app', 'email', 'push'],
      task_status_changed: ['in_app'],
      task_updated: ['in_app'],
      subtask_completed: ['in_app'],
      mention: ['in_app', 'email', 'push']
    }
  });

  const notificationTypes = [
    { value: 'task_assigned', label: 'Task Assignments', description: 'When you are assigned to a task' },
    { value: 'task_due_soon', label: 'Due Date Reminders', description: 'When a task is due soon' },
    { value: 'task_overdue', label: 'Overdue Alerts', description: 'When a task becomes overdue' },
    { value: 'task_status_changed', label: 'Status Changes', description: 'When task status is updated' },
    { value: 'task_updated', label: 'Task Updates', description: 'When task details are modified' },
    { value: 'subtask_completed', label: 'Subtask Completion', description: 'When subtasks are completed' },
    { value: 'mention', label: 'Mentions', description: 'When you are mentioned in comments' }
  ];

  const channels = [
    { value: 'in_app', label: 'In-App', icon: Bell },
    { value: 'email', label: 'Email', icon: Mail },
    { value: 'push', label: 'Push', icon: Smartphone },
    { value: 'webhook', label: 'Webhook', icon: Globe }
  ];

  const handleChannelToggle = (notifType, channel) => {
    setSettings(prev => ({
      ...prev,
      channels: {
        ...prev.channels,
        [notifType]: prev.channels[notifType].includes(channel)
          ? prev.channels[notifType].filter(c => c !== channel)
          : [...prev.channels[notifType], channel]
      }
    }));
  };

  const saveSettings = async () => {
    await fetch('/api/notifications/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify(settings)
    });
    alert('Settings saved successfully!');
  };

  return (
    <div className=\"max-w-4xl mx-auto p-6\">
      <div className=\"bg-white rounded-lg shadow-sm border border-gray-200\">
        {/* Header */}
        <div className=\"p-6 border-b border-gray-200\">
          <h2 className=\"text-xl font-semibold text-gray-900 mb-2\">Notification Settings</h2>
          <p className=\"text-sm text-gray-600\">
            Manage how and when you receive notifications
          </p>
        </div>

        {/* Global Enable/Disable */}
        <div className=\"p-6 border-b border-gray-200\">
          <label className=\"flex items-center justify-between\">
            <div>
              <h3 className=\"text-sm font-medium text-gray-900\">Enable Notifications</h3>
              <p className=\"text-sm text-gray-500\">Receive notifications across all channels</p>
            </div>
            <input
              type=\"checkbox\"
              checked={settings.enabled}
              onChange={(e) => setSettings({...settings, enabled: e.target.checked})}
              className=\"w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500\"
            />
          </label>
        </div>

        {/* Quiet Hours */}
        <div className=\"p-6 border-b border-gray-200\">
          <div className=\"flex items-start gap-3 mb-4\">
            <Clock className=\"w-5 h-5 text-gray-400 mt-0.5\" />
            <div className=\"flex-1\">
              <h3 className=\"text-sm font-medium text-gray-900 mb-1\">Quiet Hours</h3>
              <p className=\"text-sm text-gray-500 mb-4\">
                Pause non-urgent notifications during specific hours
              </p>
              
              <div className=\"flex items-center gap-4\">
                <div>
                  <label className=\"block text-xs text-gray-600 mb-1\">From</label>
                  <input
                    type=\"time\"
                    value={settings.quiet_hours_start || ''}
                    onChange={(e) => setSettings({...settings, quiet_hours_start: e.target.value})}
                    className=\"px-3 py-2 border border-gray-300 rounded text-sm\"
                  />
                </div>
                <div>
                  <label className=\"block text-xs text-gray-600 mb-1\">To</label>
                  <input
                    type=\"time\"
                    value={settings.quiet_hours_end || ''}
                    onChange={(e) => setSettings({...settings, quiet_hours_end: e.target.value})}
                    className=\"px-3 py-2 border border-gray-300 rounded text-sm\"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Notification Channels */}
        <div className=\"p-6\">
          <h3 className=\"text-sm font-medium text-gray-900 mb-4\">Notification Channels</h3>
          
          <div className=\"space-y-6\">
            {notificationTypes.map((notifType) => (
              <div key={notifType.value} className=\"border-b border-gray-100 last:border-0 pb-6 last:pb-0\">
                <div className=\"mb-3\">
                  <h4 className=\"text-sm font-medium text-gray-900\">{notifType.label}</h4>
                  <p className=\"text-xs text-gray-500\">{notifType.description}</p>
                </div>
                
                <div className=\"flex items-center gap-4\">
                  {channels.map((channel) => {
                    const Icon = channel.icon;
                    const isActive = settings.channels[notifType.value]?.includes(channel.value);
                    
                    return (
                      <button
                        key={channel.value}
                        onClick={() => handleChannelToggle(notifType.value, channel.value)}
                        className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 text-sm font-medium transition-colors ${
                          isActive
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                        }`}
                      >
                        <Icon className=\"w-4 h-4\" />
                        {channel.label}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className=\"p-6 border-t border-gray-200 bg-gray-50\">
          <button
            onClick={saveSettings}
            className=\"px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors\"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotificationSettings;
"""

# ============================================================================
# Export All Components
# ============================================================================

print("=" * 100)
print("NOTIFICATION UI COMPONENTS - FRONTEND IMPLEMENTATION")
print("=" * 100)
print()

print("✅ Generated React Components for Notification System")
print()
print("COMPONENTS CREATED:")
print("  1. NotificationCenter - Real-time notification dropdown with filtering")
print("  2. ActivityFeed - Unified activity feed with timeframe filtering")
print("  3. NotificationSettings - User preferences for notification channels")
print()
print("KEY FEATURES:")
print("  ✓ WebSocket integration for real-time updates")
print("  ✓ Advanced filtering (search, status, type, priority)")
print("  ✓ Unread count badge with automatic updates")
print("  ✓ Mark as read functionality (individual and bulk)")
print("  ✓ Browser notifications for important alerts")
print("  ✓ Responsive design with Tailwind CSS")
print("  ✓ Activity feed with multiple views and timeframes")
print("  ✓ Notification settings with channel preferences")
print("  ✓ Quiet hours configuration")
print("  ✓ Priority-based styling and icons")
print()
print("INTEGRATION POINTS:")
print("  • WebSocket: ws://api.example.com/ws/notifications")
print("  • REST API: /api/notifications/*")
print("  • Activity Feed: /api/activity-feed")
print("  • Settings: /api/notifications/settings")
print()
print("=" * 100)

notification_components = {
    'NotificationCenter': notification_center_component,
    'ActivityFeed': activity_feed_component,
    'NotificationSettings': notification_settings_component
}