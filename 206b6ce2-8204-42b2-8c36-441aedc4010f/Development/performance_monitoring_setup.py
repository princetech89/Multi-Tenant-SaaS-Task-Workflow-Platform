"""
Performance Monitoring and Observability Setup
Comprehensive monitoring for production-ready architecture
"""

# Prometheus metrics integration
prometheus_metrics = """
# monitoring/metrics.py - Prometheus metrics for FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Current database connection pool size'
)

db_connection_pool_available = Gauge(
    'db_connection_pool_available',
    'Available database connections in pool'
)

redis_cache_hits = Counter(
    'redis_cache_hits_total',
    'Total Redis cache hits'
)

redis_cache_misses = Counter(
    'redis_cache_misses_total',
    'Total Redis cache misses'
)

active_sessions = Gauge(
    'active_sessions_total',
    'Total active user sessions'
)

background_tasks_queue = Gauge(
    'background_tasks_queue_size',
    'Number of tasks in background queue'
)

# Middleware for automatic metric collection
class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

# Update pool metrics periodically
async def update_pool_metrics():
    while True:
        db_connection_pool_size.set(db_pool.get_size())
        db_connection_pool_available.set(db_pool.get_idle_size())
        await asyncio.sleep(10)
"""

# CloudWatch integration for AWS
cloudwatch_logging = """
# monitoring/cloudwatch.py - AWS CloudWatch integration
import boto3
import json
from datetime import datetime
from typing import Dict, Any

class CloudWatchLogger:
    '''Send application metrics to CloudWatch'''
    
    def __init__(self, namespace: str = 'SaaS/Application'):
        self.cloudwatch = boto3.client('cloudwatch')
        self.logs = boto3.client('logs')
        self.namespace = namespace
        self.log_group = '/aws/application/saas-api'
        self.log_stream = f"instance-{os.getenv('INSTANCE_ID', 'default')}"
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'Count',
        dimensions: Dict[str, str] = None
    ):
        '''Put custom metric to CloudWatch'''
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }
        
        if dimensions:
            metric_data['Dimensions'] = [
                {'Name': k, 'Value': v} for k, v in dimensions.items()
            ]
        
        self.cloudwatch.put_metric_data(
            Namespace=self.namespace,
            MetricData=[metric_data]
        )
    
    def log_event(self, level: str, message: str, context: Dict[str, Any] = None):
        '''Send log event to CloudWatch Logs'''
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            'context': context or {}
        }
        
        self.logs.put_log_events(
            logGroupName=self.log_group,
            logStreamName=self.log_stream,
            logEvents=[{
                'timestamp': int(datetime.utcnow().timestamp() * 1000),
                'message': json.dumps(log_entry)
            }]
        )

# Usage examples
cw_logger = CloudWatchLogger()

# Track API response times
cw_logger.put_metric(
    'APIResponseTime',
    duration,
    unit='Milliseconds',
    dimensions={'Endpoint': '/api/projects', 'Method': 'GET'}
)

# Track error rates
cw_logger.put_metric(
    'ErrorCount',
    1,
    dimensions={'ErrorType': '500', 'Endpoint': '/api/tasks'}
)

# Track business metrics
cw_logger.put_metric(
    'ProjectsCreated',
    1,
    dimensions={'OrganizationID': org_id}
)
"""

