"""
Project Management UI Components
React/TypeScript components for project list, detail pages, and CRUD operations
"""

# ============================================================================
# PROJECT LIST PAGE
# ============================================================================

project_list_page = """
import React, { useState, useEffect } from 'react';
import { 
  Plus, Archive, Trash2, MoreVertical, Search, Filter,
  Grid, List as ListIcon, Eye, Users, Lock
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
  member_count?: number;
  task_count?: number;
}

const ProjectListPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'archived'>('active');
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadProjects();
  }, [statusFilter]);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const response = await apiService.get('/api/projects', {
        params: {
          include_archived: statusFilter !== 'active',
          status: statusFilter === 'all' ? undefined : statusFilter
        }
      });
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (projectData: any) => {
    try {
      await apiService.post('/api/projects', projectData);
      setShowCreateModal(false);
      loadProjects();
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  const handleArchiveProject = async (projectId: string) => {
    try {
      await apiService.post(`/api/projects/${projectId}/archive`);
      loadProjects();
    } catch (error) {
      console.error('Failed to archive project:', error);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    try {
      await apiService.delete(`/api/projects/${projectId}`);
      loadProjects();
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getVisibilityIcon = (visibility: string) => {
    switch (visibility) {
      case 'private': return <Lock className="w-4 h-4" />;
      case 'team': return <Users className="w-4 h-4" />;
      case 'organization': return <Eye className="w-4 h-4" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      active: 'bg-green-500/10 text-green-500 border-green-500/20',
      archived: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
      deleted: 'bg-red-500/10 text-red-500 border-red-500/20'
    };
    return (
      <span className={`px-2 py-1 rounded text-xs border ${styles[status as keyof typeof styles]}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-[#1D1D20] text-[#fbfbff] p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold mb-2">Projects</h1>
            <p className="text-[#909094]">Manage your organization's projects</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 bg-[#ffd400] text-[#1D1D20] px-4 py-2 rounded-lg font-medium hover:bg-[#ffd400]/90 transition-colors"
          >
            <Plus className="w-5 h-5" />
            New Project
          </button>
        </div>

        {/* Filters and Search */}
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[#909094]" />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg pl-10 pr-4 py-2 text-[#fbfbff] placeholder-[#909094] focus:outline-none focus:border-[#ffd400]"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as any)}
            className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg px-4 py-2 text-[#fbfbff] focus:outline-none focus:border-[#ffd400]"
          >
            <option value="active">Active</option>
            <option value="archived">Archived</option>
            <option value="all">All</option>
          </select>

          <div className="flex gap-2 border border-[#3a3a3e] rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-[#3a3a3e]' : ''}`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-[#3a3a3e]' : ''}`}
            >
              <ListIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Project Grid/List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-[#909094]">Loading projects...</div>
        </div>
      ) : filteredProjects.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-[#909094] text-lg">No projects found</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onArchive={handleArchiveProject}
              onDelete={handleDeleteProject}
              getVisibilityIcon={getVisibilityIcon}
              getStatusBadge={getStatusBadge}
            />
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredProjects.map((project) => (
            <ProjectListItem
              key={project.id}
              project={project}
              onArchive={handleArchiveProject}
              onDelete={handleDeleteProject}
              getVisibilityIcon={getVisibilityIcon}
              getStatusBadge={getStatusBadge}
            />
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateProjectModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateProject}
        />
      )}
    </div>
  );
};

export default ProjectListPage;
""";

# ============================================================================
# PROJECT CARD COMPONENT (Grid View)
# ============================================================================

