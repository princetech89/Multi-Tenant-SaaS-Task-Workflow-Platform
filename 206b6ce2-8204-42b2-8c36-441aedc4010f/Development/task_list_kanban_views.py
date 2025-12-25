"""
Task List and Kanban Board Views
Includes both list and board layouts with drag-and-drop support
"""

task_list_view = """
import React, { useState, useMemo } from 'react';
import { Layers, LayoutList } from 'lucide-react';
import { TaskFiltersComponent } from './TaskFilters';
import { TaskCard } from './TaskCard';

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
  created_at: string;
  updated_at: string;
}

interface TaskListViewProps {
  tasks: Task[];
  members: Array<{ id: string; name: string; avatar?: string }>;
  onTaskClick: (taskId: string) => void;
  onCreateTask: () => void;
  onStatusChange: (taskId: string, newStatus: string) => void;
}

export const TaskListView: React.FC<TaskListViewProps> = ({
  tasks,
  members,
  onTaskClick,
  onCreateTask,
  onStatusChange
}) => {
  const [filters, setFilters] = useState({
    search: '',
    status: [],
    priority: [],
    assignee: [],
    tags: [],
    dateRange: { start: null, end: null },
    sortBy: 'priority' as const,
    sortOrder: 'asc' as const
  });

  // Extract unique tags from all tasks
  const availableTags = useMemo(() => {
    const tagSet = new Set<string>();
    tasks.forEach(task => task.tags.forEach(tag => tagSet.add(tag)));
    return Array.from(tagSet);
  }, [tasks]);

  // Apply filters and sorting
  const filteredTasks = useMemo(() => {
    let filtered = [...tasks];

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(searchLower) ||
        task.description?.toLowerCase().includes(searchLower) ||
        task.task_number.toString().includes(searchLower)
      );
    }

    // Status filter
    if (filters.status.length > 0) {
      filtered = filtered.filter(task => filters.status.includes(task.status));
    }

    // Priority filter
    if (filters.priority.length > 0) {
      filtered = filtered.filter(task => filters.priority.includes(task.priority));
    }

    // Assignee filter
    if (filters.assignee.length > 0) {
      filtered = filtered.filter(task => 
        task.assigned_to && filters.assignee.includes(task.assigned_to)
      );
    }

    // Tags filter
    if (filters.tags.length > 0) {
      filtered = filtered.filter(task =>
        filters.tags.some(tag => task.tags.includes(tag))
      );
    }

    // Sorting
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (filters.sortBy) {
        case 'priority':
          comparison = priorityOrder[a.priority] - priorityOrder[b.priority];
          break;
        case 'dueDate':
          const dateA = a.due_date ? new Date(a.due_date).getTime() : Infinity;
          const dateB = b.due_date ? new Date(b.due_date).getTime() : Infinity;
          comparison = dateA - dateB;
          break;
        case 'created':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'updated':
          comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
          break;
      }

      return filters.sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [tasks, filters]);

  // Group tasks by status
  const tasksByStatus = useMemo(() => {
    const grouped = {
      todo: [],
      in_progress: [],
      in_review: [],
      completed: [],
      blocked: [],
      cancelled: []
    };

    filteredTasks.forEach(task => {
      if (grouped[task.status]) {
        grouped[task.status].push(task);
      }
    });

    return grouped;
  }, [filteredTasks]);

  return (
    <div style={{
      padding: '24px',
      backgroundColor: '#151518',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{
            margin: '0 0 8px 0',
            color: '#fbfbff',
            fontSize: '28px',
            fontWeight: 700
          }}>
            Tasks
          </h1>
          <p style={{
            margin: 0,
            color: '#909094',
            fontSize: '14px'
          }}>
            {filteredTasks.length} task{filteredTasks.length !== 1 ? 's' : ''}
            {filters.search || filters.status.length > 0 || filters.priority.length > 0 
              ? ` (filtered from ${tasks.length})` 
              : ''}
          </p>
        </div>
      </div>

      {/* Filters */}
      <TaskFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        members={members}
        availableTags={availableTags}
        onCreateTask={onCreateTask}
      />

      {/* Task List - Grouped by Status */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {Object.entries(tasksByStatus).map(([status, statusTasks]) => {
          if (statusTasks.length === 0) return null;

          const statusLabels = {
            todo: 'To Do',
            in_progress: 'In Progress',
            in_review: 'In Review',
            completed: 'Completed',
            blocked: 'Blocked',
            cancelled: 'Cancelled'
          };

          const statusColors = {
            todo: '#909094',
            in_progress: '#A1C9F4',
            in_review: '#FFB482',
            completed: '#17b26a',
            blocked: '#f04438',
            cancelled: '#909094'
          };

          return (
            <div key={status}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '12px'
              }}>
                <div style={{
                  width: '4px',
                  height: '20px',
                  backgroundColor: statusColors[status],
                  borderRadius: '2px'
                }} />
                <h2 style={{
                  margin: 0,
                  color: '#fbfbff',
                  fontSize: '16px',
                  fontWeight: 600
                }}>
                  {statusLabels[status]}
                </h2>
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: '#2D2D30',
                  borderRadius: '12px',
                  color: '#909094',
                  fontSize: '12px',
                  fontWeight: 600
                }}>
                  {statusTasks.length}
                </span>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '12px'
              }}>
                {statusTasks.map(task => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onClick={onTaskClick}
                    onStatusChange={onStatusChange}
                    assignee={members.find(m => m.id === task.assigned_to)}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredTasks.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#909094'
        }}>
          <LayoutList size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
          <h3 style={{ margin: '0 0 8px 0', color: '#fbfbff', fontSize: '18px' }}>
            No tasks found
          </h3>
          <p style={{ margin: '0 0 16px 0', fontSize: '14px' }}>
            {filters.search || filters.status.length > 0 || filters.priority.length > 0
              ? 'Try adjusting your filters'
              : 'Create your first task to get started'}
          </p>
          {(!filters.search && filters.status.length === 0) && (
            <button
              onClick={onCreateTask}
              style={{
                padding: '10px 20px',
                backgroundColor: '#ffd400',
                border: 'none',
                borderRadius: '8px',
                color: '#1D1D20',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 600
              }}
            >
              Create Task
            </button>
          )}
        </div>
      )}
    </div>
  );
};
"""

