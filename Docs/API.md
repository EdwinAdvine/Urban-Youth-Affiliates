# API Documentation

Base URL: `/api/v1`

**Auth:** JWT Bearer token (login/register → access_token). Refresh endpoint available.

**Rate Limiting:** Redis-based (50 req/min affiliate, 200 admin).

## Auth (Public)

- `POST /auth/login` – `{email, password}` → `{access_token, refresh_token, user}`
- `POST /auth/register` – `{email, password, full_name, phone, terms_accepted}` → profile (pending)
- `POST /auth/refresh` – `{refresh_token}` → new access_token

## Admin (Bearer admin/super_admin)

### Affiliates
- `GET /admin/affiliates` – list (filter status/date), paginated
- `POST /admin/affiliates/{id}/action` – `{action: 'approve|reject|suspend'}`

### Stores/Products/Campaigns
- `POST /admin/stores` → `{name, slug}` → api_key
- `GET /admin/stores`, `PATCH /admin/stores/{id}`
- `POST /admin/products` → `{store_id, name, price, url}`
- `POST /admin/campaigns` → `{store/product_id, type, rate, min_sale}`

### Conversions/Payouts
- `GET /admin/conversions` – list pending, paginated
- `POST /admin/conversions/{id}/action` – `{action: 'approve|reject'}`
- `GET /admin/payouts` – pending requests
- `POST /admin/payouts/{id}/approve`

### Analytics
- `GET /admin/analytics` – platform stats (clicks, conversions, revenue)

## Affiliate (Bearer affiliate)

- `GET /affiliate/dashboard` – stats summary
- `POST /affiliate/links` – `{campaign_id}` → ref_code
- `GET /affiliate/links` – own links + clicks
- `GET /affiliate/earnings/balance` – pending/approved/paid
- `POST /affiliate/payouts` – `{amount}` (min threshold)
- `GET /affiliate/payouts` – history
- `GET /affiliate/marketplace` – products/campaigns grid
- `PATCH /affiliate/profile` – update bio/social/payout details

## Tracking (Public)
- `GET /track/{ref_code}` – record click, redirect to product (302)

## Webhooks (Store API Key header)
- `POST /webhooks/conversion` – `{ref_code, external_order_id, sale_amount}` → pending conversion

## Examples (curl)

**Login:**
```
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yuaffiliates.co.ke","password":"Admin@1234!"}'
```

**Generate Link:**
```
curl -X POST http://localhost:8000/api/v1/affiliate/links \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"campaign_id":1}'
```

Swagger: http://localhost:8000/docs

See backend/app/api/v1/*.py for schemas/validation.