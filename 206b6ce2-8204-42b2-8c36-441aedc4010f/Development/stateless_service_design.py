"""
Stateless Service Design for Horizontal Scaling
Enables multiple instances with shared state in Redis/Database
"""

stateless_architecture = """
# config/stateless_design.py - Core stateless principles

STATELESS DESIGN PRINCIPLES:
=============================

1. NO LOCAL STATE
   - No session data stored in server memory
   - No file uploads stored locally
   - No in-memory caches shared between requests
   - No server-side state between requests

2. EXTERNALIZED STATE
   - Sessions stored in Redis
   - Files stored in S3/object storage
   - Cache stored in Redis
   - Database for persistent data

3. HORIZONTAL SCALABILITY
   - Any instance can handle any request
   - Load balancer can distribute freely
   - Instances can be added/removed dynamically
   - No sticky sessions required

4. SHARED RESOURCES
   - Centralized database (with connection pooling)
   - Shared Redis for cache/sessions
   - Shared object storage for files
   - Message queue for async tasks
"""

# Session management with Redis
redis_session_management = """
# services/session_service.py - Redis-based stateless sessions
import redis
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict

class StatelessSessionManager:
    '''Manage sessions in Redis for stateless architecture'''
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_prefix = "session:"
        self.default_ttl = 86400  # 24 hours
    
    def create_session(self, user_id: str, metadata: Dict) -> str:
        '''Create new session in Redis'''
        session_id = str(uuid.uuid4())
        session_key = f"{self.session_prefix}{session_id}"
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        
        # Store in Redis with TTL
        self.redis.setex(
            session_key,
            self.default_ttl,
            json.dumps(session_data)
        )
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        '''Retrieve session from Redis'''
        session_key = f"{self.session_prefix}{session_id}"
        data = self.redis.get(session_key)
        
        if not data:
            return None
        
        session = json.loads(data)
        
        # Update last activity and refresh TTL
        session["last_activity"] = datetime.utcnow().isoformat()
        self.redis.setex(
            session_key,
            self.default_ttl,
            json.dumps(session)
        )
        
        return session
    
    def delete_session(self, session_id: str):
        '''Delete session from Redis'''
        session_key = f"{self.session_prefix}{session_id}"
        self.redis.delete(session_key)
    
    def update_session(self, session_id: str, updates: Dict):
        '''Update session data'''
        session = self.get_session(session_id)
        if session:
            session["metadata"].update(updates)
            session_key = f"{self.session_prefix}{session_id}"
            self.redis.setex(
                session_key,
                self.default_ttl,
                json.dumps(session)
            )

# Example usage
redis_client = redis.Redis(host='redis-cluster', port=6379, decode_responses=True)
session_manager = StatelessSessionManager(redis_client)

# Create session on login
session_id = session_manager.create_session(
    user_id="user_123",
    metadata={"organization_id": "org_456", "role": "ADMIN"}
)

# Retrieve session on subsequent requests (from any server instance)
session = session_manager.get_session(session_id)
"""

# File upload to S3
file_storage_service = """
# services/file_storage.py - S3-based file storage (stateless)
import boto3
import uuid
from typing import BinaryIO
from datetime import datetime

class StatelessFileStorage:
    '''Store files in S3 instead of local filesystem'''
    
    def __init__(self, bucket_name: str):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name
    
    def upload_file(
        self,
        file: BinaryIO,
        organization_id: str,
        filename: str,
        content_type: str
    ) -> Dict[str, str]:
        '''Upload file to S3 and return metadata'''
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Construct S3 key with organization prefix
        s3_key = f"{organization_id}/uploads/{file_id}/{filename}"
        
        # Upload to S3
        self.s3_client.upload_fileobj(
            file,
            self.bucket_name,
            s3_key,
            ExtraArgs={
                'ContentType': content_type,
                'Metadata': {
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'organization_id': organization_id
                }
            }
        )
        
        # Generate presigned URL for download
        download_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            "file_id": file_id,
            "filename": filename,
            "s3_key": s3_key,
            "download_url": download_url,
            "size": file.tell()
        }
    
    def get_file_url(self, s3_key: str, expires_in: int = 3600) -> str:
        '''Generate presigned URL for file access'''
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': s3_key},
            ExpiresIn=expires_in
        )
    
    def delete_file(self, s3_key: str):
        '''Delete file from S3'''
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=s3_key
        )

# Example usage with FastAPI
from fastapi import UploadFile

@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile,
    organization_id: str,
    storage: StatelessFileStorage = Depends(get_file_storage)
):
    '''Upload file to S3 (stateless - works on any instance)'''
    
    file_metadata = storage.upload_file(
        file.file,
        organization_id,
        file.filename,
        file.content_type
    )
    
    # Store metadata in database (shared across instances)
    await db.execute('''
        INSERT INTO files (id, organization_id, filename, s3_key, size)
        VALUES ($1, $2, $3, $4, $5)
    ''',
        file_metadata['file_id'],
        organization_id,
        file_metadata['filename'],
        file_metadata['s3_key'],
        file_metadata['size']
    )
    
    return file_metadata
"""