project_card_component = """
interface ProjectCardProps {
  project: Project;
  onArchive: (id: string) => void;
  onDelete: (id: string) => void;
  getVisibilityIcon: (visibility: string) => React.ReactNode;
  getStatusBadge: (status: string) => React.ReactNode;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onArchive,
  onDelete,
  getVisibilityIcon,
  getStatusBadge
}) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg p-6 hover:border-[#ffd400] transition-colors cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <a href={`/projects/${project.id}`} className="block">
            <h3 className="text-xl font-semibold mb-2 hover:text-[#ffd400] transition-colors">
              {project.name}
            </h3>
          </a>
          <p className="text-[#909094] text-sm line-clamp-2">
            {project.description || 'No description'}
          </p>
        </div>
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1 hover:bg-[#3a3a3e] rounded"
          >
            <MoreVertical className="w-5 h-5" />
          </button>
          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg shadow-lg z-10">
              <button
                onClick={() => {
                  onArchive(project.id);
                  setShowMenu(false);
                }}
                className="w-full text-left px-4 py-2 hover:bg-[#3a3a3e] flex items-center gap-2"
              >
                <Archive className="w-4 h-4" />
                Archive
              </button>
              <button
                onClick={() => {
                  onDelete(project.id);
                  setShowMenu(false);
                }}
                className="w-full text-left px-4 py-2 hover:bg-[#3a3a3e] text-red-500 flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-[#909094]">
        <div className="flex items-center gap-2">
          {getVisibilityIcon(project.visibility)}
          <span className="capitalize">{project.visibility}</span>
        </div>
        <div>{getStatusBadge(project.status)}</div>
      </div>

      <div className="mt-4 pt-4 border-t border-[#3a3a3e] flex items-center justify-between text-sm">
        <div className="text-[#909094]">
          <span className="font-medium text-[#fbfbff]">{project.task_count || 0}</span> tasks
        </div>
        <div className="text-[#909094]">
          <span className="font-medium text-[#fbfbff]">{project.member_count || 0}</span> members
        </div>
        <div className="text-[#909094]">
          {new Date(project.updated_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};
""";

# ============================================================================
# PROJECT LIST ITEM (List View)
# ============================================================================

project_list_item = """
const ProjectListItem: React.FC<ProjectCardProps> = ({
  project,
  onArchive,
  onDelete,
  getVisibilityIcon,
  getStatusBadge
}) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <div className="bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg p-4 hover:border-[#ffd400] transition-colors">
      <div className="flex items-center gap-4">
        <a href={`/projects/${project.id}`} className="flex-1">
          <h3 className="text-lg font-semibold hover:text-[#ffd400] transition-colors">
            {project.name}
          </h3>
          <p className="text-[#909094] text-sm mt-1">{project.description || 'No description'}</p>
        </a>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            {getVisibilityIcon(project.visibility)}
            <span className="text-sm text-[#909094] capitalize">{project.visibility}</span>
          </div>

          <div>{getStatusBadge(project.status)}</div>

          <div className="text-sm text-[#909094]">
            <span className="font-medium text-[#fbfbff]">{project.task_count || 0}</span> tasks
          </div>

          <div className="text-sm text-[#909094]">
            <span className="font-medium text-[#fbfbff]">{project.member_count || 0}</span> members
          </div>

          <div className="text-sm text-[#909094]">
            {new Date(project.updated_at).toLocaleDateString()}
          </div>

          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-1 hover:bg-[#3a3a3e] rounded"
            >
              <MoreVertical className="w-5 h-5" />
            </button>
            {showMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-[#2a2a2e] border border-[#3a3a3e] rounded-lg shadow-lg z-10">
                <button
                  onClick={() => {
                    onArchive(project.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-[#3a3a3e] flex items-center gap-2"
                >
                  <Archive className="w-4 h-4" />
                  Archive
                </button>
                <button
                  onClick={() => {
                    onDelete(project.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-[#3a3a3e] text-red-500 flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
""";

print("✅ Project UI Components - List Page Created")
print("\nComponents:")
print("  • ProjectListPage - Main list view with grid/list toggle")
print("  • ProjectCard - Card view for grid layout")
print("  • ProjectListItem - Row view for list layout")
print("  • Search and filtering (by status, name)")
print("  • Status badges with Zerve design system colors")
print("  • Visibility indicators (private/team/org)")
print("  • Quick actions menu (archive/delete)")
print("  • Create project button and modal")
