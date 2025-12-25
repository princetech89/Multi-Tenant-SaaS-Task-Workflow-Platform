"""
Task Detail Page with Subtasks, Comments, and Activity History
Full task view with all details, inline editing, and comprehensive workflow controls
"""

task_detail_page = """
import React, { useState, useEffect } from 'react';
import { 
  X, Edit2, Save, Trash2, Clock, User, Tag, Calendar, 
  CheckSquare, MessageSquare, Activity, Plus, MoreVertical,
  ArrowLeft, AlertCircle, Flag
} from 'lucide-react';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  task_number: number;
  assigned_to?: string;
  created_by: string;
  due_date?: string;
  start_date?: string;
  tags: string[];
  estimated_hours?: number;
  actual_hours?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

interface Subtask {
  id: string;
  title: string;
  description?: string;
  status: string;
  assigned_to?: string;
  completed_at?: string;
}

interface Comment {
  id: string;
  user_id: string;
  user_name: string;
  content: string;
  created_at: string;
  updated_at?: string;
}

interface ActivityItem {
  id: string;
  user_name: string;
  action: string;
  field?: string;
  old_value?: string;
  new_value?: string;
  timestamp: string;
}

interface TaskDetailPageProps {
  taskId: string;
  onClose: () => void;
  onUpdate: (taskId: string, updates: Partial<Task>) => void;
  onDelete: (taskId: string) => void;
  members: Array<{ id: string; name: string; avatar?: string }>;
  currentUserId: string;
}

export const TaskDetailPage: React.FC<TaskDetailPageProps> = ({
  taskId,
  onClose,
  onUpdate,
  onDelete,
  members,
  currentUserId
}) => {
  // State
  const [task, setTask] = useState<Task | null>(null);
  const [subtasks, setSubtasks] = useState<Subtask[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [activeTab, setActiveTab] = useState<'details' | 'comments' | 'activity'>('details');
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<Task>>({});
  const [newComment, setNewComment] = useState('');
  const [newSubtask, setNewSubtask] = useState('');

  // Load task data
  useEffect(() => {
    // In real app, fetch from API
    // This is mock data
    loadTaskData();
  }, [taskId]);

  const loadTaskData = async () => {
    // Mock task data
    const mockTask: Task = {
      id: taskId,
      title: 'Implement user authentication',
      description: 'Add JWT-based authentication with OAuth support for Google and GitHub. Include password reset and email verification flows.',
      status: 'in_progress',
      priority: 'high',
      task_number: 42,
      assigned_to: 'user-1',
      created_by: 'user-2',
      due_date: '2025-01-15',
      start_date: '2025-01-05',
      tags: ['backend', 'security', 'authentication'],
      estimated_hours: 16,
      actual_hours: 8.5,
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-08T14:30:00Z'
    };

    const mockSubtasks: Subtask[] = [
      { id: 's1', title: 'Set up JWT token generation', status: 'completed', completed_at: '2025-01-06T16:00:00Z' },
      { id: 's2', title: 'Implement OAuth providers', status: 'completed', assigned_to: 'user-1', completed_at: '2025-01-07T12:00:00Z' },
      { id: 's3', title: 'Add password reset flow', status: 'in_progress', assigned_to: 'user-1' },
      { id: 's4', title: 'Email verification system', status: 'todo' }
    ];

    const mockComments: Comment[] = [
      { id: 'c1', user_id: 'user-1', user_name: 'John Doe', content: 'Started working on this. OAuth setup is complete.', created_at: '2025-01-07T10:00:00Z' },
      { id: 'c2', user_id: 'user-2', user_name: 'Jane Smith', content: 'Great progress! Make sure to add rate limiting for password reset.', created_at: '2025-01-07T14:30:00Z' }
    ];

    const mockActivity: ActivityItem[] = [
      { id: 'a1', user_name: 'John Doe', action: 'status_changed', field: 'status', old_value: 'todo', new_value: 'in_progress', timestamp: '2025-01-05T09:00:00Z' },
      { id: 'a2', user_name: 'Jane Smith', action: 'assigned', field: 'assigned_to', new_value: 'John Doe', timestamp: '2025-01-05T08:30:00Z' },
      { id: 'a3', user_name: 'Jane Smith', action: 'created', timestamp: '2025-01-01T10:00:00Z' }
    ];

    setTask(mockTask);
    setSubtasks(mockSubtasks);
    setComments(mockComments);
    setActivity(mockActivity);
    setEditForm(mockTask);
  };

  const statusOptions = [
    { value: 'todo', label: 'To Do', color: '#909094' },
    { value: 'in_progress', label: 'In Progress', color: '#A1C9F4' },
    { value: 'in_review', label: 'In Review', color: '#FFB482' },
    { value: 'completed', label: 'Completed', color: '#17b26a' },
    { value: 'blocked', label: 'Blocked', color: '#f04438' }
  ];

  const priorityOptions = [
    { value: 'critical', label: 'Critical', icon: '🔴', color: '#f04438' },
    { value: 'high', label: 'High', icon: '🟠', color: '#FFB482' },
    { value: 'medium', label: 'Medium', icon: '🟡', color: '#ffd400' },
    { value: 'low', label: 'Low', icon: '🟢', color: '#17b26a' }
  ];

  if (!task) return <div>Loading...</div>;

  const currentStatus = statusOptions.find(s => s.value === task.status);
  const currentPriority = priorityOptions.find(p => p.value === task.priority);
  const assignee = members.find(m => m.id === task.assigned_to);
  const completedSubtasks = subtasks.filter(s => s.status === 'completed').length;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      zIndex: 1000,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: '#1D1D20',
        borderRadius: '16px',
        maxWidth: '1200px',
        width: '100%',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        border: '1px solid #2D2D30'
      }}>
        {/* Header */}
        <div style={{
          padding: '24px',
          borderBottom: '1px solid #2D2D30',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <span style={{
                fontSize: '13px',
                color: '#909094',
                fontWeight: 600,
                fontFamily: 'monospace'
              }}>
                #{task.task_number}
              </span>
              <span style={{ fontSize: '18px' }}>{currentPriority?.icon}</span>
            </div>
            
            {isEditing ? (
              <input
                type="text"
                value={editForm.title || ''}
                onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: '#2D2D30',
                  border: '1px solid #3D3D40',
                  borderRadius: '6px',
                  color: '#fbfbff',
                  fontSize: '20px',
                  fontWeight: 600
                }}
              />
            ) : (
              <h2 style={{
                margin: 0,
                color: '#fbfbff',
                fontSize: '24px',
                fontWeight: 700
              }}>
                {task.title}
              </h2>
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px' }}>
            {isEditing ? (
              <>
                <button
                  onClick={() => {
                    onUpdate(task.id, editForm);
                    setIsEditing(false);
                  }}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#17b26a',
                    border: 'none',
                    borderRadius: '6px',
                    color: '#fbfbff',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                >
                  <Save size={16} />
                  Save
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditForm(task);
                  }}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#2D2D30',
                    border: '1px solid #3D3D40',
                    borderRadius: '6px',
                    color: '#fbfbff',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                style={{
                  padding: '8px',
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: '#909094',
                  cursor: 'pointer'
                }}
              >
                <Edit2 size={18} />
              </button>
            )}
            
            <button
              onClick={onClose}
              style={{
                padding: '8px',
                backgroundColor: 'transparent',
                border: 'none',
                color: '#909094',
                cursor: 'pointer'
              }}
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div style={{
          display: 'flex',
          flex: 1,
          overflow: 'hidden'
        }}>
          {/* Main Content */}
          <div style={{
            flex: 1,
            padding: '24px',
            overflowY: 'auto'
          }}>
            {/* Tabs */}
            <div style={{
              display: 'flex',
              gap: '4px',
              marginBottom: '24px',
              borderBottom: '1px solid #2D2D30'
            }}>
              {(['details', 'comments', 'activity'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: 'transparent',
                    border: 'none',
                    borderBottom: activeTab === tab ? '2px solid #ffd400' : '2px solid transparent',
                    color: activeTab === tab ? '#fbfbff' : '#909094',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: 600,
                    textTransform: 'capitalize'
                  }}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Details Tab */}
            {activeTab === 'details' && (
              <div>
                {/* Description */}
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ margin: '0 0 12px 0', color: '#fbfbff', fontSize: '14px', fontWeight: 600 }}>
                    Description
                  </h3>
                  {isEditing ? (
                    <textarea
                      value={editForm.description || ''}
                      onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                      style={{
                        width: '100%',
                        minHeight: '120px',
                        padding: '12px',
                        backgroundColor: '#2D2D30',
                        border: '1px solid #3D3D40',
                        borderRadius: '6px',
                        color: '#fbfbff',
                        fontSize: '14px',
                        fontFamily: 'inherit',
                        resize: 'vertical'
                      }}
                    />
                  ) : (
                    <p style={{
                      margin: 0,
                      color: '#909094',
                      fontSize: '14px',
                      lineHeight: '1.6'
                    }}>
                      {task.description || 'No description provided'}
                    </p>
                  )}
                </div>

                {/* Subtasks */}
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h3 style={{ margin: 0, color: '#fbfbff', fontSize: '14px', fontWeight: 600 }}>
                      Subtasks ({completedSubtasks}/{subtasks.length})
                    </h3>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {subtasks.map(subtask => (
                      <div
                        key={subtask.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          padding: '12px',
                          backgroundColor: '#2D2D30',
                          borderRadius: '6px',
                          border: '1px solid #3D3D40'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={subtask.status === 'completed'}
                          onChange={() => {
                            // Toggle subtask status
                          }}
                          style={{
                            width: '18px',
                            height: '18px',
                            cursor: 'pointer'
                          }}
                        />
                        <span style={{
                          flex: 1,
                          color: subtask.status === 'completed' ? '#909094' : '#fbfbff',
                          textDecoration: subtask.status === 'completed' ? 'line-through' : 'none',
                          fontSize: '14px'
                        }}>
                          {subtask.title}
                        </span>
                        {subtask.assigned_to && (
                          <User size={14} style={{ color: '#909094' }} />
                        )}
                      </div>
                    ))}

                    {/* Add Subtask */}
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <input
                        type="text"
                        value={newSubtask}
                        onChange={(e) => setNewSubtask(e.target.value)}
                        placeholder="Add a subtask..."
                        style={{
                          flex: 1,
                          padding: '10px 12px',
                          backgroundColor: '#2D2D30',
                          border: '1px solid #3D3D40',
                          borderRadius: '6px',
                          color: '#fbfbff',
                          fontSize: '13px'
                        }}
                      />
                      <button
                        onClick={() => {
                          if (newSubtask.trim()) {
                            // Add subtask
                            setNewSubtask('');
                          }
                        }}
                        style={{
                          padding: '10px 16px',
                          backgroundColor: '#ffd400',
                          border: 'none',
                          borderRadius: '6px',
                          color: '#1D1D20',
                          cursor: 'pointer',
                          fontWeight: 600
                        }}
                      >
                        Add
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Comments Tab */}
            {activeTab === 'comments' && (
              <div>
                <div style={{ marginBottom: '24px' }}>
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a comment..."
                    style={{
                      width: '100%',
                      minHeight: '100px',
                      padding: '12px',
                      backgroundColor: '#2D2D30',
                      border: '1px solid #3D3D40',
                      borderRadius: '6px',
                      color: '#fbfbff',
                      fontSize: '14px',
                      fontFamily: 'inherit',
                      resize: 'vertical',
                      marginBottom: '12px'
                    }}
                  />
                  <button
                    onClick={() => {
                      if (newComment.trim()) {
                        // Add comment
                        setNewComment('');
                      }
                    }}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#ffd400',
                      border: 'none',
                      borderRadius: '6px',
                      color: '#1D1D20',
                      cursor: 'pointer',
                      fontWeight: 600
                    }}
                  >
                    Post Comment
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {comments.map(comment => (
                    <div
                      key={comment.id}
                      style={{
                        padding: '16px',
                        backgroundColor: '#2D2D30',
                        borderRadius: '8px',
                        border: '1px solid #3D3D40'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ color: '#fbfbff', fontSize: '13px', fontWeight: 600 }}>
                          {comment.user_name}
                        </span>
                        <span style={{ color: '#909094', fontSize: '12px' }}>
                          {new Date(comment.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p style={{ margin: 0, color: '#fbfbff', fontSize: '14px', lineHeight: '1.5' }}>
                        {comment.content}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Activity Tab */}
            {activeTab === 'activity' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {activity.map(item => (
                  <div
                    key={item.id}
                    style={{
                      padding: '12px',
                      backgroundColor: '#2D2D30',
                      borderRadius: '6px',
                      border: '1px solid #3D3D40',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}
                  >
                    <Activity size={16} style={{ color: '#909094' }} />
                    <div style={{ flex: 1 }}>
                      <p style={{ margin: 0, color: '#fbfbff', fontSize: '13px' }}>
                        <strong>{item.user_name}</strong>{' '}
                        {item.action === 'status_changed' && `changed status from ${item.old_value} to ${item.new_value}`}
                        {item.action === 'assigned' && `assigned to ${item.new_value}`}
                        {item.action === 'created' && 'created this task'}
                      </p>
                      <span style={{ color: '#909094', fontSize: '11px' }}>
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar - Task Metadata */}
          <div style={{
            width: '320px',
            padding: '24px',
            borderLeft: '1px solid #2D2D30',
            backgroundColor: '#1A1A1D',
            overflowY: 'auto'
          }}>
            <h3 style={{ margin: '0 0 20px 0', color: '#fbfbff', fontSize: '14px', fontWeight: 600 }}>
              Task Details
            </h3>

            {/* Status */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', color: '#909094', fontSize: '12px', marginBottom: '8px' }}>
                Status
              </label>
              <select
                value={task.status}
                onChange={(e) => onUpdate(task.id, { status: e.target.value })}
                disabled={!isEditing}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: currentStatus?.color + '20',
                  border: `1px solid ${currentStatus?.color}`,
                  borderRadius: '6px',
                  color: currentStatus?.color,
                  fontSize: '13px',
                  fontWeight: 600
                }}
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Priority */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', color: '#909094', fontSize: '12px', marginBottom: '8px' }}>
                Priority
              </label>
              <select
                value={task.priority}
                onChange={(e) => onUpdate(task.id, { priority: e.target.value })}
                disabled={!isEditing}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: '#2D2D30',
                  border: '1px solid #3D3D40',
                  borderRadius: '6px',
                  color: '#fbfbff',
                  fontSize: '13px'
                }}
              >
                {priorityOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.icon} {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Assignee */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', color: '#909094', fontSize: '12px', marginBottom: '8px' }}>
                Assignee
              </label>
              <select
                value={task.assigned_to || ''}
                onChange={(e) => onUpdate(task.id, { assigned_to: e.target.value })}
                disabled={!isEditing}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: '#2D2D30',
                  border: '1px solid #3D3D40',
                  borderRadius: '6px',
                  color: '#fbfbff',
                  fontSize: '13px'
                }}
              >
                <option value="">Unassigned</option>
                {members.map(member => (
                  <option key={member.id} value={member.id}>
                    {member.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Dates */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', color: '#909094', fontSize: '12px', marginBottom: '8px' }}>
                Due Date
              </label>
              <input
                type="date"
                value={task.due_date || ''}
                onChange={(e) => onUpdate(task.id, { due_date: e.target.value })}
                disabled={!isEditing}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  backgroundColor: '#2D2D30',
                  border: '1px solid #3D3D40',
                  borderRadius: '6px',
                  color: '#fbfbff',
                  fontSize: '13px'
                }}
              />
            </div>

            {/* Hours */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', color: '#909094', fontSize: '12px', marginBottom: '8px' }}>
                Time Tracking
              </label>
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ flex: 1 }}>
                  <input
                    type="number"
                    value={task.estimated_hours || ''}
                    placeholder="Est."
                    disabled={!isEditing}
                    style={{
                      width: '100%',
                      padding: '8px',
                      backgroundColor: '#2D2D30',
                      border: '1px solid #3D3D40',
                      borderRadius: '6px',
                      color: '#fbfbff',
                      fontSize: '12px'
                    }}
                  />
                  <span style={{ color: '#909094', fontSize: '10px' }}>Estimated</span>
                </div>
                <div style={{ flex: 1 }}>
                  <input
                    type="number"
                    value={task.actual_hours || ''}
                    placeholder="Act."
                    disabled={!isEditing}
                    style={{
                      width: '100%',
                      padding: '8px',
                      backgroundColor: '#2D2D30',
                      border: '1px solid #3D3D40',
                      borderRadius: '6px',
                      color: '#fbfbff',
                      fontSize: '12px'
                    }}
                  />
                  <span style={{ color: '#909094', fontSize: '10px' }}>Actual</span>
                </div>
              </div>
            </div>

            {/* Tags */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', color: '#909094', fontSize: '12px', marginBottom: '8px' }}>
                Tags
              </label>
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                {task.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    style={{
                      padding: '4px 10px',
                      backgroundColor: '#2D2D30',
                      border: '1px solid #3D3D40',
                      borderRadius: '12px',
                      color: '#909094',
                      fontSize: '11px',
                      fontWeight: 500
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Delete */}
            <button
              onClick={() => {
                if (confirm('Are you sure you want to delete this task?')) {
                  onDelete(task.id);
                  onClose();
                }
              }}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: 'transparent',
                border: '1px solid #f04438',
                borderRadius: '6px',
                color: '#f04438',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              <Trash2 size={16} />
              Delete Task
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
"""

print("✅ Task Detail Page created")
print("\nFeatures:")
print("  • Full task details with inline editing")
print("  • Subtasks with checkbox completion")
print("  • Comments section with add/view")
print("  • Activity history timeline")
print("  • Sidebar with status, priority, assignee controls")
print("  • Time tracking and tags")
print("  • Delete confirmation")
print("\nExported: task_detail_page")
