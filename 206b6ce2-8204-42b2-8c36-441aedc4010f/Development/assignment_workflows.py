"""
Assignment Workflows and Related UI Components
Includes assignment modal, bulk actions, and team member selection
"""

assignment_modal = """
import React, { useState } from 'react';
import { X, User, Calendar, Clock, Tag, AlertCircle } from 'lucide-react';

interface Member {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: string;
  workload?: number; // Number of active tasks
}

interface AssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  taskIds: string[]; // Support single or bulk assignment
  currentAssignees?: string[]; // Current assignee(s) if editing
  members: Member[];
  onAssign: (taskIds: string[], assigneeId: string, metadata?: any) => void;
}

export const AssignmentModal: React.FC<AssignmentModalProps> = ({
  isOpen,
  onClose,
  taskIds,
  currentAssignees = [],
  members,
  onAssign
}) => {
  const [selectedMember, setSelectedMember] = useState<string>(currentAssignees[0] || '');
  const [dueDate, setDueDate] = useState('');
  const [estimatedHours, setEstimatedHours] = useState('');
  const [priority, setPriority] = useState('medium');
  const [notes, setNotes] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  if (!isOpen) return null;

  const filteredMembers = members.filter(member =>
    member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    member.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sortedMembers = [...filteredMembers].sort((a, b) => {
    // Sort by workload (ascending) then name
    if (a.workload !== b.workload) {
      return (a.workload || 0) - (b.workload || 0);
    }
    return a.name.localeCompare(b.name);
  });

  const handleAssign = () => {
    if (!selectedMember) return;

    const metadata = {
      due_date: dueDate || undefined,
      estimated_hours: estimatedHours ? parseFloat(estimatedHours) : undefined,
      priority: priority,
      assignment_notes: notes || undefined
    };

    onAssign(taskIds, selectedMember, metadata);
    onClose();
  };

  const isBulk = taskIds.length > 1;
  const selectedMemberData = members.find(m => m.id === selectedMember);

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
        borderRadius: '12px',
        maxWidth: '600px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'hidden',
        border: '1px solid #2D2D30'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #2D2D30',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h2 style={{
              margin: '0 0 4px 0',
              color: '#fbfbff',
              fontSize: '18px',
              fontWeight: 600
            }}>
              {isBulk ? `Assign ${taskIds.length} Tasks` : 'Assign Task'}
            </h2>
            <p style={{
              margin: 0,
              color: '#909094',
              fontSize: '13px'
            }}>
              Choose a team member and set task details
            </p>
          </div>
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

        {/* Content */}
        <div style={{
          padding: '24px',
          overflowY: 'auto',
          maxHeight: 'calc(90vh - 160px)'
        }}>
          {/* Search Members */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              color: '#909094',
              fontSize: '12px',
              marginBottom: '8px',
              fontWeight: 600
            }}>
              Assign To *
            </label>
            <input
              type="text"
              placeholder="Search members..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: '#2D2D30',
                border: '1px solid #3D3D40',
                borderRadius: '8px',
                color: '#fbfbff',
                fontSize: '14px',
                marginBottom: '12px'
              }}
            />

            {/* Member List */}
            <div style={{
              maxHeight: '250px',
              overflowY: 'auto',
              border: '1px solid #2D2D30',
              borderRadius: '8px',
              backgroundColor: '#1A1A1D'
            }}>
              {sortedMembers.map(member => (
                <div
                  key={member.id}
                  onClick={() => setSelectedMember(member.id)}
                  style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid #2D2D30',
                    cursor: 'pointer',
                    backgroundColor: selectedMember === member.id ? '#2D2D30' : 'transparent',
                    transition: 'background-color 0.2s',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedMember !== member.id) {
                      e.currentTarget.style.backgroundColor = '#252528';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedMember !== member.id) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  {/* Avatar */}
                  {member.avatar ? (
                    <img
                      src={member.avatar}
                      alt={member.name}
                      style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '50%',
                        border: '2px solid #3D3D40'
                      }}
                    />
                  ) : (
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      backgroundColor: '#3D3D40',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fbfbff',
                      fontSize: '14px',
                      fontWeight: 600
                    }}>
                      {member.name.charAt(0).toUpperCase()}
                    </div>
                  )}

                  {/* Info */}
                  <div style={{ flex: 1 }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      marginBottom: '2px'
                    }}>
                      <span style={{
                        color: '#fbfbff',
                        fontSize: '14px',
                        fontWeight: 500
                      }}>
                        {member.name}
                      </span>
                      <span style={{
                        padding: '2px 6px',
                        backgroundColor: '#2D2D30',
                        borderRadius: '4px',
                        color: '#909094',
                        fontSize: '10px',
                        fontWeight: 500
                      }}>
                        {member.role}
                      </span>
                    </div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}>
                      <span style={{
                        color: '#909094',
                        fontSize: '12px'
                      }}>
                        {member.email}
                      </span>
                      {member.workload !== undefined && (
                        <span style={{
                          color: member.workload > 10 ? '#f04438' : '#909094',
                          fontSize: '11px',
                          fontWeight: 500
                        }}>
                          {member.workload} active tasks
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Selected Indicator */}
                  {selectedMember === member.id && (
                    <div style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      backgroundColor: '#ffd400',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#1D1D20',
                      fontSize: '12px',
                      fontWeight: 700
                    }}>
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Additional Details */}
          {selectedMember && (
            <div style={{
              padding: '16px',
              backgroundColor: '#2D2D30',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <h4 style={{
                margin: '0 0 12px 0',
                color: '#fbfbff',
                fontSize: '13px',
                fontWeight: 600
              }}>
                Assignment Details (Optional)
              </h4>

              {/* Due Date */}
              <div style={{ marginBottom: '12px' }}>
                <label style={{
                  display: 'block',
                  color: '#909094',
                  fontSize: '11px',
                  marginBottom: '6px'
                }}>
                  <Calendar size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Due Date
                </label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#1D1D20',
                    border: '1px solid #3D3D40',
                    borderRadius: '6px',
                    color: '#fbfbff',
                    fontSize: '13px'
                  }}
                />
              </div>

              {/* Estimated Hours */}
              <div style={{ marginBottom: '12px' }}>
                <label style={{
                  display: 'block',
                  color: '#909094',
                  fontSize: '11px',
                  marginBottom: '6px'
                }}>
                  <Clock size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Estimated Hours
                </label>
                <input
                  type="number"
                  value={estimatedHours}
                  onChange={(e) => setEstimatedHours(e.target.value)}
                  placeholder="8"
                  min="0"
                  step="0.5"
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#1D1D20',
                    border: '1px solid #3D3D40',
                    borderRadius: '6px',
                    color: '#fbfbff',
                    fontSize: '13px'
                  }}
                />
              </div>

              {/* Priority */}
              {!isBulk && (
                <div style={{ marginBottom: '12px' }}>
                  <label style={{
                    display: 'block',
                    color: '#909094',
                    fontSize: '11px',
                    marginBottom: '6px'
                  }}>
                    Priority
                  </label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px',
                      backgroundColor: '#1D1D20',
                      border: '1px solid #3D3D40',
                      borderRadius: '6px',
                      color: '#fbfbff',
                      fontSize: '13px'
                    }}
                  >
                    <option value="low">🟢 Low</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="high">🟠 High</option>
                    <option value="critical">🔴 Critical</option>
                  </select>
                </div>
              )}

              {/* Notes */}
              <div>
                <label style={{
                  display: 'block',
                  color: '#909094',
                  fontSize: '11px',
                  marginBottom: '6px'
                }}>
                  Notes
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add any context or instructions..."
                  style={{
                    width: '100%',
                    minHeight: '60px',
                    padding: '8px',
                    backgroundColor: '#1D1D20',
                    border: '1px solid #3D3D40',
                    borderRadius: '6px',
                    color: '#fbfbff',
                    fontSize: '13px',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>
            </div>
          )}

          {/* Workload Warning */}
          {selectedMemberData && selectedMemberData.workload && selectedMemberData.workload > 10 && (
            <div style={{
              padding: '12px',
              backgroundColor: '#f04438' + '20',
              border: '1px solid #f04438',
              borderRadius: '8px',
              display: 'flex',
              gap: '10px',
              alignItems: 'flex-start',
              marginBottom: '20px'
            }}>
              <AlertCircle size={16} style={{ color: '#f04438', marginTop: '2px' }} />
              <div>
                <p style={{
                  margin: '0 0 4px 0',
                  color: '#f04438',
                  fontSize: '12px',
                  fontWeight: 600
                }}>
                  High Workload
                </p>
                <p style={{
                  margin: 0,
                  color: '#f04438',
                  fontSize: '11px',
                  lineHeight: '1.4'
                }}>
                  {selectedMemberData.name} currently has {selectedMemberData.workload} active tasks. 
                  Consider distributing work to other team members.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid #2D2D30',
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 20px',
              backgroundColor: 'transparent',
              border: '1px solid #3D3D40',
              borderRadius: '8px',
              color: '#fbfbff',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleAssign}
            disabled={!selectedMember}
            style={{
              padding: '10px 24px',
              backgroundColor: selectedMember ? '#ffd400' : '#3D3D40',
              border: 'none',
              borderRadius: '8px',
              color: selectedMember ? '#1D1D20' : '#909094',
              cursor: selectedMember ? 'pointer' : 'not-allowed',
              fontSize: '14px',
              fontWeight: 600
            }}
          >
            {isBulk ? `Assign ${taskIds.length} Tasks` : 'Assign Task'}
          </button>
        </div>
      </div>
    </div>
  );
};
"""