# Application Performance Monitoring (APM)
apm_integration = """
# monitoring/apm.py - Application Performance Monitoring
import elasticapm
from elasticapm.contrib.starlette import ElasticAPM

# Initialize Elastic APM
apm_config = {
    'SERVICE_NAME': 'saas-api',
    'SECRET_TOKEN': os.getenv('ELASTIC_APM_SECRET_TOKEN'),
    'SERVER_URL': os.getenv('ELASTIC_APM_SERVER_URL'),
    'ENVIRONMENT': os.getenv('ENVIRONMENT', 'production'),
    'CAPTURE_BODY': 'all',
    'TRANSACTION_SAMPLE_RATE': 1.0,
    'SPAN_FRAMES_MIN_DURATION': '5ms'
}

# Add to FastAPI
app.add_middleware(ElasticAPM, client=elasticapm.Client(apm_config))

# Custom transaction tracking
@elasticapm.capture_span('database.query')
async def execute_complex_query(org_id: str):
    '''Automatically tracked in APM'''
    result = await db.fetch('''
        SELECT * FROM projects
        WHERE organization_id = $1
    ''', org_id)
    return result

# Track custom metrics
elasticapm.label(
    organization_id=org_id,
    user_role=user_role,
    feature_flag='new_dashboard'
)
"""

# Health check endpoints
health_checks = """
# api/health.py - Comprehensive health checks
from fastapi import APIRouter, Response
import asyncpg
import redis
import psutil
from datetime import datetime

router = APIRouter(tags=['health'])

@router.get('/health')
async def health_check():
    '''Basic health check for load balancer'''
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}

@router.get('/health/detailed')
async def detailed_health_check():
    '''Detailed health check with dependency status'''
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        health_status['checks']['database'] = {
            'status': 'healthy',
            'pool_size': db_pool.get_size(),
            'pool_available': db_pool.get_idle_size()
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # Redis check
    try:
        redis_client.ping()
        health_status['checks']['redis'] = {'status': 'healthy'}
    except Exception as e:
        health_status['status'] = 'degraded'
        health_status['checks']['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # System resources
    health_status['checks']['system'] = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }
    
    # Determine overall status
    if health_status['status'] == 'unhealthy':
        return Response(
            content=json.dumps(health_status),
            status_code=503,
            media_type='application/json'
        )
    
    return health_status

@router.get('/health/readiness')
async def readiness_check():
    '''Kubernetes readiness probe'''
    # Check if app is ready to serve traffic
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        return {'ready': True}
    except:
        return Response(
            content=json.dumps({'ready': False}),
            status_code=503,
            media_type='application/json'
        )

@router.get('/health/liveness')
async def liveness_check():
    '''Kubernetes liveness probe'''
    # Check if app is alive (not deadlocked)
    return {'alive': True}
"""

# Structured logging configuration
structured_logging = """
# monitoring/logging_config.py - Structured logging
import logging
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    '''Custom JSON formatter with additional context'''
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['service'] = 'saas-api'
        log_record['instance_id'] = os.getenv('INSTANCE_ID')
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'organization_id'):
            log_record['organization_id'] = record.organization_id

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(CustomJsonFormatter())

logger = logging.getLogger('saas-api')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info(
    'Project created',
    extra={
        'user_id': user_id,
        'organization_id': org_id,
        'project_id': project_id,
        'request_id': request_id
    }
)
"""

# Grafana dashboard configuration
grafana_dashboard = """
# monitoring/grafana_dashboard.json - Pre-configured dashboard
{
  "dashboard": {
    "title": "SaaS Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m])"
          }
        ]
      },
      {
        "title": "Database Connection Pool",
        "targets": [
          {
            "expr": "db_connection_pool_size"
          },
          {
            "expr": "db_connection_pool_available"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "rate(redis_cache_hits_total[5m]) / (rate(redis_cache_hits_total[5m]) + rate(redis_cache_misses_total[5m]))"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "targets": [
          {
            "expr": "active_sessions_total"
          }
        ]
      }
    ]
  }
}
"""

# Alert configuration
alert_rules = """
# monitoring/alert_rules.yml - Prometheus alert rules
groups:
  - name: application_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
      
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response times detected"
          description: "P95 response time is {{ $value }}s"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: db_connection_pool_available < 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Only {{ $value }} connections available"
      
      - alert: HighCPUUsage
        expr: system_cpu_percent > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"
      
      - alert: HighMemoryUsage
        expr: system_memory_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"
"""