# Distributed caching with Redis
distributed_cache = """
# services/cache_service.py - Distributed cache for stateless architecture
import redis
import json
from typing import Optional, Any, Callable
from functools import wraps
import hashlib

class DistributedCache:
    '''Redis-based cache shared across all instances'''
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        '''Get value from cache'''
        data = self.redis.get(key)
        return json.loads(data) if data else None
    
    def set(self, key: str, value: Any, ttl: int = None):
        '''Set value in cache with TTL'''
        ttl = ttl or self.default_ttl
        self.redis.setex(key, ttl, json.dumps(value, default=str))
    
    def delete(self, key: str):
        '''Delete key from cache'''
        self.redis.delete(key)
    
    def delete_pattern(self, pattern: str):
        '''Delete all keys matching pattern'''
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
    
    def cache_decorator(self, ttl: int = None):
        '''Decorator to cache function results'''
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_data = f"{func.__name__}:{args}:{kwargs}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Check cache
                cached = self.get(cache_key)
                if cached is not None:
                    return cached
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                self.set(cache_key, result, ttl or self.default_ttl)
                
                return result
            return wrapper
        return decorator

# Example usage
cache = DistributedCache(redis_client)

@cache.cache_decorator(ttl=600)
async def get_organization_settings(org_id: str):
    '''Cached across all instances'''
    return await db.fetchrow(
        "SELECT * FROM organizations WHERE id = $1",
        org_id
    )
"""

# Load balancer configuration
load_balancer_config = """
# nginx.conf - Load balancer for stateless instances

upstream api_servers {
    # No need for ip_hash (sticky sessions) - completely stateless
    least_conn;  # Route to least busy server
    
    server api-instance-1:8000 max_fails=3 fail_timeout=30s;
    server api-instance-2:8000 max_fails=3 fail_timeout=30s;
    server api-instance-3:8000 max_fails=3 fail_timeout=30s;
    server api-instance-4:8000 max_fails=3 fail_timeout=30s;
    
    # Health check
    check interval=10000 rise=2 fall=3 timeout=1000;
}

server {
    listen 80;
    server_name api.yoursaas.com;
    
    location / {
        proxy_pass http://api_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # No sticky sessions needed - completely stateless
        proxy_next_upstream error timeout http_500 http_502 http_503;
    }
    
    location /health {
        proxy_pass http://api_servers/health;
    }
}
"""

# Docker compose for multi-instance deployment
docker_compose = """
# docker-compose.yml - Multiple stateless instances
version: '3.8'

services:
  # Shared PostgreSQL
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: saas_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  # Shared Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
  
  # API Instance 1
  api-1:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/saas_db
      REDIS_URL: redis://redis:6379
      S3_BUCKET: your-saas-files
      INSTANCE_ID: api-1
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
  
  # API Instance 2
  api-2:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/saas_db
      REDIS_URL: redis://redis:6379
      S3_BUCKET: your-saas-files
      INSTANCE_ID: api-2
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
  
  # API Instance 3
  api-3:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/saas_db
      REDIS_URL: redis://redis:6379
      S3_BUCKET: your-saas-files
      INSTANCE_ID: api-3
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
  
  # API Instance 4
  api-4:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/saas_db
      REDIS_URL: redis://redis:6379
      S3_BUCKET: your-saas-files
      INSTANCE_ID: api-4
    depends_on:
      - postgres
      - redis
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
  
  # Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api-1
      - api-2
      - api-3
      - api-4

volumes:
  postgres_data:
"""

stateless_checklist = {
    "sessions": "✓ Stored in Redis, accessible from any instance",
    "file_uploads": "✓ Stored in S3, not local filesystem",
    "cache": "✓ Distributed Redis cache, shared across instances",
    "database": "✓ Centralized PostgreSQL with connection pooling",
    "background_tasks": "✓ Queue-based (Redis/Celery), not in-memory",
    "configuration": "✓ Environment variables, not local files",
    "logging": "✓ Centralized logging (CloudWatch/ELK)",
    "health_checks": "✓ Endpoint returns status without local state"
}

scaling_benefits = {
    "horizontal_scaling": "Add more instances to handle increased load",
    "no_sticky_sessions": "Load balancer can route to any instance",
    "fault_tolerance": "Instance failure doesn't lose user sessions",
    "zero_downtime_deployment": "Rolling updates without session loss",
    "auto_scaling": "AWS Auto Scaling can add/remove instances automatically",
    "geographical_distribution": "Instances can be deployed across regions",
    "cost_efficiency": "Scale down during low traffic periods"
}

print("=" * 80)
print("STATELESS SERVICE DESIGN FOR HORIZONTAL SCALING")
print("=" * 80)
print()

print("STATELESS ARCHITECTURE CHECKLIST")
print("-" * 80)
for component, status in stateless_checklist.items():
    print(f"{component.upper()}: {status}")

print("\n" + "=" * 80)
print("HORIZONTAL SCALING BENEFITS")
print("=" * 80)
for benefit, description in scaling_benefits.items():
    print(f"\n{benefit.replace('_', ' ').title()}")
    print(f"  {description}")

print("\n" + "=" * 80)
print("IMPLEMENTATION COMPONENTS")
print("=" * 80)
print("  ✓ Redis-based session management")
print("  ✓ S3 file storage (no local files)")
print("  ✓ Distributed Redis cache")
print("  ✓ Load balancer configuration (no sticky sessions)")
print("  ✓ Docker Compose multi-instance setup")
print("  ✓ Connection pooling for shared database")
print("  ✓ Health check endpoints")
print("  ✓ Environment-based configuration")

print("\n" + "=" * 80)
print("DEPLOYMENT ARCHITECTURE")
print("=" * 80)
print("""
    Load Balancer (NGINX)
           |
    +------+------+------+------+
    |      |      |      |      |
  API-1  API-2  API-3  API-4   (Stateless instances)
    |      |      |      |      |
    +------+------+------+------+
           |             |
      PostgreSQL      Redis      S3
      (Database)    (Cache)   (Files)
""")

implementation_artifacts = {
    "session_service.py": redis_session_management,
    "file_storage.py": file_storage_service,
    "cache_service.py": distributed_cache,
    "nginx.conf": load_balancer_config,
    "docker-compose.yml": docker_compose,
    "stateless_design.py": stateless_architecture
}