task_kanban_view = """
import React, { useState, useMemo } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Plus } from 'lucide-react';
import { TaskFiltersComponent } from './TaskFilters';
import { TaskCard } from './TaskCard';

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
  position: number;
}

interface KanbanColumn {
  id: string;
  label: string;
  color: string;
  tasks: Task[];
}

interface TaskKanbanViewProps {
  tasks: Task[];
  members: Array<{ id: string; name: string; avatar?: string }>;
  onTaskClick: (taskId: string) => void;
  onCreateTask: (status?: string) => void;
  onStatusChange: (taskId: string, newStatus: string, newPosition: number) => void;
}

export const TaskKanbanView: React.FC<TaskKanbanViewProps> = ({
  tasks,
  members,
  onTaskClick,
  onCreateTask,
  onStatusChange
}) => {
  const [filters, setFilters] = useState({
    search: '',
    status: [],
    priority: [],
    assignee: [],
    tags: [],
    dateRange: { start: null, end: null },
    sortBy: 'priority' as const,
    sortOrder: 'asc' as const
  });

  const availableTags = useMemo(() => {
    const tagSet = new Set<string>();
    tasks.forEach(task => task.tags.forEach(tag => tagSet.add(tag)));
    return Array.from(tagSet);
  }, [tasks]);

  // Apply filters
  const filteredTasks = useMemo(() => {
    let filtered = [...tasks];

    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(searchLower) ||
        task.description?.toLowerCase().includes(searchLower) ||
        task.task_number.toString().includes(searchLower)
      );
    }

    if (filters.priority.length > 0) {
      filtered = filtered.filter(task => filters.priority.includes(task.priority));
    }

    if (filters.assignee.length > 0) {
      filtered = filtered.filter(task => 
        task.assigned_to && filters.assignee.includes(task.assigned_to)
      );
    }

    if (filters.tags.length > 0) {
      filtered = filtered.filter(task =>
        filters.tags.some(tag => task.tags.includes(tag))
      );
    }

    return filtered;
  }, [tasks, filters]);

  // Organize into columns
  const columns: KanbanColumn[] = useMemo(() => {
    const columnDefs = [
      { id: 'todo', label: 'To Do', color: '#909094' },
      { id: 'in_progress', label: 'In Progress', color: '#A1C9F4' },
      { id: 'in_review', label: 'In Review', color: '#FFB482' },
      { id: 'completed', label: 'Completed', color: '#17b26a' }
    ];

    return columnDefs.map(col => ({
      ...col,
      tasks: filteredTasks
        .filter(task => task.status === col.id)
        .sort((a, b) => a.position - b.position)
    }));
  }, [filteredTasks]);

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const { source, destination, draggableId } = result;

    // Moved to different column (status change)
    if (source.droppableId !== destination.droppableId) {
      onStatusChange(draggableId, destination.droppableId, destination.index);
    } 
    // Reordered within same column
    else if (source.index !== destination.index) {
      onStatusChange(draggableId, source.droppableId, destination.index);
    }
  };

  return (
    <div style={{
      padding: '24px',
      backgroundColor: '#151518',
      minHeight: '100vh',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{
          margin: '0 0 8px 0',
          color: '#fbfbff',
          fontSize: '28px',
          fontWeight: 700
        }}>
          Task Board
        </h1>
        <p style={{
          margin: 0,
          color: '#909094',
          fontSize: '14px'
        }}>
          {filteredTasks.length} task{filteredTasks.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Filters (compact version for kanban) */}
      <TaskFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        members={members}
        availableTags={availableTags}
        onCreateTask={() => onCreateTask()}
      />

      {/* Kanban Board */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, minmax(300px, 1fr))',
          gap: '16px',
          overflowX: 'auto',
          paddingBottom: '24px'
        }}>
          {columns.map(column => (
            <div
              key={column.id}
              style={{
                backgroundColor: '#1D1D20',
                border: '1px solid #2D2D30',
                borderRadius: '12px',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                minHeight: '600px',
                maxHeight: 'calc(100vh - 300px)'
              }}
            >
              {/* Column Header */}
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px',
                paddingBottom: '12px',
                borderBottom: `2px solid ${column.color}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h3 style={{
                    margin: 0,
                    color: '#fbfbff',
                    fontSize: '14px',
                    fontWeight: 600
                  }}>
                    {column.label}
                  </h3>
                  <span style={{
                    padding: '2px 8px',
                    backgroundColor: column.color + '20',
                    border: `1px solid ${column.color}`,
                    borderRadius: '12px',
                    color: column.color,
                    fontSize: '11px',
                    fontWeight: 600
                  }}>
                    {column.tasks.length}
                  </span>
                </div>
                
                <button
                  onClick={() => onCreateTask(column.id)}
                  style={{
                    padding: '4px',
                    backgroundColor: 'transparent',
                    border: 'none',
                    borderRadius: '4px',
                    color: '#909094',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2D2D30'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <Plus size={16} />
                </button>
              </div>

              {/* Droppable Column */}
              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    style={{
                      flex: 1,
                      overflowY: 'auto',
                      backgroundColor: snapshot.isDraggingOver ? '#252528' : 'transparent',
                      borderRadius: '8px',
                      transition: 'background-color 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {column.tasks.map((task, index) => (
                        <Draggable key={task.id} draggableId={task.id} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              style={{
                                ...provided.draggableProps.style,
                                opacity: snapshot.isDragging ? 0.8 : 1,
                                transform: snapshot.isDragging 
                                  ? provided.draggableProps.style?.transform + ' rotate(2deg)'
                                  : provided.draggableProps.style?.transform
                              }}
                            >
                              <TaskCard
                                task={task}
                                onClick={onTaskClick}
                                assignee={members.find(m => m.id === task.assigned_to)}
                                compact
                              />
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>

                    {/* Empty Column State */}
                    {column.tasks.length === 0 && (
                      <div style={{
                        textAlign: 'center',
                        padding: '40px 20px',
                        color: '#909094',
                        fontSize: '13px'
                      }}>
                        Drop tasks here
                      </div>
                    )}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>
    </div>
  );
};
"""

print("✅ Task List and Kanban Views created")
print("\nViews:")
print("  • TaskListView - List layout with grouping and filtering")
print("  • TaskKanbanView - Kanban board with drag-and-drop")
print("\nExported: task_list_view, task_kanban_view")
