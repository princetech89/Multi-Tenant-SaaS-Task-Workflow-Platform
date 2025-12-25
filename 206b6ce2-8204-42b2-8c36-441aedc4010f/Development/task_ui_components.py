"""
Task Management UI Components - Reusable components for task views
Includes task cards, filters, status badges, and common UI elements
"""

task_list_filters = """
import React, { useState } from 'react';
import { Search, Filter, SortAsc, Plus, X } from 'lucide-react';

interface TaskFilters {
  search: string;
  status: string[];
  priority: string[];
  assignee: string[];
  tags: string[];
  dateRange: { start: Date | null; end: Date | null };
  sortBy: 'priority' | 'dueDate' | 'created' | 'updated';
  sortOrder: 'asc' | 'desc';
}

interface TaskFiltersComponentProps {
  filters: TaskFilters;
  onFiltersChange: (filters: TaskFilters) => void;
  members: Array<{ id: string; name: string; avatar?: string }>;
  availableTags: string[];
  onCreateTask?: () => void;
}

export const TaskFiltersComponent: React.FC<TaskFiltersComponentProps> = ({
  filters,
  onFiltersChange,
  members,
  availableTags,
  onCreateTask
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const statusOptions = [
    { value: 'todo', label: 'To Do', color: '#909094' },
    { value: 'in_progress', label: 'In Progress', color: '#A1C9F4' },
    { value: 'in_review', label: 'In Review', color: '#FFB482' },
    { value: 'completed', label: 'Completed', color: '#17b26a' },
    { value: 'blocked', label: 'Blocked', color: '#f04438' },
    { value: 'cancelled', label: 'Cancelled', color: '#909094' }
  ];

  const priorityOptions = [
    { value: 'critical', label: 'Critical', icon: '🔴' },
    { value: 'high', label: 'High', icon: '🟠' },
    { value: 'medium', label: 'Medium', icon: '🟡' },
    { value: 'low', label: 'Low', icon: '🟢' }
  ];

  const sortOptions = [
    { value: 'priority', label: 'Priority' },
    { value: 'dueDate', label: 'Due Date' },
    { value: 'created', label: 'Created' },
    { value: 'updated', label: 'Updated' }
  ];

  return (
    <div style={{
      backgroundColor: '#1D1D20',
      padding: '20px',
      borderRadius: '12px',
      border: '1px solid #2D2D30',
      marginBottom: '20px'
    }}>
      {/* Search and Create */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={20} style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: '#909094'
          }} />
          <input
            type="text"
            placeholder="Search tasks..."
            value={filters.search}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            style={{
              width: '100%',
              padding: '12px 12px 12px 44px',
              backgroundColor: '#2D2D30',
              border: '1px solid #3D3D40',
              borderRadius: '8px',
              color: '#fbfbff',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>
        
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          style={{
            padding: '12px 20px',
            backgroundColor: showAdvanced ? '#3D3D40' : '#2D2D30',
            border: '1px solid #3D3D40',
            borderRadius: '8px',
            color: '#fbfbff',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px'
          }}
        >
          <Filter size={18} />
          Filters
        </button>

        {onCreateTask && (
          <button
            onClick={onCreateTask}
            style={{
              padding: '12px 24px',
              backgroundColor: '#ffd400',
              border: 'none',
              borderRadius: '8px',
              color: '#1D1D20',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '14px',
              fontWeight: 600
            }}
          >
            <Plus size={18} />
            New Task
          </button>
        )}
      </div>

      {/* Quick Filters */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: showAdvanced ? '16px' : '0' }}>
        {/* Status Pills */}
        {statusOptions.map(status => {
          const isActive = filters.status.includes(status.value);
          return (
            <button
              key={status.value}
              onClick={() => {
                const newStatus = isActive
                  ? filters.status.filter(s => s !== status.value)
                  : [...filters.status, status.value];
                onFiltersChange({ ...filters, status: newStatus });
              }}
              style={{
                padding: '6px 12px',
                backgroundColor: isActive ? status.color + '20' : '#2D2D30',
                border: `1px solid ${isActive ? status.color : '#3D3D40'}`,
                borderRadius: '20px',
                color: isActive ? status.color : '#fbfbff',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: 500,
                transition: 'all 0.2s'
              }}
            >
              {status.label}
            </button>
          );
        })}
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div style={{
          marginTop: '16px',
          paddingTop: '16px',
          borderTop: '1px solid #2D2D30',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          {/* Priority Filter */}
          <div>
            <label style={{ color: '#909094', fontSize: '12px', marginBottom: '8px', display: 'block' }}>
              Priority
            </label>
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {priorityOptions.map(priority => {
                const isActive = filters.priority.includes(priority.value);
                return (
                  <button
                    key={priority.value}
                    onClick={() => {
                      const newPriority = isActive
                        ? filters.priority.filter(p => p !== priority.value)
                        : [...filters.priority, priority.value];
                      onFiltersChange({ ...filters, priority: newPriority });
                    }}
                    style={{
                      padding: '6px 10px',
                      backgroundColor: isActive ? '#3D3D40' : '#2D2D30',
                      border: `1px solid ${isActive ? '#ffd400' : '#3D3D40'}`,
                      borderRadius: '6px',
                      color: '#fbfbff',
                      cursor: 'pointer',
                      fontSize: '12px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <span>{priority.icon}</span>
                    {priority.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Assignee Filter */}
          <div>
            <label style={{ color: '#909094', fontSize: '12px', marginBottom: '8px', display: 'block' }}>
              Assignee
            </label>
            <select
              multiple
              value={filters.assignee}
              onChange={(e) => {
                const selected = Array.from(e.target.selectedOptions, option => option.value);
                onFiltersChange({ ...filters, assignee: selected });
              }}
              style={{
                width: '100%',
                padding: '8px',
                backgroundColor: '#2D2D30',
                border: '1px solid #3D3D40',
                borderRadius: '6px',
                color: '#fbfbff',
                fontSize: '12px',
                maxHeight: '120px'
              }}
            >
              <option value="">All Members</option>
              {members.map(member => (
                <option key={member.id} value={member.id}>
                  {member.name}
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div>
            <label style={{ color: '#909094', fontSize: '12px', marginBottom: '8px', display: 'block' }}>
              Sort By
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select
                value={filters.sortBy}
                onChange={(e) => onFiltersChange({ ...filters, sortBy: e.target.value as any })}
                style={{
                  flex: 1,
                  padding: '8px',
                  backgroundColor: '#2D2D30',
                  border: '1px solid #3D3D40',
                  borderRadius: '6px',
                  color: '#fbfbff',
                  fontSize: '12px'
                }}
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <button
                onClick={() => onFiltersChange({
                  ...filters,
                  sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc'
                })}
                style={{
                  padding: '8px',
                  backgroundColor: '#2D2D30',
                  border: '1px solid #3D3D40',
                  borderRadius: '6px',
                  color: '#fbfbff',
                  cursor: 'pointer'
                }}
              >
                <SortAsc size={16} style={{
                  transform: filters.sortOrder === 'desc' ? 'scaleY(-1)' : 'none'
                }} />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Summary */}
      {(filters.status.length > 0 || filters.priority.length > 0 || filters.assignee.length > 0 || filters.search) && (
        <div style={{
          marginTop: '12px',
          paddingTop: '12px',
          borderTop: '1px solid #2D2D30',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: '#909094'
        }}>
          <span>Active filters:</span>
          <button
            onClick={() => onFiltersChange({
              search: '',
              status: [],
              priority: [],
              assignee: [],
              tags: [],
              dateRange: { start: null, end: null },
              sortBy: 'priority',
              sortOrder: 'asc'
            })}
            style={{
              padding: '4px 8px',
              backgroundColor: 'transparent',
              border: '1px solid #3D3D40',
              borderRadius: '4px',
              color: '#909094',
              cursor: 'pointer',
              fontSize: '11px'
            }}
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
};
"""

