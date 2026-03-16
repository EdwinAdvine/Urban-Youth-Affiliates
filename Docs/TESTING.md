# Testing Guide

## Frontend (Vitest)

No test files yet (*.test.tsx).

Run:
```
pnpm turbo run test  # Builds then vitest run
pnpm --filter @yua/web test:watch  # Interactive
```

Add tests in `apps/web/src/__tests__/`.

## Backend (Pytest 8)

**Unit:**
```
cd backend
pytest tests/test_commission.py -v  # Commission logic, code gen
```

**Integration (DB/Redis needed):**
```
docker compose up postgres redis -d
pytest tests/ -m integration -v  # Full flow, API e2e
pytest --cov=app tests/  # Coverage
```

Fixtures (`conftest.py`): test DB (alembic upgrade), AsyncClient (override get_db), rollback.

## End-to-End

Manual:
1. docker compose dev up
2. seed
3. Register affiliate → approve → generate link → /track/code → webhook conversion → payout

CI: GitHub Actions (pnpm test, pytest-cov >80%).