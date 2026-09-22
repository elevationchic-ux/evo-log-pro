#!/bin/bash
# Monitoring Active Setup Script for EVO-LOG SaaS

echo "🚀 Setting up Active Monitoring for EVO-LOG SaaS"

# 1. Install Monitoring Tools
echo "📊 Installing monitoring tools..."

# Backend Monitoring
pip install prometheus-fastapi-instrumentator==7.0.0
pip install sentry-sdk==1.39.0
pip install slowapi==0.1.9

# 2. Setup Prometheus Configuration
echo "📈 Setting up Prometheus configuration..."
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'evo-log-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
EOF

# 3. Setup Grafana Dashboards
echo "📊 Setting up Grafana dashboards..."
mkdir -p grafana/dashboards

cat > grafana/dashboards/evo-log-overview.json << 'EOF'
{
  "dashboard": {
    "title": "EVO-LOG Overview",
    "panels": [
      {
        "title": "API Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])"
          }
        ]
      },
      {
        "title": "Database Connections",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      },
      {
        "title": "Redis Memory Usage",
        "targets": [
          {
            "expr": "redis_memory_used_bytes"
          }
        ]
      }
    ]
  }
}
EOF

# 4. Setup Sentry Configuration
echo "🔍 Setting up Sentry configuration..."
cat > sentry_config.py << 'EOF'
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn="${SENTRY_DSN}",
    traces_sample_rate=0.2,
    profiles_sample_rate=0.1,
    integrations=[
        SqlalchemyIntegration(),
        RedisIntegration(),
        CeleryIntegration(),
    ],
    environment="${ENVIRONMENT}",
    release="${RELEASE_VERSION}",
)
EOF

# 5. Setup Alerting Rules
echo "🚨 Setting up alerting rules..."
cat > prometheus_alerts.yml << 'EOF'
groups:
  - name: evo-log-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
      
      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
EOF

# 6. Setup Health Check Monitoring
echo "💓 Setting up health check monitoring..."
cat > health_check_config.yml << 'EOF'
health_checks:
  - name: backend-api
    url: http://localhost:8000/api/health
    interval: 30s
    timeout: 10s
    retries: 3
    
  - name: database
    command: pg_isready -h localhost -U postgres
    interval: 30s
    timeout: 5s
    retries: 3
    
  - name: redis
    command: redis-cli ping
    interval: 30s
    timeout: 5s
    retries: 3
    
  - name: frontend
    url: http://localhost:3000
    interval: 60s
    timeout: 10s
    retries: 3
EOF

# 7. Setup Log Aggregation
echo "📝 Setting up log aggregation..."
cat > logging_config.yml << 'EOF'
version: 1
disable_existing_loggers: false
formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    class: pythonjsonlogger.jsonlogger.JsonFormatter

handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    level: INFO
    
  file:
    class: logging.handlers.RotatingFileHandler
    formatter: json
    filename: /var/log/evo-log/app.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    level: INFO

loggers:
  app:
    level: INFO
    handlers: [console, file]
    propagate: false

  uvicorn:
    level: INFO
    handlers: [console]
    propagate: false
EOF

# 8. Setup Uptime Monitoring
echo "⏰ Setting up uptime monitoring..."
cat > uptime_check.sh << 'EOF'
#!/bin/bash
# Uptime monitoring script
ENDPOINTS=(
  "http://localhost:8000/api/health"
  "http://localhost:8000/api/v1/auth/login"
  "http://localhost:3000"
)

for endpoint in "${ENDPOINTS[@]}"; do
  if curl -f -s -o /dev/null "$endpoint"; then
    echo "✅ $endpoint is UP"
  else
    echo "❌ $endpoint is DOWN"
    # Send alert (implement webhook notification)
    curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK" \
      -H 'Content-Type: application/json' \
      -d "{\"text\":\"⚠️ EVO-LOG Alert: $endpoint is DOWN\"}"
  fi
done
EOF

chmod +x uptime_check.sh

# 9. Setup Performance Monitoring
echo "⚡ Setting up performance monitoring..."
cat > performance_monitor.py << 'EOF'
import time
import psutil
import prometheus_client as prom

# Performance metrics
cpu_usage = prom.Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = prom.Gauge('memory_usage_bytes', 'Memory usage in bytes')
disk_usage = prom.Gauge('disk_usage_percent', 'Disk usage percentage')

def collect_performance_metrics():
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().used)
    disk_usage.set(psutil.disk_usage('/').percent)

if __name__ == '__main__':
    collect_performance_metrics()
EOF

# 10. Setup Docker Compose for Monitoring Stack
echo "🐳 Setting up Docker Compose for monitoring stack..."
cat > docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    depends_on:
      - evo-log-backend

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./prometheus_alerts.yml:/etc/alertmanager/alerts.yml
    depends_on:
      - prometheus

volumes:
  prometheus_data:
  grafana_data:
EOF

echo "✅ Active monitoring setup complete!"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3001 (admin/admin)"
echo "🚨 Alertmanager: http://localhost:9093"