monitoring_components = {
    "prometheus": {
        "description": "Time-series metrics and alerting",
        "metrics": [
            "HTTP request rates and latencies",
            "Database connection pool stats",
            "Redis cache hit/miss rates",
            "Active sessions count",
            "Background task queue size"
        ]
    },
    "cloudwatch": {
        "description": "AWS native monitoring and logging",
        "features": [
            "Custom application metrics",
            "Centralized log aggregation",
            "CloudWatch Alarms",
            "AWS service integration"
        ]
    },
    "elastic_apm": {
        "description": "Application Performance Monitoring",
        "capabilities": [
            "Distributed tracing",
            "Error tracking",
            "Transaction monitoring",
            "Service maps"
        ]
    },
    "grafana": {
        "description": "Visualization and dashboards",
        "dashboards": [
            "API performance overview",
            "Database metrics",
            "Business KPIs",
            "System resources"
        ]
    }
}

monitoring_best_practices = [
    "Implement comprehensive health checks for load balancers",
    "Use structured JSON logging for better searchability",
    "Set up alerts for critical metrics (error rate, latency, pool exhaustion)",
    "Monitor both technical and business metrics",
    "Use distributed tracing for debugging issues across services",
    "Track cache hit rates to optimize caching strategy",
    "Monitor connection pool utilization to prevent exhaustion",
    "Set up synthetic monitoring for critical user flows",
    "Use percentile metrics (p50, p95, p99) not just averages",
    "Implement request ID tracking across all services"
]

print("=" * 80)
print("PERFORMANCE MONITORING & OBSERVABILITY SETUP")
print("=" * 80)
print()

print("MONITORING COMPONENTS")
print("-" * 80)
for component, config in monitoring_components.items():
    print(f"\n{component.upper()}")
    print(f"  {config['description']}")
    
    if 'metrics' in config:
        print("  Metrics:")
        for metric in config['metrics']:
            print(f"    • {metric}")
    
    if 'features' in config:
        print("  Features:")
        for feature in config['features']:
            print(f"    • {feature}")
    
    if 'capabilities' in config:
        print("  Capabilities:")
        for cap in config['capabilities']:
            print(f"    • {cap}")
    
    if 'dashboards' in config:
        print("  Dashboards:")
        for dash in config['dashboards']:
            print(f"    • {dash}")

print("\n" + "=" * 80)
print("MONITORING BEST PRACTICES")
print("=" * 80)
for idx, practice in enumerate(monitoring_best_practices, 1):
    print(f"{idx:2d}. {practice}")

print("\n" + "=" * 80)
print("IMPLEMENTATION ARTIFACTS")
print("=" * 80)
print("  ✓ Prometheus metrics middleware")
print("  ✓ CloudWatch logging integration")
print("  ✓ Elastic APM instrumentation")
print("  ✓ Health check endpoints (liveness/readiness)")
print("  ✓ Structured JSON logging")
print("  ✓ Grafana dashboard templates")
print("  ✓ Prometheus alert rules")

print("\n" + "=" * 80)
print("KEY METRICS TO MONITOR")
print("=" * 80)
print("""
GOLDEN SIGNALS:
  • Latency: Request duration (p50, p95, p99)
  • Traffic: Requests per second
  • Errors: Error rate by endpoint
  • Saturation: Resource utilization (CPU, memory, connections)

BUSINESS METRICS:
  • Projects created per hour
  • Active users per organization
  • Task completion rate
  • API usage by organization

INFRASTRUCTURE METRICS:
  • Database connection pool utilization
  • Redis cache hit rate
  • Background task queue length
  • Instance health status
""")

implementation_files = {
    "metrics.py": prometheus_metrics,
    "cloudwatch.py": cloudwatch_logging,
    "apm.py": apm_integration,
    "health.py": health_checks,
    "logging_config.py": structured_logging,
    "grafana_dashboard.json": grafana_dashboard,
    "alert_rules.yml": alert_rules
}
