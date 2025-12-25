"""
Database Indexing Strategy for Multi-Tenant SaaS Application
Optimized for horizontal scaling and query performance
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class IndexDefinition:
    """Index definition with rationale"""
    table: str
    name: str
    columns: List[str]
    index_type: str
    rationale: str

# Core indexing strategy for production-ready horizontal scaling
indexing_strategy = {
    "organizations": [
        IndexDefinition(
            table="organizations",
            name="idx_org_created_at",
            columns=["created_at"],
            index_type="BTREE",
            rationale="Optimizes time-based queries and activity feed generation"
        ),
        IndexDefinition(
            table="organizations",
            name="idx_org_subdomain",
            columns=["subdomain"],
            index_type="UNIQUE BTREE",
            rationale="Fast subdomain lookup for multi-tenant routing, enforces uniqueness"
        )
    ],
    
    "users": [
        IndexDefinition(
            table="users",
            name="idx_user_email",
            columns=["email"],
            index_type="UNIQUE BTREE",
            rationale="Fast authentication lookups, enforces uniqueness constraint"
        ),
        IndexDefinition(
            table="users",
            name="idx_user_org_id",
            columns=["organization_id"],
            index_type="BTREE",
            rationale="Critical for tenant isolation and organization member queries"
        ),
        IndexDefinition(
            table="users",
            name="idx_user_org_role",
            columns=["organization_id", "role"],
            index_type="COMPOSITE BTREE",
            rationale="Optimizes permission checks and role-based filtering"
        )
    ],
    
    "projects": [
        IndexDefinition(
            table="projects",
            name="idx_project_org_id",
            columns=["organization_id"],
            index_type="BTREE",
            rationale="Tenant isolation filter - most critical index for multi-tenancy"
        ),
        IndexDefinition(
            table="projects",
            name="idx_project_org_status",
            columns=["organization_id", "status"],
            index_type="COMPOSITE BTREE",
            rationale="Dashboard queries filtering by status within organization"
        ),
        IndexDefinition(
            table="projects",
            name="idx_project_created_at",
            columns=["created_at"],
            index_type="BTREE",
            rationale="Activity feeds and recent project queries"
        )
    ],
    
    "tasks": [
        IndexDefinition(
            table="tasks",
            name="idx_task_project_id",
            columns=["project_id"],
            index_type="BTREE",
            rationale="Project task list queries - high frequency operation"
        ),
        IndexDefinition(
            table="tasks",
            name="idx_task_assignee",
            columns=["assignee_id"],
            index_type="BTREE",
            rationale="User task dashboard and assignment queries"
        ),
        IndexDefinition(
            table="tasks",
            name="idx_task_status",
            columns=["status"],
            index_type="BTREE",
            rationale="Kanban board views and status-based filtering"
        ),
        IndexDefinition(
            table="tasks",
            name="idx_task_project_status",
            columns=["project_id", "status"],
            index_type="COMPOSITE BTREE",
            rationale="Optimizes project kanban board queries - very high frequency"
        ),
        IndexDefinition(
            table="tasks",
            name="idx_task_due_date",
            columns=["due_date"],
            index_type="BTREE",
            rationale="Deadline tracking and notification queries"
        )
    ],
    
    "audit_logs": [
        IndexDefinition(
            table="audit_logs",
            name="idx_audit_org_id",
            columns=["organization_id"],
            index_type="BTREE",
            rationale="Tenant isolation for audit log queries"
        ),
        IndexDefinition(
            table="audit_logs",
            name="idx_audit_timestamp",
            columns=["timestamp"],
            index_type="BTREE",
            rationale="Time-based activity feed and audit trail queries"
        ),
        IndexDefinition(
            table="audit_logs",
            name="idx_audit_entity",
            columns=["entity_type", "entity_id"],
            index_type="COMPOSITE BTREE",
            rationale="Entity-specific activity history lookups"
        ),
        IndexDefinition(
            table="audit_logs",
            name="idx_audit_user_id",
            columns=["user_id"],
            index_type="BTREE",
            rationale="User activity tracking and analytics"
        )
    ],
    
    "notifications": [
        IndexDefinition(
            table="notifications",
            name="idx_notif_user_read",
            columns=["user_id", "read"],
            index_type="COMPOSITE BTREE",
            rationale="Unread notification queries - extremely high frequency"
        ),
        IndexDefinition(
            table="notifications",
            name="idx_notif_created_at",
            columns=["created_at"],
            index_type="BTREE",
            rationale="Recent notifications and time-based queries"
        )
    ],
    
    "sessions": [
        IndexDefinition(
            table="sessions",
            name="idx_session_user_id",
            columns=["user_id"],
            index_type="BTREE",
            rationale="Active session lookups and user session management"
        ),
        IndexDefinition(
            table="sessions",
            name="idx_session_expires",
            columns=["expires_at"],
            index_type="BTREE",
            rationale="Session cleanup and expiration checks"
        )
    ]
}

# Generate SQL DDL statements
index_ddl_statements = []

for table, indexes in indexing_strategy.items():
    for idx in indexes:
        if "UNIQUE" in idx.index_type:
            sql = f"CREATE UNIQUE INDEX {idx.name} ON {idx.table} ({', '.join(idx.columns)});"
        else:
            sql = f"CREATE INDEX {idx.name} ON {idx.table} ({', '.join(idx.columns)});"
        index_ddl_statements.append(sql)

# Performance monitoring queries
monitoring_queries = {
    "index_usage": """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
    """,
    
    "missing_indexes": """
        SELECT 
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            seq_tup_read / seq_scan as avg_tuples_per_scan
        FROM pg_stat_user_tables
        WHERE seq_scan > 0
        ORDER BY seq_scan DESC;
    """,
    
    "table_sizes": """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    """
}

# Composite index strategy for common query patterns
composite_index_notes = """
COMPOSITE INDEX STRATEGY:

1. Organization + Secondary Filters:
   - organization_id MUST be first column (tenant isolation)
   - Secondary filters (status, role, etc.) come second
   - Supports both single-org queries and filtered queries

2. Entity + Status Patterns:
   - project_id + status for kanban boards
   - user_id + read for notifications
   - Covers most common dashboard queries

3. Time-Based Queries:
   - created_at/timestamp for activity feeds
   - due_date for deadline tracking
   - expires_at for cleanup operations

4. Lookup Patterns:
   - entity_type + entity_id for polymorphic relations
   - Supports fast entity history lookups
"""

# Print comprehensive strategy
print("=" * 80)
print("DATABASE INDEXING STRATEGY FOR HORIZONTAL SCALING")
print("=" * 80)
print()

total_indexes = sum(len(indexes) for indexes in indexing_strategy.values())
print(f"Total Indexes: {total_indexes}")
print(f"Tables Covered: {len(indexing_strategy)}")
print()

for table, indexes in indexing_strategy.items():
    print(f"\n{table.upper()} ({len(indexes)} indexes)")
    print("-" * 80)
    for idx in indexes:
        print(f"  {idx.name}")
        print(f"    Columns: {', '.join(idx.columns)}")
        print(f"    Type: {idx.index_type}")
        print(f"    Rationale: {idx.rationale}")
        print()

print("\n" + "=" * 80)
print("SQL DDL STATEMENTS")
print("=" * 80)
for sql in index_ddl_statements:
    print(sql)

print("\n" + "=" * 80)
print("PERFORMANCE MONITORING")
print("=" * 80)
print(composite_index_notes)
print("\nMonitoring Queries Available:")
for query_name in monitoring_queries.keys():
    print(f"  - {query_name}")
