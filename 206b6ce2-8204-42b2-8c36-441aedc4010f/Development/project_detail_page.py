"""
Project Detail Page with Task Board View
Comprehensive project view with tabs for overview, tasks, members, and activity timeline
"""

# ============================================================================
# PROJECT DETAIL PAGE - MAIN COMPONENT
# ============================================================================

project_detail_page = """
import React, { useState, useEffect } from 'react';
import {
  ArrowLeft, Settings, Archive, Trash2, Users, CheckSquare,
  Activity, MoreVertical, Plus, Edit2, Calendar, Clock,
  MessageSquare, Paperclip, Flag
} from 'lucide-react';
import { apiService } from './services/api';

interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'archived' | 'deleted';
  visibility: 'private' | 'team' | 'organization';
  owner_id: string;
  created_at: string;
  updated_at: string;
  metadata: any;
}

interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'review' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assignee_id?: string;
  due_date?: string;
  created_at: string;
}

interface Member {
  id: string;
  user_id: string;
  role: string;
  name: string;
  email: string;
  added_at: string;
}

interface ActivityItem {
  id: string;
  type: string;
  user_id: string;
  user_name: string;
  action: string;
  target: string;
  timestamp: string;
}

const ProjectDetailPage: React.FC<{ projectId: string }> = ({ projectId }) => {
  const [project, setProject] = useState<Project | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'members' | 'activity'>('overview');
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [activities, setActivities] = useState<ActivityItem[]>([]);

  useEffect(() => {
    loadProjectData();
  }, [projectId]);

  const loadProjectData = async () => {
    try {
      setLoading(true);
      const [projectRes, tasksRes, membersRes, activitiesRes] = await Promise.all([
        apiService.get(`/api/projects/${projectId}`),
        apiService.get(`/api/projects/${projectId}/tasks`),
        apiService.get(`/api/projects/${projectId}/members`),
        apiService.get(`/api/projects/${projectId}/activities`)
      ]);
      
      setProject(projectRes.data);
      setTasks(tasksRes.data);
      setMembers(membersRes.data);
      setActivities(activitiesRes.data);
    } catch (error) {
      console.error('Failed to load project data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProject = async (updates: Partial<Project>) => {
    try {
      await apiService.patch(`/api/projects/${projectId}`, updates);
      loadProjectData();
    } catch (error) {
      console.error('Failed to update project:', error);
    }
  };

  if (loading || !project) {
    return (
      <div className="min-h-screen bg-[#1D1D20] flex items-center justify-center">
        <div className="text-[#909094]">Loading project...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#1D1D20] text-[#fbfbff]">
      {/* Header */}
      <div className="border-b border-[#3a3a3e] bg-[#2a2a2e]">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4 mb-4">
            <a href="/projects" className="hover:text-[#ffd400]">
              <ArrowLeft className="w-5 h-5" />
            </a>
            <div className="flex-1">
              <h1 className="text-2xl font-bold">{project.name}</h1>
              <p className="text-[#909094] text-sm mt-1">{project.description}</p>
            </div>
            <div className="flex gap-2">
              <button className="p-2 hover:bg-[#3a3a3e] rounded">
                <Settings className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-[#3a3a3e] rounded">
                <MoreVertical className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('overview')}
              className={`pb-3 border-b-2 transition-colors ${
                activeTab === 'overview'
                  ? 'border-[#ffd400] text-[#ffd400]'
                  : 'border-transparent text-[#909094] hover:text-[#fbfbff]'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('tasks')}
              className={`pb-3 border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'tasks'
                  ? 'border-[#ffd400] text-[#ffd400]'
                  : 'border-transparent text-[#909094] hover:text-[#fbfbff]'
              }`}
            >
              <CheckSquare className="w-4 h-4" />
              Tasks ({tasks.length})
            </button>
            <button
              onClick={() => setActiveTab('members')}
              className={`pb-3 border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'members'
                  ? 'border-[#ffd400] text-[#ffd400]'
                  : 'border-transparent text-[#909094] hover:text-[#fbfbff]'
              }`}
            >
              <Users className="w-4 h-4" />
              Members ({members.length})
            </button>
            <button
              onClick={() => setActiveTab('activity')}
              className={`pb-3 border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === 'activity'
                  ? 'border-[#ffd400] text-[#ffd400]'
                  : 'border-transparent text-[#909094] hover:text-[#fbfbff]'
              }`}
            >
              <Activity className="w-4 h-4" />
              Activity
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === 'overview' && <OverviewTab project={project} />}
        {activeTab === 'tasks' && <TaskBoardView tasks={tasks} projectId={projectId} onUpdate={loadProjectData} />}
        {activeTab === 'members' && <MembersTab members={members} projectId={projectId} onUpdate={loadProjectData} />}
        {activeTab === 'activity' && <ActivityTimeline activities={activities} />}
      </div>
    </div>
  );
};

export default ProjectDetailPage;
""";

# ============================================================================
# TASK BOARD VIEW (Kanban)
# ============================================================================

