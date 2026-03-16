# Deployment Guide

## Docker Prod

Use `docker-compose.yml` (no volumes/hot-reload).

```
docker compose up --build -d
docker compose logs -f
```

Services:
- postgres, redis
- backend (gunicorn)
- frontend (nginx static)
- worker (celery)

Migrate/seed:
```
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

## Env Prod

```
ENVIRONMENT=production
SECRET_KEY=...
PAYSTACK_SECRET_KEY=sk_live_...
DATABASE_URL=postgresql+asyncpg://.../yua_prod
REDIS_URL=redis://.../0
CELERY_BROKER_URL=redis://.../0
```

## Scaling

- Horizontal backend/worker (multiple replicas)
- Postgres: AWS RDS
- Redis: ElastiCache
- CDN for frontend static
- NGINX reverse proxy + HTTPS (Let's Encrypt)

## Monitoring

Prometheus + Grafana (prometheus-fastapi-instrumentator).

Paystack webhooks: /api/v1/webhooks/paystack