bulk_actions_toolbar = """
import React from 'react';
import { User, Trash2, Tag, Calendar, X, CheckSquare } from 'lucide-react';

interface BulkActionsToolbarProps {
  selectedCount: number;
  onAssign: () => void;
  onDelete: () => void;
  onUpdateStatus: (status: string) => void;
  onUpdatePriority: (priority: string) => void;
  onClearSelection: () => void;
}

export const BulkActionsToolbar: React.FC<BulkActionsToolbarProps> = ({
  selectedCount,
  onAssign,
  onDelete,
  onUpdateStatus,
  onUpdatePriority,
  onClearSelection
}) => {
  if (selectedCount === 0) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      left: '50%',
      transform: 'translateX(-50%)',
      backgroundColor: '#1D1D20',
      border: '2px solid #ffd400',
      borderRadius: '12px',
      padding: '16px 24px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      zIndex: 100
    }}>
      {/* Selection Info */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        paddingRight: '16px',
        borderRight: '1px solid #3D3D40'
      }}>
        <CheckSquare size={18} style={{ color: '#ffd400' }} />
        <span style={{
          color: '#fbfbff',
          fontSize: '14px',
          fontWeight: 600
        }}>
          {selectedCount} task{selectedCount !== 1 ? 's' : ''} selected
        </span>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '8px' }}>
        {/* Assign */}
        <button
          onClick={onAssign}
          style={{
            padding: '8px 16px',
            backgroundColor: '#2D2D30',
            border: '1px solid #3D3D40',
            borderRadius: '6px',
            color: '#fbfbff',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            fontWeight: 500
          }}
        >
          <User size={14} />
          Assign
        </button>

        {/* Status Dropdown */}
        <select
          onChange={(e) => {
            if (e.target.value) {
              onUpdateStatus(e.target.value);
              e.target.value = '';
            }
          }}
          style={{
            padding: '8px 12px',
            backgroundColor: '#2D2D30',
            border: '1px solid #3D3D40',
            borderRadius: '6px',
            color: '#fbfbff',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          <option value="">Set Status</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="completed">Completed</option>
          <option value="blocked">Blocked</option>
        </select>

        {/* Priority Dropdown */}
        <select
          onChange={(e) => {
            if (e.target.value) {
              onUpdatePriority(e.target.value);
              e.target.value = '';
            }
          }}
          style={{
            padding: '8px 12px',
            backgroundColor: '#2D2D30',
            border: '1px solid #3D3D40',
            borderRadius: '6px',
            color: '#fbfbff',
            cursor: 'pointer',
            fontSize: '13px'
          }}
        >
          <option value="">Set Priority</option>
          <option value="low">🟢 Low</option>
          <option value="medium">🟡 Medium</option>
          <option value="high">🟠 High</option>
          <option value="critical">🔴 Critical</option>
        </select>

        {/* Delete */}
        <button
          onClick={onDelete}
          style={{
            padding: '8px 16px',
            backgroundColor: 'transparent',
            border: '1px solid #f04438',
            borderRadius: '6px',
            color: '#f04438',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            fontWeight: 500
          }}
        >
          <Trash2 size={14} />
          Delete
        </button>
      </div>

      {/* Clear Selection */}
      <button
        onClick={onClearSelection}
        style={{
          padding: '8px',
          backgroundColor: 'transparent',
          border: 'none',
          color: '#909094',
          cursor: 'pointer',
          marginLeft: '8px',
          borderLeft: '1px solid #3D3D40',
          paddingLeft: '16px'
        }}
      >
        <X size={18} />
      </button>
    </div>
  );
};
"""

print("✅ Assignment Workflows created")
print("\nComponents:")
print("  • AssignmentModal - Assign tasks with member selection and details")
print("  • BulkActionsToolbar - Multi-select actions for tasks")
print("\nFeatures:")
print("  • Smart member sorting by workload")
print("  • Workload warnings for overloaded members")
print("  • Bulk assignment with metadata")
print("  • Status and priority bulk updates")
print("\nExported: assignment_modal, bulk_actions_toolbar")
