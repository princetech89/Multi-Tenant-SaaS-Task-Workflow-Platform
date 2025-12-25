"""
Members Management and Activity Timeline Components
Team member management with role assignment and comprehensive activity tracking
"""

# ============================================================================
# MEMBERS TAB - Team Management
# ============================================================================

members_tab = """
interface MembersTabProps {
  members: Member[];
  projectId: string;
  onUpdate: () => void;
}

const MembersTab: React.FC<MembersTabProps> = ({ members, projectId, onUpdate }) => {
  const [showInviteModal, setShowInviteModal] = useState(false);

  const handleInviteMember = async (memberData: any) => {
    try {
      await apiService.post(`/api/projects/${projectId}/members`, memberData);
      setShowInviteModal(false);
      onUpdate();
    } catch (error) {
      console.error('Failed to invite member:', error);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!confirm('Are you sure you want to remove this member?')) return;
    try {
      await apiService.delete(`/api/projects/${projectId}/members/${memberId}`);
      onUpdate();
    } catch (error) {
      console.error('Failed to remove member:', error);
    }
  };

  const handleChangeRole = async (memberId: string, newRole: string) => {
    try {
      await apiService.patch(`/api/projects/${projectId}/members/${memberId}`, {
        role: newRole
      });
      onUpdate();
    } catch (error) {
      console.error('Failed to change role:', error);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors = {
      owner: 'bg-[#ffd400]/10 text-[#ffd400] border-[#ffd400]/20',
      admin: 'bg-[#f04438]/10 text-[#f04438] border-[#f04438]/20',
      manager: 'bg-[#A1C9F4]/10 text-[#A1C9F4] border-[#A1C9F4]/20',
      member: 'bg-[#17b26a]/10 text-[#17b26a] border-[#17b26a]/20',
      viewer: 'bg-[#909094]/10 text-[#909094] border-[#909094]/20'
    };
    return colors[role as keyof typeof colors] || colors.member;
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">Team Members ({members.length})</h2>
        <button
          onClick={() => setShowInviteModal(true)}
          className="flex items-center gap-2 bg-[#ffd400] text-[#1D1D20] px-4 py-2 rounded-lg font-medium hover:bg-[#ffd400]/90"
        >
          <Plus className="w-4 h-4" />
          Add Member
        </button>
      </div>

      <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-[#1D1D20] border-b border-[#3a3a3e]">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-[#909094]">Member</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-[#909094]">Role</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-[#909094]">Added</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-[#909094]">Actions</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.id} className="border-b border-[#3a3a3e] hover:bg-[#1D1D20]">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#3a3a3e] flex items-center justify-center text-sm font-medium">
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-medium">{member.name}</div>
                      <div className="text-sm text-[#909094]">{member.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <select
                    value={member.role}
                    onChange={(e) => handleChangeRole(member.id, e.target.value)}
                    className={`px-3 py-1 rounded text-xs border ${getRoleBadgeColor(member.role)} bg-transparent`}
                    disabled={member.role === 'owner'}
                  >
                    <option value="owner">Owner</option>
                    <option value="admin">Admin</option>
                    <option value="manager">Manager</option>
                    <option value="member">Member</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </td>
                <td className="px-6 py-4 text-sm text-[#909094]">
                  {new Date(member.added_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4">
                  {member.role !== 'owner' && (
                    <button
                      onClick={() => handleRemoveMember(member.id)}
                      className="text-red-500 hover:text-red-400 text-sm"
                    >
                      Remove
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showInviteModal && (
        <InviteMemberModal
          onClose={() => setShowInviteModal(false)}
          onInvite={handleInviteMember}
        />
      )}
    </div>
  );
};
""";

# ============================================================================
# ACTIVITY TIMELINE - Comprehensive Project History
# ============================================================================