task_card_component = """
import React from 'react';
import { Calendar, User, MessageSquare, CheckSquare, MoreVertical, Clock } from 'lucide-react';

interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  task_number: number;
  assigned_to?: string;
  due_date?: string;
  tags: string[];
  subtask_count?: number;
  completed_subtasks?: number;
  comment_count?: number;
}

interface TaskCardProps {
  task: Task;
  onClick: (taskId: string) => void;
  onStatusChange?: (taskId: string, newStatus: string) => void;
  assignee?: { name: string; avatar?: string };
  compact?: boolean;
}

const statusColors = {
  'todo': '#909094',
  'in_progress': '#A1C9F4',
  'in_review': '#FFB482',
  'completed': '#17b26a',
  'blocked': '#f04438',
  'cancelled': '#909094'
};

const priorityIcons = {
  'critical': '🔴',
  'high': '🟠',
  'medium': '🟡',
  'low': '🟢'
};

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onClick,
  onStatusChange,
  assignee,
  compact = false
}) => {
  const statusColor = statusColors[task.status] || '#909094';
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';

  return (
    <div
      onClick={() => onClick(task.id)}
      style={{
        backgroundColor: '#1D1D20',
        border: '1px solid #2D2D30',
        borderLeft: `3px solid ${statusColor}`,
        borderRadius: '8px',
        padding: compact ? '12px' : '16px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        ':hover': {
          backgroundColor: '#252528',
          borderColor: '#3D3D40'
        }
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = '#252528';
        e.currentTarget.style.borderColor = '#3D3D40';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = '#1D1D20';
        e.currentTarget.style.borderColor = '#2D2D30';
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
          <span style={{
            fontSize: '11px',
            color: '#909094',
            fontWeight: 600,
            fontFamily: 'monospace'
          }}>
            #{task.task_number}
          </span>
          <span style={{ fontSize: '16px' }}>{priorityIcons[task.priority]}</span>
        </div>
        
        <button
          onClick={(e) => {
            e.stopPropagation();
            // Open context menu
          }}
          style={{
            padding: '4px',
            backgroundColor: 'transparent',
            border: 'none',
            borderRadius: '4px',
            color: '#909094',
            cursor: 'pointer'
          }}
        >
          <MoreVertical size={16} />
        </button>
      </div>

      {/* Title */}
      <h4 style={{
        margin: '0 0 8px 0',
        color: '#fbfbff',
        fontSize: compact ? '13px' : '14px',
        fontWeight: 600,
        lineHeight: '1.4'
      }}>
        {task.title}
      </h4>

      {/* Description (if not compact) */}
      {!compact && task.description && (
        <p style={{
          margin: '0 0 12px 0',
          color: '#909094',
          fontSize: '12px',
          lineHeight: '1.5',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {task.description}
        </p>
      )}

      {/* Tags */}
      {task.tags.length > 0 && (
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '12px' }}>
          {task.tags.map((tag, idx) => (
            <span
              key={idx}
              style={{
                padding: '2px 8px',
                backgroundColor: '#2D2D30',
                border: '1px solid #3D3D40',
                borderRadius: '4px',
                color: '#909094',
                fontSize: '10px',
                fontWeight: 500
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Footer */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '11px',
        color: '#909094'
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* Assignee */}
          {assignee && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              {assignee.avatar ? (
                <img
                  src={assignee.avatar}
                  alt={assignee.name}
                  style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    border: '1px solid #3D3D40'
                  }}
                />
              ) : (
                <User size={14} />
              )}
              <span>{assignee.name}</span>
            </div>
          )}

          {/* Subtasks */}
          {task.subtask_count > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <CheckSquare size={14} />
              <span>{task.completed_subtasks}/{task.subtask_count}</span>
            </div>
          )}

          {/* Comments */}
          {task.comment_count > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <MessageSquare size={14} />
              <span>{task.comment_count}</span>
            </div>
          )}
        </div>

        {/* Due Date */}
        {task.due_date && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            color: isOverdue ? '#f04438' : '#909094',
            fontWeight: isOverdue ? 600 : 400
          }}>
            <Clock size={14} />
            <span>{new Date(task.due_date).toLocaleDateString()}</span>
          </div>
        )}
      </div>
    </div>
  );
};
"""

print("✅ Task UI Components created")
print("\nComponents:")
print("  • TaskFiltersComponent - Search, filters, and sorting")
print("  • TaskCard - Individual task card with metadata")
print("\nExported: task_list_filters, task_card_component")
