"""
Async Request Handling with FastAPI for High Concurrency
Implements connection pooling, async operations, and background tasks
"""

async_fastapi_implementation = """
# main.py - Async FastAPI application
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import aioredis
from typing import Optional
import asyncio

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None
redis_pool: Optional[aioredis.Redis] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''Manage application lifecycle - connection pools'''
    global db_pool, redis_pool
    
    # Startup: Initialize connection pools
    db_pool = await asyncpg.create_pool(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='saas_db',
        min_size=10,
        max_size=50,
        command_timeout=60,
        max_queries=50000,
        max_inactive_connection_lifetime=300
    )
    
    redis_pool = await aioredis.create_redis_pool(
        'redis://localhost:6379',
        minsize=5,
        maxsize=20,
        encoding='utf-8'
    )
    
    print("✓ Connection pools initialized")
    
    yield
    
    # Shutdown: Close connection pools
    await db_pool.close()
    redis_pool.close()
    await redis_pool.wait_closed()
    print("✓ Connection pools closed")

app = FastAPI(
    title="Multi-Tenant SaaS API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency: Get database connection from pool
async def get_db():
    async with db_pool.acquire() as connection:
        yield connection

# Dependency: Get Redis connection
async def get_redis():
    return redis_pool
"""

async_endpoints = """
# api/projects.py - Async endpoints with connection pooling
from fastapi import APIRouter, Depends, BackgroundTasks
from typing import List
import asyncpg
import aioredis
from datetime import datetime
import json

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("/{org_id}/projects", response_model=List[dict])
async def list_projects(
    org_id: str,
    status: Optional[str] = None,
    db: asyncpg.Connection = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    '''List projects for organization with Redis caching'''
    
    # Check cache first
    cache_key = f"projects:{org_id}:{status or 'all'}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Query database with prepared statement
    if status:
        query = '''
            SELECT id, name, description, status, created_at, updated_at
            FROM projects
            WHERE organization_id = $1 AND status = $2
            ORDER BY created_at DESC
        '''
        rows = await db.fetch(query, org_id, status)
    else:
        query = '''
            SELECT id, name, description, status, created_at, updated_at
            FROM projects
            WHERE organization_id = $1
            ORDER BY created_at DESC
        '''
        rows = await db.fetch(query, org_id)
    
    # Convert to list of dicts
    projects = [dict(row) for row in rows]
    
    # Cache for 5 minutes
    await redis.setex(cache_key, 300, json.dumps(projects, default=str))
    
    return projects

@router.post("/{org_id}/projects")
async def create_project(
    org_id: str,
    project: dict,
    background_tasks: BackgroundTasks,
    db: asyncpg.Connection = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    '''Create project with background task for notifications'''
    
    # Insert project
    query = '''
        INSERT INTO projects (organization_id, name, description, status, created_by)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, name, description, status, created_at
    '''
    row = await db.fetchrow(
        query,
        org_id,
        project['name'],
        project.get('description'),
        'ACTIVE',
        project['created_by']
    )
    
    project_data = dict(row)
    
    # Invalidate cache
    await redis.delete(f"projects:{org_id}:all")
    await redis.delete(f"projects:{org_id}:ACTIVE")
    
    # Schedule background tasks
    background_tasks.add_task(
        send_project_created_notification,
        org_id,
        project_data
    )
    background_tasks.add_task(
        log_audit_event,
        org_id,
        'PROJECT_CREATED',
        project_data['id']
    )
    
    return project_data

@router.get("/{org_id}/projects/stats")
async def project_statistics(
    org_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    '''Get project statistics with parallel queries'''
    
    # Execute multiple queries concurrently
    total_query = "SELECT COUNT(*) FROM projects WHERE organization_id = $1"
    active_query = "SELECT COUNT(*) FROM projects WHERE organization_id = $1 AND status = 'ACTIVE'"
    completed_query = "SELECT COUNT(*) FROM projects WHERE organization_id = $1 AND status = 'COMPLETED'"
    
    total, active, completed = await asyncio.gather(
        db.fetchval(total_query, org_id),
        db.fetchval(active_query, org_id),
        db.fetchval(completed_query, org_id)
    )
    
    return {
        "total": total,
        "active": active,
        "completed": completed,
        "archived": total - active - completed
    }
"""

background_tasks = """
# services/background_tasks.py - Background task handlers
import asyncpg
import aioredis
from datetime import datetime
import asyncio

async def send_project_created_notification(org_id: str, project_data: dict):
    '''Send notifications to team members (async)'''
    await asyncio.sleep(0.1)  # Simulate async work
    
    async with db_pool.acquire() as conn:
        # Get organization members
        members = await conn.fetch(
            "SELECT user_id, email FROM users WHERE organization_id = $1",
            org_id
        )
        
        # Create notifications for each member
        for member in members:
            await conn.execute('''
                INSERT INTO notifications (user_id, type, title, message, entity_type, entity_id)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''',
                member['user_id'],
                'PROJECT_CREATED',
                'New Project Created',
                f"Project '{project_data['name']}' has been created",
                'PROJECT',
                project_data['id']
            )
    
    print(f"✓ Notifications sent for project {project_data['id']}")

async def log_audit_event(org_id: str, action: str, entity_id: str):
    '''Log audit event asynchronously'''
    async with db_pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO audit_logs (organization_id, action_type, entity_type, entity_id, timestamp)
            VALUES ($1, $2, $3, $4, $5)
        ''',
            org_id,
            action,
            'PROJECT',
            entity_id,
            datetime.utcnow()
        )
    
    print(f"✓ Audit log created for {action}")

async def process_bulk_import(org_id: str, file_path: str):
    '''Process bulk import in background'''
    # Long-running task
    async with db_pool.acquire() as conn:
        # Read and process file
        await asyncio.sleep(5)  # Simulate processing
        
        # Bulk insert (use COPY for best performance)
        await conn.copy_to_table(
            'tasks',
            source=file_path,
            columns=['project_id', 'title', 'description', 'status']
        )
    
    print(f"✓ Bulk import completed for org {org_id}")
"""

