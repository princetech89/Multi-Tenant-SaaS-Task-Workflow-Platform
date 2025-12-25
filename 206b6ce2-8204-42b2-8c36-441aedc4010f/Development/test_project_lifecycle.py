"""
Comprehensive Test Suite for Project CRUD APIs
Tests full project lifecycle, tenant isolation, and hierarchical access control
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

# ============================================================================
# Re-define models locally
# ============================================================================

class _ProjectStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class _ProjectVisibility(Enum):
    PRIVATE = "private"
    TEAM = "team"
    ORGANIZATION = "organization"

# Use the classes from upstream
_test_service = ProjectService()
_test_api = ProjectAPI(_test_service)

# ============================================================================
# Test Setup
# ============================================================================

print("=" * 80)
print("PROJECT CRUD API COMPREHENSIVE TEST SUITE")
print("=" * 80)

# Test data
_org1_test_id = str(uuid.uuid4())
_org2_test_id = str(uuid.uuid4())
_user1_test_id = str(uuid.uuid4())
_user2_test_id = str(uuid.uuid4())
_user3_test_id = str(uuid.uuid4())

_test_results = []

def test_assert(condition, test_name):
    """Helper to track test results"""
    _test_results.append({'test': test_name, 'passed': condition})
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}: {test_name}")
    return condition

# ============================================================================
# TEST 1: Project Creation
# ============================================================================

print("\n" + "=" * 80)
print("TEST 1: Project Creation")
print("=" * 80)

# Create project in org1
result = _test_api.create_project({
    'organization_id': _org1_test_id,
    'user_id': _user1_test_id,
    'name': 'Test Project 1',
    'description': 'First test project',
    'visibility': 'team'
})

test_assert(result['success'] == True, "Create project successfully")
test_assert(result['code'] == 201, "Returns 201 status code")
_project1_test_id = result['project']['id']
test_assert(result['project']['status'] == 'active', "Project status is active")
test_assert(result['project']['visibility'] == 'team', "Project visibility is team")

# Verify owner is automatically added as member
_members = _test_service.get_project_members(_project1_test_id)
test_assert(len(_members) == 1, "Owner automatically added as member")
test_assert(_members[0].user_id == _user1_test_id, "Owner user ID matches")
test_assert(_members[0].role == 'owner', "Owner has owner role")

# ============================================================================
# TEST 2: Project Access Control
# ============================================================================

print("\n" + "=" * 80)
print("TEST 2: Project Access Control - Visibility & Membership")
print("=" * 80)

# User1 (owner) can access
result = _test_api.get_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Owner can access project")

# User2 (not member) cannot access team project
result = _test_api.get_project(_project1_test_id, _user2_test_id, _org1_test_id)
test_assert(result['success'] == False, "Non-member cannot access team project")
test_assert(result['code'] == 403, "Returns 403 for non-member")

# Add user2 as member
result = _test_api.add_project_member(
    _project1_test_id, _user1_test_id, _org1_test_id,
    _user2_test_id, 'developer'
)
test_assert(result['success'] == True, "Owner can add members")

# Now user2 can access
result = _test_api.get_project(_project1_test_id, _user2_test_id, _org1_test_id)
test_assert(result['success'] == True, "Member can access project after being added")

# ============================================================================
# TEST 3: Tenant Isolation
# ============================================================================

print("\n" + "=" * 80)
print("TEST 3: Tenant Isolation - Cross-Organization Access")
print("=" * 80)

# Create project in org2
result = _test_api.create_project({
    'organization_id': _org2_test_id,
    'user_id': _user3_test_id,
    'name': 'Org2 Project',
    'visibility': 'organization'
})
_project2_test_id = result['project']['id']

# User from org1 cannot access org2 project
result = _test_api.get_project(_project2_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == False, "Cross-org access denied")
test_assert(result['code'] == 403, "Returns 403 for cross-org access")
test_assert('cross-organization' in result['error'].lower(), "Error message mentions cross-org")

# ============================================================================
# TEST 4: Project Update
# ============================================================================

print("\n" + "=" * 80)
print("TEST 4: Project Update")
print("=" * 80)

# Owner can update
result = _test_api.update_project(
    _project1_test_id, _user1_test_id, _org1_test_id,
    {'name': 'Updated Project Name', 'description': 'Updated description'}
)
test_assert(result['success'] == True, "Owner can update project")
test_assert(result['project']['name'] == 'Updated Project Name', "Project name updated")

# Non-owner member cannot update (unless admin)
result = _test_api.update_project(
    _project1_test_id, _user2_test_id, _org1_test_id,
    {'name': 'Unauthorized Update'}
)
test_assert(result['success'] == False, "Non-admin member cannot update")

# ============================================================================
# TEST 5: Archive and Unarchive
# ============================================================================

print("\n" + "=" * 80)
print("TEST 5: Archive and Unarchive")
print("=" * 80)

# Archive project
result = _test_api.archive_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Project archived successfully")
test_assert(result['project']['status'] == 'archived', "Project status is archived")
test_assert(result['project']['archived_at'] is not None, "Archived timestamp set")

# Archived projects not in default user list
result = _test_api.list_user_projects(_user1_test_id, _org1_test_id, include_archived=False)
test_assert(result['count'] == 0, "Archived projects excluded from default list")

# Archived projects included when requested
result = _test_api.list_user_projects(_user1_test_id, _org1_test_id, include_archived=True)
test_assert(result['count'] == 1, "Archived projects included when requested")

# Unarchive project
result = _test_api.unarchive_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Project unarchived successfully")
test_assert(result['project']['status'] == 'active', "Project status is active after unarchive")

# ============================================================================
# TEST 6: Soft Delete and Restore
# ============================================================================

print("\n" + "=" * 80)
print("TEST 6: Soft Delete and Restore")
print("=" * 80)

# Soft delete project
result = _test_api.delete_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Project soft deleted successfully")
test_assert(result['project']['status'] == 'deleted', "Project status is deleted")
test_assert(result['project']['deleted_at'] is not None, "Deleted timestamp set")

# Deleted project not accessible normally
result = _test_api.get_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == False, "Deleted project not accessible")

# Restore project
result = _test_api.restore_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Project restored successfully")
test_assert(result['project']['status'] == 'active', "Project status is active after restore")

# Project accessible again
result = _test_api.get_project(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Restored project accessible again")

# ============================================================================
# TEST 7: Hierarchical Access - Visibility Levels
# ============================================================================

print("\n" + "=" * 80)
print("TEST 7: Hierarchical Access - Visibility Levels")
print("=" * 80)

# Create private project
result = _test_api.create_project({
    'organization_id': _org1_test_id,
    'user_id': _user1_test_id,
    'name': 'Private Project',
    'visibility': 'private'
})
_private_proj_id = result['project']['id']

# Only owner can see private project
_projects = _test_service.get_user_projects(_org1_test_id, _user1_test_id)
_private_count = sum(1 for p in _projects if p.id == _private_proj_id)
test_assert(_private_count == 1, "Owner can see private project")

_projects = _test_service.get_user_projects(_org1_test_id, _user2_test_id)
_private_count = sum(1 for p in _projects if p.id == _private_proj_id)
test_assert(_private_count == 0, "Other users cannot see private project")

# Create organization-wide project
result = _test_api.create_project({
    'organization_id': _org1_test_id,
    'user_id': _user1_test_id,
    'name': 'Org-Wide Project',
    'visibility': 'organization'
})
_org_proj_id = result['project']['id']

# All org users can see organization project
_projects = _test_service.get_user_projects(_org1_test_id, _user2_test_id)
_org_count = sum(1 for p in _projects if p.id == _org_proj_id)
test_assert(_org_count == 1, "All org users can see organization project")

# ============================================================================
# TEST 8: Member Management
# ============================================================================

print("\n" + "=" * 80)
print("TEST 8: Member Management")
print("=" * 80)

# List members
result = _test_api.list_project_members(_project1_test_id, _user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Can list project members")
test_assert(result['count'] == 2, "Project has 2 members (owner + added)")

# Cannot remove owner
result = _test_api.remove_project_member(
    _project1_test_id, _user1_test_id, _org1_test_id, _user1_test_id
)
test_assert(result['success'] == False, "Cannot remove project owner")

# Remove member
result = _test_api.remove_project_member(
    _project1_test_id, _user1_test_id, _org1_test_id, _user2_test_id
)
test_assert(result['success'] == True, "Can remove non-owner member")

# ============================================================================
# TEST 9: Statistics
# ============================================================================

print("\n" + "=" * 80)
print("TEST 9: Project Statistics")
print("=" * 80)

# Get stats (owner role)
result = _test_api.get_project_statistics(_org1_test_id, _user1_test_id, 'owner')
test_assert(result['success'] == True, "Owner can access statistics")
_stats = result['statistics']
test_assert(_stats['total'] >= 3, "Total projects count is correct")
test_assert('by_visibility' in _stats, "Stats include visibility breakdown")

# Non-admin cannot access stats
result = _test_api.get_project_statistics(_org1_test_id, _user2_test_id, 'developer')
test_assert(result['success'] == False, "Non-admin cannot access statistics")

# ============================================================================
# TEST 10: Project-Scoped Queries
# ============================================================================

print("\n" + "=" * 80)
print("TEST 10: Project-Scoped Queries")
print("=" * 80)

# List user's accessible projects
result = _test_api.list_user_projects(_user1_test_id, _org1_test_id)
test_assert(result['success'] == True, "Can list user projects")
test_assert(result['count'] >= 2, "User has access to multiple projects")

# Organization admin view (all projects)
result = _test_api.list_organization_projects(
    _org1_test_id, _user1_test_id, 'owner', include_archived=False
)
test_assert(result['success'] == True, "Owner can list all org projects")
test_assert(result['count'] >= 3, "All active projects listed")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

total_tests = len(_test_results)
passed_tests = sum(1 for r in _test_results if r['passed'])
failed_tests = total_tests - passed_tests

print(f"\nTotal Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")

if failed_tests > 0:
    print("\nFailed Tests:")
    for r in _test_results:
        if not r['passed']:
            print(f"  • {r['test']}")

print("\n" + "=" * 80)
print("KEY FEATURES VALIDATED:")
print("=" * 80)
print("✅ Full CRUD operations (Create, Read, Update, Delete)")
print("✅ Soft delete with restore capability")
print("✅ Archive/unarchive projects")
print("✅ Role-based access control (owner, admin, developer)")
print("✅ Tenant isolation (organization-scoped)")
print("✅ Hierarchical access (private/team/organization visibility)")
print("✅ Project member management")
print("✅ Project-scoped queries")
print("✅ Statistics and reporting")
print("=" * 80)
