"""Prometheus metrics middleware for EVO-LOG SaaS monitoring"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.fastapi import metrics
from fastapi import Request
import time
from functools import wraps

# Application info
app_info = Info('evo_log_info', 'EVO-LOG SaaS Information')
app_info.info({
    'version': '2.0.0',
    'environment': 'production'
})

# HTTP metrics
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
http_requests_in_progress = Gauge('http_requests_in_progress', 'HTTP requests in progress', ['method', 'endpoint'])

# Database metrics
db_query_duration_seconds = Histogram('db_query_duration_seconds', 'Database query duration', ['operation'])
db_connections_active = Gauge('db_connections_active', 'Active database connections')
db_connections_idle = Gauge('db_connections_idle', 'Idle database connections')

# Tenant metrics
active_tenants = Gauge('active_tenants', 'Number of active tenants')
tenant_requests_total = Counter('tenant_requests_total', 'Total requests per tenant', ['tenant_id'])

# Business metrics
missions_created_total = Counter('missions_created_total', 'Total missions created', ['tenant_id'])
stock_adjustments_total = Counter('stock_adjustments_total', 'Total stock adjustments', ['tenant_id'])
api_errors_total = Counter('api_errors_total', 'Total API errors', ['endpoint', 'error_type'])

def track_endpoint_metrics(endpoint: str):
    """Decorator to track custom endpoint metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                http_requests_total.labels(
                    method='POST' if 'create' in endpoint or 'send' in endpoint else 'GET',
                    endpoint=endpoint,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                error_type = type(e).__name__
                api_errors_total.labels(endpoint=endpoint, error_type=error_type).inc()
                raise
            finally:
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method='POST' if 'create' in endpoint or 'send' in endpoint else 'GET',
                    endpoint=endpoint
                ).observe(duration)
        return wrapper
    return decorator
