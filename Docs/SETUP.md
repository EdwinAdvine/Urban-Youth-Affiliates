# Setup Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 20+ (nvm use 20)
- pnpm 9+ (`corepack enable pnpm`)
- Python 3.12+ (for local backend dev/tests)
- PostgreSQL client (optional: psql, TablePlus for DB inspection)
- Redis client (optional)

## Environment Variables

Copy `.env.example` to `.env` and edit:

```
# Database (dev uses docker postgres)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/yua_dev
TEST_DATABASE_URL=postgresql+asyncpg://yua_user:password@localhost:5432/yua_test  # for pytest integration

# Redis
REDIS_URL=redis://localhost:6379/0

# Auth/JWT
SECRET_KEY=your-super-secret-key-at-least-32-chars-long-change-in-prod
AFFILIATE_REQUIRE_APPROVAL=true
DEFAULT_COMMISSION_RATE=0.10
MIN_PAYOUT_THRESHOLD=500
COOKIE_DAYS=30

# Paystack (get from dashboard.paystack.com)
PAYSTACK_SECRET_KEY=sk_test_...
PAYSTACK_PUBLIC_KEY=pk_test_...
PAYSTACK_WEBHOOK_SECRET=whsec_...

# Email (Resend/SMTP)
RESEND_API_KEY=...  # or SMTP_*

# Store webhook auth (global or per-store in DB)
STORE_API_KEY=sk_store_123...

# Platform
ENVIRONMENT=development
DEBUG=true
DATABASE_ECHO=true  # SQL logs
```

## Local Development

### Full Stack (Recommended - Docker)

```
pnpm install
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

- Backend hot-reload: http://localhost:8000/docs (Swagger)
- Frontend dev server: http://localhost:3000
- Postgres: localhost:5432 (user:postgres pass:postgres db:yua_dev)
- Redis: localhost:6379

Seed super admin:
```
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

Login: admin@yuaffiliates.co.ke / Admin@1234!

### Backend Only (Local Python)

```
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend Only

```
pnpm --filter @yua/web dev
```

## Testing

**Frontend:**
```
pnpm turbo run test  # Vitest (no files yet)
```

**Backend Unit:**
```
cd backend
pytest tests/test_commission.py -v
```

**Backend Integration:**
Setup test DB/Redis (docker compose up postgres redis), then:
```
pytest tests/ -m integration -v
```

## Common Issues

- **Port conflicts:** Kill processes on 3000/8000/5432/6379
- **Deps slow:** pnpm install --frozen-lockfile
- **Migrations fail:** docker compose exec postgres psql -U postgres -c "CREATE DATABASE yua_dev;"
- **Paystack errors:** Use test keys, verify webhook secrets
- **Vitest no files:** Normal, add *.test.tsx later

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md)