async_middleware = """
# middleware/async_middleware.py - Async middleware for request processing
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio

class AsyncRequestMiddleware(BaseHTTPMiddleware):
    '''Async middleware for request timing and logging'''
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add timing header
        response.headers["X-Process-Time"] = str(duration)
        
        # Log slow requests asynchronously
        if duration > 1.0:
            asyncio.create_task(
                log_slow_request(request.url.path, duration)
            )
        
        return response

class ConnectionPoolMiddleware(BaseHTTPMiddleware):
    '''Monitor connection pool health'''
    
    async def dispatch(self, request: Request, call_next):
        # Check pool health before processing
        if db_pool.get_size() >= db_pool.get_max_size() * 0.9:
            print(f"⚠ WARNING: Connection pool near capacity")
        
        response = await call_next(request)
        return response

async def log_slow_request(path: str, duration: float):
    '''Log slow requests to monitoring system'''
    async with db_pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO performance_logs (endpoint, duration, timestamp)
            VALUES ($1, $2, $3)
        ''', path, duration, datetime.utcnow())
"""

streaming_response = """
# api/streaming.py - Streaming responses for large datasets
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncpg
import json

router = APIRouter(prefix="/api/stream", tags=["streaming"])

@router.get("/projects/{org_id}/export")
async def export_projects_stream(
    org_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    '''Stream large dataset export'''
    
    async def generate_csv():
        # Send header
        yield "id,name,description,status,created_at\\n"
        
        # Stream results without loading all into memory
        async with db.transaction():
            cursor = await db.cursor('''
                SELECT id, name, description, status, created_at
                FROM projects
                WHERE organization_id = $1
            ''', org_id)
            
            async for row in cursor:
                csv_line = f"{row['id']},{row['name']},{row['description']},{row['status']},{row['created_at']}\\n"
                yield csv_line
    
    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=projects.csv"}
    )

@router.get("/tasks/{project_id}/stream")
async def stream_tasks(
    project_id: str,
    db: asyncpg.Connection = Depends(get_db)
):
    '''Server-sent events for real-time updates'''
    
    async def event_stream():
        while True:
            # Fetch latest tasks
            tasks = await db.fetch('''
                SELECT id, title, status, updated_at
                FROM tasks
                WHERE project_id = $1
                ORDER BY updated_at DESC
                LIMIT 10
            ''', project_id)
            
            # Send as SSE
            data = json.dumps([dict(t) for t in tasks], default=str)
            yield f"data: {data}\\n\\n"
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )
"""

performance_config = {
    "connection_pooling": {
        "database": {
            "min_connections": 10,
            "max_connections": 50,
            "connection_timeout": 60,
            "max_queries_per_connection": 50000,
            "max_inactive_lifetime": 300
        },
        "redis": {
            "min_connections": 5,
            "max_connections": 20,
            "socket_timeout": 5
        }
    },
    "async_workers": {
        "uvicorn_workers": 4,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "threads_per_worker": 1,
        "max_requests": 10000,
        "max_requests_jitter": 1000
    },
    "caching": {
        "strategy": "Redis with TTL",
        "ttl_seconds": 300,
        "cache_patterns": [
            "project_lists",
            "user_profiles",
            "organization_settings"
        ]
    },
    "background_tasks": {
        "executor": "asyncio",
        "max_concurrent_tasks": 10,
        "task_timeout": 300
    }
}

best_practices = [
    "Use asyncpg for PostgreSQL (10x faster than psycopg2)",
    "Implement connection pooling with proper limits",
    "Cache frequently accessed data in Redis",
    "Use background tasks for non-critical operations",
    "Stream large datasets instead of loading into memory",
    "Use prepared statements for repeated queries",
    "Monitor connection pool utilization",
    "Implement circuit breakers for external services",
    "Use asyncio.gather() for parallel async operations",
    "Set appropriate timeouts for all async operations"
]

print("=" * 80)
print("ASYNC REQUEST HANDLING ARCHITECTURE")
print("=" * 80)
print()

print("CONNECTION POOLING CONFIGURATION")
print("-" * 80)
for service, config in performance_config["connection_pooling"].items():
    print(f"\n{service.upper()}")
    for key, value in config.items():
        print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("ASYNC WORKERS CONFIGURATION")
print("=" * 80)
for key, value in performance_config["async_workers"].items():
    print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("PERFORMANCE BEST PRACTICES")
print("=" * 80)
for i, practice in enumerate(best_practices, 1):
    print(f"{i:2d}. {practice}")

print("\n" + "=" * 80)
print("IMPLEMENTATION FEATURES")
print("=" * 80)
print("  ✓ Async connection pooling (PostgreSQL + Redis)")
print("  ✓ Background task processing")
print("  ✓ Response caching with Redis")
print("  ✓ Streaming responses for large datasets")
print("  ✓ Server-sent events for real-time updates")
print("  ✓ Parallel async query execution")
print("  ✓ Request timing and monitoring")
print("  ✓ Graceful shutdown handling")

implementation_components = {
    "main.py": async_fastapi_implementation,
    "api/projects.py": async_endpoints,
    "services/background_tasks.py": background_tasks,
    "middleware/async_middleware.py": async_middleware,
    "api/streaming.py": streaming_response
}