task_board_view = """
interface TaskBoardProps {
  tasks: Task[];
  projectId: string;
  onUpdate: () => void;
}

const TaskBoardView: React.FC<TaskBoardProps> = ({ tasks, projectId, onUpdate }) => {
  const [showCreateModal, setShowCreateModal] = useState(false);

  const columns = [
    { id: 'todo', title: 'To Do', color: '#909094' },
    { id: 'in_progress', title: 'In Progress', color: '#A1C9F4' },
    { id: 'review', title: 'Review', color: '#FFB482' },
    { id: 'done', title: 'Done', color: '#17b26a' }
  ];

  const getTasksByStatus = (status: string) => {
    return tasks.filter(task => task.status === status);
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: '#909094',
      medium: '#A1C9F4',
      high: '#FFB482',
      urgent: '#f04438'
    };
    return colors[priority as keyof typeof colors] || colors.low;
  };

  const handleCreateTask = async (taskData: any) => {
    try {
      await apiService.post(`/api/projects/${projectId}/tasks`, taskData);
      setShowCreateModal(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId);
  };

  const handleDrop = async (e: React.DragEvent, newStatus: string) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    try {
      await apiService.patch(`/api/tasks/${taskId}`, { status: newStatus });
      onUpdate();
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Task Board</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-[#ffd400] text-[#1D1D20] px-4 py-2 rounded-lg font-medium hover:bg-[#ffd400]/90"
        >
          <Plus className="w-4 h-4" />
          New Task
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {columns.map(column => (
          <div
            key={column.id}
            className="bg-[#2a2a2e] rounded-lg p-4"
            onDrop={(e) => handleDrop(e, column.id)}
            onDragOver={handleDragOver}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: column.color }}
                />
                <h3 className="font-semibold">{column.title}</h3>
              </div>
              <span className="text-sm text-[#909094]">
                {getTasksByStatus(column.id).length}
              </span>
            </div>

            <div className="space-y-3">
              {getTasksByStatus(column.id).map(task => (
                <div
                  key={task.id}
                  draggable
                  onDragStart={(e) => handleDragStart(e, task.id)}
                  className="bg-[#1D1D20] border border-[#3a3a3e] rounded-lg p-3 cursor-move hover:border-[#ffd400] transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-sm">{task.title}</h4>
                    <div
                      className="w-2 h-2 rounded-full mt-1"
                      style={{ backgroundColor: getPriorityColor(task.priority) }}
                    />
                  </div>
                  
                  {task.description && (
                    <p className="text-xs text-[#909094] mb-2 line-clamp-2">
                      {task.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between text-xs text-[#909094]">
                    <div className="flex items-center gap-2">
                      {task.assignee_id && (
                        <div className="w-5 h-5 rounded-full bg-[#3a3a3e] flex items-center justify-center">
                          <Users className="w-3 h-3" />
                        </div>
                      )}
                      {task.due_date && (
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span>{new Date(task.due_date).toLocaleDateString()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {showCreateModal && (
        <CreateTaskModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateTask}
        />
      )}
    </div>
  );
};
""";

# ============================================================================
# OVERVIEW TAB
# ============================================================================

overview_tab = """
interface OverviewTabProps {
  project: Project;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ project }) => {
  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Main Info */}
      <div className="col-span-2 space-y-6">
        <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Project Details</h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-[#909094] block mb-1">Description</label>
              <p className="text-[#fbfbff]">{project.description || 'No description provided'}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-[#909094] block mb-1">Status</label>
                <span className="capitalize text-[#fbfbff]">{project.status}</span>
              </div>
              <div>
                <label className="text-sm text-[#909094] block mb-1">Visibility</label>
                <span className="capitalize text-[#fbfbff]">{project.visibility}</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-[#909094] block mb-1">Created</label>
                <p className="text-[#fbfbff]">{new Date(project.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <label className="text-sm text-[#909094] block mb-1">Last Updated</label>
                <p className="text-[#fbfbff]">{new Date(project.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity Preview */}
        <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="text-[#909094] text-sm">
            View the Activity tab for full timeline
          </div>
        </div>
      </div>

      {/* Sidebar Stats */}
      <div className="space-y-6">
        <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg p-6">
          <h3 className="font-semibold mb-4">Quick Stats</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[#909094]">Total Tasks</span>
              <span className="font-semibold">0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#909094]">Completed</span>
              <span className="font-semibold text-[#17b26a]">0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#909094]">In Progress</span>
              <span className="font-semibold text-[#A1C9F4]">0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[#909094]">Team Members</span>
              <span className="font-semibold">0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
""";

print("✅ Project Detail Page Created")
print("\nComponents:")
print("  • ProjectDetailPage - Main detail view with tabs")
print("  • TaskBoardView - Kanban board with drag & drop")
print("  • OverviewTab - Project details and stats")
print("  • Four-column task board (To Do, In Progress, Review, Done)")
print("  • Drag-and-drop task status updates")
print("  • Priority indicators with color coding")
print("  • Task creation modal integration")
