# Backend Documentation

## Structure

`backend/app/`

- **api/v1/**: Thin routers (FastAPI APIRouter)
  - `admin/`: affiliates.py, analytics.py, campaigns.py, conversions.py, creative_assets.py, payouts.py
  - `affiliate/`: creative_assets.py, dashboard.py, earnings.py, links.py, marketplace.py, notifications.py, payouts.py, profile.py, stats.py
  - `auth/`: login/register/refresh
  - `public/`: ?
  - `tracking.py`: /track/{code}
  - `webhooks/`: conversion

- **models/**: SQLAlchemy ORM (one file per model: user.py, affiliate_profile.py etc.)
- **schemas/**: Pydantic (request/response per domain)
- **services/**: Business logic
  - auth_service.py: JWT, hash, validate
  - catalog_service.py: CRUD stores/products/campaigns
  - commission_service.py: calc_commission(campaign, sale_amount)
  - payout_service.py: request/approve
  - tracking_service.py: generate_code(), record_click(), resolve_click()
  - payments/paystack.py: recipient, transfer, verify

- **tasks/**: Celery (celery_app.py, notifications.py, email_helper.py)
- **middleware/**: audit_log.py, rate_limit.py, request_id.py
- **main.py**: app = FastAPI(lifespan=lifespan), include_router(routers.api_router)
- **routers.py**: api_router = APIRouter(prefix='/api/v1'), include admin/affiliate etc.
- **config.py**: Pydantic Settings (.env)

## Run

Dev: docker compose dev up backend
Local: uvicorn app.main:app --reload

Swagger: /docs | /redoc