# EVO-LOG SaaS - Production Deployment Guide

## 🚀 Quick Deployment for 10+ Companies

### Prerequisites
- PostgreSQL 14+
- Redis 7+
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Step 1: Database Setup

```bash
# Create PostgreSQL database
createdb evo_log_prod

# Run migrations
cd evo-log-backend
alembic upgrade head

# Seed initial data
python scripts/seed_data.py
```

### Step 2: Redis Configuration

```bash
# Start Redis
redis-server

# Verify connection
redis-cli ping
# Should return: PONG
```

### Step 3: Backend Configuration

```bash
# Copy production environment
cp .env.production .env

# Edit .env with your production values
nano .env
```

**Critical settings to change:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `DATABASE_URL` - PostgreSQL connection string
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` - For document storage
- `SENTRY_DSN` - For error tracking

### Step 4: Install Dependencies

```bash
cd evo-log-backend
pip install -r requirements.txt
```

### Step 5: Start Services

```bash
# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Start Celery worker (for background tasks)
celery -A app.worker worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.worker beat --loglevel=info
```

### Step 6: Frontend Deployment

```bash
cd evo-log-frontend
npm install
npm run build
# Serve the /out directory with nginx or Vercel
```

### Step 7: Monitoring

Access metrics at:
- **Prometheus metrics**: `http://your-domain/metrics`
- **API docs**: `http://your-domain/api/docs`
- **Health check**: `http://your-domain/api/health`

## 📊 Performance Optimizations Applied

### 1. Database Connection Pooling
- `pool_size=20` - Base connections for 10+ tenants
- `max_overflow=40` - Handle peak loads
- `pool_recycle=1800` - Recycle every 30 min
- `pool_pre_ping=True` - Validate connections

### 2. Redis Caching
- Dashboard KPIs cached for 5 minutes
- Master data cached for 1 hour
- Session data cached for 30 minutes

### 3. Database Indexes
- Tenant ID indexes on all tables
- Date-based indexes for time-series queries
- Composite indexes for common filters

### 4. Query Optimization
- Eager loading with `joinedload()` to prevent N+1
- Pagination on all list endpoints
- Selective field loading where possible

### 5. WebSocket Real-Time
- Redis Pub/Sub for multi-instance support
- Tenant-isolated chat rooms
- Message history limited to 1000 per room

## 🔒 Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Configure production database credentials
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS to production domains only
- [ ] Set up Sentry error tracking
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Set up backup strategy

## 🧪 Testing

```bash
# Run multi-tenant isolation tests
pytest tests/test_multi_tenant_isolation.py -v

# Run all tests
pytest

# Load test with locust (if available)
locust -f tests/locustfile.py
```

## 📈 Scaling Recommendations

### For 10 Companies (Current Configuration)
- 4 API workers
- 2 Celery workers
- 1 Redis instance
- 1 PostgreSQL instance

### For 50 Companies
- 8 API workers
- 4 Celery workers
- Redis Cluster (3 nodes)
- PostgreSQL with read replicas

### For 100+ Companies
- Kubernetes deployment
- Horizontal Pod Autoscaling
- Redis Cluster with sharding
- PostgreSQL with connection pooling (PgBouncer)
- CDN for static assets

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check connection pool status
# Add logging in database.py to monitor
```

### Redis Connection Issues
```bash
# Check Redis health
redis-cli ping

# Check memory usage
redis-cli info memory
```

### Slow Queries
```bash
# Enable slow query logging in PostgreSQL
# Add to postgresql.conf:
log_min_duration_statement = 100
```

## 📞 Support

For production issues, contact:
- Email: tech@evo-log.cm
- Documentation: https://docs.evo-log.cm