activity_timeline = """
interface ActivityTimelineProps {
  activities: ActivityItem[];
}

const ActivityTimeline: React.FC<ActivityTimelineProps> = ({ activities }) => {
  const getActivityIcon = (type: string) => {
    const icons = {
      project_created: <Plus className="w-4 h-4" />,
      project_updated: <Edit2 className="w-4 h-4" />,
      task_created: <CheckSquare className="w-4 h-4" />,
      task_updated: <Edit2 className="w-4 h-4" />,
      task_completed: <CheckSquare className="w-4 h-4" />,
      member_added: <Users className="w-4 h-4" />,
      member_removed: <Users className="w-4 h-4" />,
      comment_added: <MessageSquare className="w-4 h-4" />,
      attachment_added: <Paperclip className="w-4 h-4" />
    };
    return icons[type as keyof typeof icons] || <Activity className="w-4 h-4" />;
  };

  const getActivityColor = (type: string) => {
    const colors = {
      project_created: '#17b26a',
      project_updated: '#A1C9F4',
      task_created: '#17b26a',
      task_updated: '#A1C9F4',
      task_completed: '#17b26a',
      member_added: '#17b26a',
      member_removed: '#f04438',
      comment_added: '#FFB482',
      attachment_added: '#D0BBFF'
    };
    return colors[type as keyof typeof colors] || '#909094';
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 7) {
        return `${diffInDays} day${diffInDays !== 1 ? 's' : ''} ago`;
      } else {
        return date.toLocaleDateString();
      }
    }
  };

  const groupedActivities = activities.reduce((acc, activity) => {
    const date = new Date(activity.timestamp).toDateString();
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(activity);
    return acc;
  }, {} as Record<string, ActivityItem[]>);

  return (
    <div>
      <h2 className="text-xl font-semibold mb-6">Activity Timeline</h2>

      <div className="space-y-6">
        {Object.entries(groupedActivities).map(([date, dayActivities]) => (
          <div key={date}>
            <div className="text-sm font-semibold text-[#909094] mb-3">
              {new Date(date).toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>

            <div className="space-y-3">
              {dayActivities.map((activity) => (
                <div
                  key={activity.id}
                  className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg p-4 hover:border-[#ffd400] transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div
                      className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                      style={{ backgroundColor: `${getActivityColor(activity.type)}20` }}
                    >
                      <div style={{ color: getActivityColor(activity.type) }}>
                        {getActivityIcon(activity.type)}
                      </div>
                    </div>

                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">{activity.user_name}</span>
                        <span className="text-[#909094]">{activity.action}</span>
                        <span className="font-medium">{activity.target}</span>
                      </div>
                      <div className="text-xs text-[#909094]">
                        {formatTimestamp(activity.timestamp)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {activities.length === 0 && (
        <div className="text-center py-12 bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg">
          <Activity className="w-12 h-12 text-[#909094] mx-auto mb-3" />
          <p className="text-[#909094]">No activity yet</p>
        </div>
      )}
    </div>
  );
};
""";

# ============================================================================
# CRUD MODALS - Create/Edit Forms
# ============================================================================

create_project_modal = """
interface CreateProjectModalProps {
  onClose: () => void;
  onCreate: (data: any) => void;
}

const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ onClose, onCreate }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    visibility: 'team' as 'private' | 'team' | 'organization'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg w-full max-w-md p-6">
        <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#909094] mb-2">
              Project Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#909094] mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#909094] mb-2">
              Visibility
            </label>
            <select
              value={formData.visibility}
              onChange={(e) => setFormData({ ...formData, visibility: e.target.value as any })}
              className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
            >
              <option value="private">Private - Only you</option>
              <option value="team">Team - Project members</option>
              <option value="organization">Organization - All members</option>
            </select>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-[#3a3a3e] rounded-lg hover:bg-[#4a4a4e] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-[#ffd400] text-[#1D1D20] rounded-lg font-medium hover:bg-[#ffd400]/90 transition-colors"
            >
              Create Project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
""";

create_task_modal = """
interface CreateTaskModalProps {
  onClose: () => void;
  onCreate: (data: any) => void;
}

const CreateTaskModal: React.FC<CreateTaskModalProps> = ({ onClose, onCreate }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent',
    status: 'todo' as 'todo' | 'in_progress' | 'review' | 'done',
    due_date: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onCreate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg w-full max-w-md p-6">
        <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-[#909094] mb-2">
              Task Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#909094] mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#909094] mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#909094] mb-2">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[#909094] mb-2">
              Due Date
            </label>
            <input
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              className="w-full bg-[#1D1D20] border border-[#3a3a3e] rounded-lg px-3 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
            />
          </div>

          <div className="flex gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-[#3a3a3e] rounded-lg hover:bg-[#4a4a4e] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-[#ffd400] text-[#1D1D20] rounded-lg font-medium hover:bg-[#ffd400]/90 transition-colors"
            >
              Create Task
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
""";

print("✅ Members and Activity Tabs Created")
print("\nComponents:")
print("  • MembersTab - Team member management with role controls")
print("  • ActivityTimeline - Comprehensive project activity tracking")
print("  • CreateProjectModal - Project creation form")
print("  • CreateTaskModal - Task creation form")
print("  • Role-based badge colors using Zerve palette")
print("  • Activity grouping by date with relative timestamps")
print("  • Inline role editing for members")
print("  • Icon-based activity indicators")
