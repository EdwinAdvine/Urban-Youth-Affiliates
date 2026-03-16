# Y&U Affiliates Platform

## Overview

Y&U Affiliates is a standalone affiliate marketing platform for Youth & Urbanism stores. Young influencers and marketers sign up as affiliates, generate trackable referral links for products/services, earn commissions on reported conversions, and receive payouts via Paystack.

**Key Features:**
- Role-based access: Super Admin, Admin, Affiliate
- Affiliate approval workflow
- Product/Campaign management (admin)
- Referral link generation & click tracking (/track/{code})
- Store webhook conversions (/api/v1/webhooks/conversion)
- Commission calculation (percent/fixed, min sale threshold)
- Balances (pending/approved/paid), payout requests
- Dashboards with analytics (Recharts)
- Marketplace for affiliates
- Notifications (Celery + in-app)
- Rate limiting, audit logs, fraud basics

**Tech Stack:**
- **Backend:** FastAPI (async), SQLAlchemy 2.0 (Postgres), Redis, Celery, Alembic migrations, Pydantic v2
- **Frontend:** React 18, Vite, TypeScript, TanStack Query, Zustand, Tailwind CSS, React Router, Recharts
- **Monorepo:** pnpm workspaces + Turborepo
- **DevOps:** Docker Compose (dev/prod), Paystack integration

Mirrors Urban Home School (UHS) patterns for proven reliability.

## Quick Start (Dev)

1. **Clone & Install:**
   ```
   git clone <repo>
   cd Y&U Affiliates
   cp .env.example .env  # Edit Paystack keys, DB if needed
   pnpm install
   ```

2. **Run Dev Stack:**
   ```
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```
   - Backend: http://localhost:8000/docs (Swagger)
   - Frontend: http://localhost:3000
   - Postgres: localhost:5432 (dev.yml exposes)

3. **Seed Data:**
   ```
   docker compose exec backend python -m app.seed
   ```
   - Creates super_admin (admin@yuaffiliates.co.ke / Admin@1234!)

4. **Test:**
   ```
   # Frontend
   pnpm turbo run test

   # Backend unit
   cd backend && pytest tests/test_commission.py -v

   # Backend integration (needs DB/Redis)
   cd backend && pytest tests/ -m integration -v
   ```

See [SETUP.md](SETUP.md) for full details.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md)

## API

See [API.md](API.md)

## Database

See [DATABASE.md](DATABASE.md)