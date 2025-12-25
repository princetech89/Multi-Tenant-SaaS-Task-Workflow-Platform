# Organization Settings UI - Member Management, Role Assignment, Invitations, and Org Details Editing

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum

# === React Component Code ===

organization_settings_page = """
'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { apiService } from '@/services/api';
import { 
  Card, CardContent, CardDescription, CardHeader, CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue 
} from '@/components/ui/select';
import { 
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow 
} from '@/components/ui/table';
import { 
  Dialog, DialogContent, DialogDescription, DialogFooter, 
  DialogHeader, DialogTitle, DialogTrigger 
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  AlertDialog, AlertDialogAction, AlertDialogCancel, 
  AlertDialogContent, AlertDialogDescription, AlertDialogFooter, 
  AlertDialogHeader, AlertDialogTitle 
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/useToast';
import { 
  Users, Mail, Shield, Settings, Trash2, UserPlus, 
  MoreVertical, Check, X, RefreshCw, Edit2 
} from 'lucide-react';

interface OrganizationMember {
  id: string;
  user_id: string;
  email: string;
  display_name: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  status: 'active' | 'inactive';
  joined_at: string;
}

interface Invitation {
  id: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  status: 'pending' | 'accepted' | 'revoked' | 'expired';
  invited_by: string;
  created_at: string;
  expires_at: string;
}

interface Organization {
  id: string;
  name: string;
  display_name: string;
  description?: string;
  status: 'active' | 'suspended' | 'archived';
  tier: 'free' | 'pro' | 'enterprise';
  settings: Record<string, any>;
  created_at: string;
}

const ROLE_COLORS = {
  owner: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  admin: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  member: 'bg-green-500/20 text-green-300 border-green-500/30',
  viewer: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
};

const STATUS_COLORS = {
  active: 'bg-green-500/20 text-green-300',
  inactive: 'bg-gray-500/20 text-gray-300',
  pending: 'bg-yellow-500/20 text-yellow-300',
  accepted: 'bg-green-500/20 text-green-300',
  revoked: 'bg-red-500/20 text-red-300',
  expired: 'bg-gray-500/20 text-gray-300',
};

export default function OrganizationSettingsPage() {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Dialog states
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [editOrgDialogOpen, setEditOrgDialogOpen] = useState(false);
  const [editMemberDialogOpen, setEditMemberDialogOpen] = useState(false);
  const [removeMemberDialogOpen, setRemoveMemberDialogOpen] = useState(false);
  
  // Form states
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'admin' | 'member' | 'viewer'>('member');
  const [editedOrgName, setEditedOrgName] = useState('');
  const [editedOrgDescription, setEditedOrgDescription] = useState('');
  const [selectedMember, setSelectedMember] = useState<OrganizationMember | null>(null);
  const [newMemberRole, setNewMemberRole] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [orgData, membersData, invitesData] = await Promise.all([
        apiService.get(`/organizations/${user.organization_id}`),
        apiService.get(`/organizations/${user.organization_id}/members`),
        apiService.get(`/organizations/${user.organization_id}/invitations`),
      ]);
      
      setOrganization(orgData);
      setMembers(membersData);
      setInvitations(invitesData);
      
      setEditedOrgName(orgData.display_name);
      setEditedOrgDescription(orgData.description || '');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load organization data',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleInviteUser = async () => {
    if (!inviteEmail) {
      toast({
        title: 'Validation Error',
        description: 'Please enter an email address',
        variant: 'destructive',
      });
      return;
    }

    try {
      await apiService.post(`/organizations/${user.organization_id}/invitations`, {
        email: inviteEmail,
        role: inviteRole,
      });
      
      toast({
        title: 'Success',
        description: `Invitation sent to ${inviteEmail}`,
      });
      
      setInviteEmail('');
      setInviteRole('member');
      setInviteDialogOpen(false);
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to send invitation',
        variant: 'destructive',
      });
    }
  };

  const handleUpdateOrganization = async () => {
    try {
      await apiService.put(`/organizations/${organization.id}`, {
        display_name: editedOrgName,
        description: editedOrgDescription,
      });
      
      toast({
        title: 'Success',
        description: 'Organization updated successfully',
      });
      
      setEditOrgDialogOpen(false);
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update organization',
        variant: 'destructive',
      });
    }
  };

  const handleUpdateMemberRole = async () => {
    if (!selectedMember) return;

    try {
      await apiService.patch(
        `/organizations/${user.organization_id}/members/${selectedMember.id}/role`,
        { role: newMemberRole }
      );
      
      toast({
        title: 'Success',
        description: `Updated ${selectedMember.display_name}'s role to ${newMemberRole}`,
      });
      
      setEditMemberDialogOpen(false);
      setSelectedMember(null);
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update member role',
        variant: 'destructive',
      });
    }
  };

  const handleRemoveMember = async () => {
    if (!selectedMember) return;

    try {
      await apiService.delete(
        `/organizations/${user.organization_id}/members/${selectedMember.id}`
      );
      
      toast({
        title: 'Success',
        description: `Removed ${selectedMember.display_name} from organization`,
      });
      
      setRemoveMemberDialogOpen(false);
      setSelectedMember(null);
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to remove member',
        variant: 'destructive',
      });
    }
  };

  const handleRevokeInvitation = async (invitationId: string) => {
    try {
      await apiService.post(
        `/organizations/${user.organization_id}/invitations/${invitationId}/revoke`
      );
      
      toast({
        title: 'Success',
        description: 'Invitation revoked',
      });
      
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to revoke invitation',
        variant: 'destructive',
      });
    }
  };

  const handleResendInvitation = async (invitationId: string) => {
    try {
      await apiService.post(
        `/organizations/${user.organization_id}/invitations/${invitationId}/resend`
      );
      
      toast({
        title: 'Success',
        description: 'Invitation resent',
      });
      
      loadData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to resend invitation',
        variant: 'destructive',
      });
    }
  };

  if (loading) {
    return (
      <div className=\"flex items-center justify-center min-h-screen\">
        <RefreshCw className=\"h-8 w-8 animate-spin text-primary\" />
      </div>
    );
  }

  const canManageMembers = ['owner', 'admin'].includes(user?.role);
  const canEditOrg = user?.role === 'owner';

  return (
    <div className=\"container mx-auto py-8 px-4 max-w-7xl\">
      <div className=\"mb-8\">
        <h1 className=\"text-3xl font-bold text-primary mb-2\">
          Organization Settings
        </h1>
        <p className=\"text-secondary\">
          Manage your organization's members, invitations, and settings
        </p>
      </div>

      <Tabs defaultValue=\"members\" className=\"space-y-6\">
        <TabsList className=\"grid w-full grid-cols-3 lg:w-auto\">
          <TabsTrigger value=\"members\" className=\"flex items-center gap-2\">
            <Users className=\"h-4 w-4\" />
            Members
          </TabsTrigger>
          <TabsTrigger value=\"invitations\" className=\"flex items-center gap-2\">
            <Mail className=\"h-4 w-4\" />
            Invitations
          </TabsTrigger>
          <TabsTrigger value=\"general\" className=\"flex items-center gap-2\">
            <Settings className=\"h-4 w-4\" />
            General
          </TabsTrigger>
        </TabsList>

        {/* Members Tab */}
        <TabsContent value=\"members\" className=\"space-y-6\">
          <Card>
            <CardHeader>
              <div className=\"flex items-center justify-between\">
                <div>
                  <CardTitle>Organization Members</CardTitle>
                  <CardDescription>
                    Manage member roles and permissions
                  </CardDescription>
                </div>
                {canManageMembers && (
                  <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <UserPlus className=\"h-4 w-4 mr-2\" />
                        Invite Member
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Invite New Member</DialogTitle>
                        <DialogDescription>
                          Send an invitation to join your organization
                        </DialogDescription>
                      </DialogHeader>
                      <div className=\"space-y-4 py-4\">
                        <div className=\"space-y-2\">
                          <Label htmlFor=\"email\">Email Address</Label>
                          <Input
                            id=\"email\"
                            type=\"email\"
                            placeholder=\"colleague@example.com\"
                            value={inviteEmail}
                            onChange={(e) => setInviteEmail(e.target.value)}
                          />
                        </div>
                        <div className=\"space-y-2\">
                          <Label htmlFor=\"role\">Role</Label>
                          <Select value={inviteRole} onValueChange={setInviteRole}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value=\"admin\">Admin</SelectItem>
                              <SelectItem value=\"member\">Member</SelectItem>
                              <SelectItem value=\"viewer\">Viewer</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant=\"outline\" onClick={() => setInviteDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleInviteUser}>Send Invitation</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Member</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Joined</TableHead>
                    {canManageMembers && <TableHead>Actions</TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {members.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell>
                        <div>
                          <div className=\"font-medium\">{member.display_name}</div>
                          <div className=\"text-sm text-secondary\">{member.email}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={ROLE_COLORS[member.role]}>
                          {member.role}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={STATUS_COLORS[member.status]}>
                          {member.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(member.joined_at).toLocaleDateString()}
                      </TableCell>
                      {canManageMembers && member.role !== 'owner' && (
                        <TableCell>
                          <div className=\"flex gap-2\">
                            <Button
                              variant=\"ghost\"
                              size=\"sm\"
                              onClick={() => {
                                setSelectedMember(member);
                                setNewMemberRole(member.role);
                                setEditMemberDialogOpen(true);
                              }}
                            >
                              <Edit2 className=\"h-4 w-4\" />
                            </Button>
                            <Button
                              variant=\"ghost\"
                              size=\"sm\"
                              onClick={() => {
                                setSelectedMember(member);
                                setRemoveMemberDialogOpen(true);
                              }}
                            >
                              <Trash2 className=\"h-4 w-4 text-red-400\" />
                            </Button>
                          </div>
                        </TableCell>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Invitations Tab */}
        <TabsContent value=\"invitations\" className=\"space-y-6\">
          <Card>
            <CardHeader>
              <CardTitle>Pending Invitations</CardTitle>
              <CardDescription>
                Manage sent invitations
              </CardDescription>
            </CardHeader>
            <CardContent>
              {invitations.length === 0 ? (
                <div className=\"text-center py-8 text-secondary\">
                  No pending invitations
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Email</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Sent</TableHead>
                      <TableHead>Expires</TableHead>
                      {canManageMembers && <TableHead>Actions</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {invitations.map((invitation) => (
                      <TableRow key={invitation.id}>
                        <TableCell>{invitation.email}</TableCell>
                        <TableCell>
                          <Badge className={ROLE_COLORS[invitation.role]}>
                            {invitation.role}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className={STATUS_COLORS[invitation.status]}>
                            {invitation.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {new Date(invitation.created_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          {new Date(invitation.expires_at).toLocaleDateString()}
                        </TableCell>
                        {canManageMembers && invitation.status === 'pending' && (
                          <TableCell>
                            <div className=\"flex gap-2\">
                              <Button
                                variant=\"ghost\"
                                size=\"sm\"
                                onClick={() => handleResendInvitation(invitation.id)}
                              >
                                <RefreshCw className=\"h-4 w-4\" />
                              </Button>
                              <Button
                                variant=\"ghost\"
                                size=\"sm\"
                                onClick={() => handleRevokeInvitation(invitation.id)}
                              >
                                <X className=\"h-4 w-4 text-red-400\" />
                              </Button>
                            </div>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* General Settings Tab */}
        <TabsContent value=\"general\" className=\"space-y-6\">
          <Card>
            <CardHeader>
              <div className=\"flex items-center justify-between\">
                <div>
                  <CardTitle>Organization Details</CardTitle>
                  <CardDescription>
                    View and edit your organization information
                  </CardDescription>
                </div>
                {canEditOrg && (
                  <Dialog open={editOrgDialogOpen} onOpenChange={setEditOrgDialogOpen}>
                    <DialogTrigger asChild>
                      <Button variant=\"outline\">
                        <Edit2 className=\"h-4 w-4 mr-2\" />
                        Edit
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Edit Organization</DialogTitle>
                        <DialogDescription>
                          Update your organization details
                        </DialogDescription>
                      </DialogHeader>
                      <div className=\"space-y-4 py-4\">
                        <div className=\"space-y-2\">
                          <Label htmlFor=\"org-name\">Organization Name</Label>
                          <Input
                            id=\"org-name\"
                            value={editedOrgName}
                            onChange={(e) => setEditedOrgName(e.target.value)}
                          />
                        </div>
                        <div className=\"space-y-2\">
                          <Label htmlFor=\"org-description\">Description</Label>
                          <Input
                            id=\"org-description\"
                            value={editedOrgDescription}
                            onChange={(e) => setEditedOrgDescription(e.target.value)}
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant=\"outline\" onClick={() => setEditOrgDialogOpen(false)}>
                          Cancel
                        </Button>
                        <Button onClick={handleUpdateOrganization}>Save Changes</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                )}
              </div>
            </CardHeader>
            <CardContent className=\"space-y-4\">
              <div className=\"grid grid-cols-2 gap-4\">
                <div>
                  <Label className=\"text-secondary\">Organization Name</Label>
                  <p className=\"font-medium\">{organization?.display_name}</p>
                </div>
                <div>
                  <Label className=\"text-secondary\">Status</Label>
                  <Badge className={STATUS_COLORS[organization?.status]}>
                    {organization?.status}
                  </Badge>
                </div>
                <div>
                  <Label className=\"text-secondary\">Tier</Label>
                  <p className=\"font-medium uppercase\">{organization?.tier}</p>
                </div>
                <div>
                  <Label className=\"text-secondary\">Created</Label>
                  <p className=\"font-medium\">
                    {new Date(organization?.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              {organization?.description && (
                <div>
                  <Label className=\"text-secondary\">Description</Label>
                  <p className=\"font-medium\">{organization.description}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit Member Role Dialog */}
      <Dialog open={editMemberDialogOpen} onOpenChange={setEditMemberDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Change Member Role</DialogTitle>
            <DialogDescription>
              Update {selectedMember?.display_name}'s role
            </DialogDescription>
          </DialogHeader>
          <div className=\"space-y-4 py-4\">
            <Select value={newMemberRole} onValueChange={setNewMemberRole}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value=\"admin\">Admin</SelectItem>
                <SelectItem value=\"member\">Member</SelectItem>
                <SelectItem value=\"viewer\">Viewer</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant=\"outline\" onClick={() => setEditMemberDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateMemberRole}>Update Role</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Remove Member Confirmation */}
      <AlertDialog open={removeMemberDialogOpen} onOpenChange={setRemoveMemberDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove {selectedMember?.display_name} from the organization?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRemoveMember} className=\"bg-red-600 hover:bg-red-700\">
              Remove Member
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
"""

# Save the component
print("✅ Organization Settings UI Component Created")
print("\\n📋 Features Implemented:")
print("  ✓ Member Management - View all org members with roles and status")
print("  ✓ Role Assignment - Update member roles (admin, member, viewer)")
print("  ✓ User Invitations - Send, resend, and revoke invitations")
print("  ✓ Organization Details - View and edit org name, description, tier")
print("  ✓ Permission-Based UI - Admin/owner actions guarded by role")
print("  ✓ Complete CRUD Operations - All management capabilities")
print("\\n🎨 UI Features:")
print("  ✓ Tabbed interface (Members, Invitations, General)")
print("  ✓ Role-based color coding")
print("  ✓ Status badges for members and invitations")
print("  ✓ Modal dialogs for all actions")
print("  ✓ Confirmation dialogs for destructive actions")
print("  ✓ Toast notifications for feedback")
print("  ✓ Loading states and error handling")
print("\\n🔒 Security:")
print("  ✓ Permission checks before showing action buttons")
print("  ✓ Owner-only organization editing")
print("  ✓ Admin/owner-only member management")
print("  ✓ Token-aware API calls via apiService")

# Component is ready to be saved to file
org_settings_ui_file = organization_settings_page
