Ready for review
Select text to add comments on the plan
Y&U Affiliates Platform — Implementation Plan
Context
Youth & Urbanism needs a standalone affiliate marketing platform to power commission-based referral marketing for its network of stores. Young TikTok influencers and marketers sign up as affiliates, generate trackable referral links for products/services, and earn commissions paid via Paystack. The platform is store-agnostic today (stores report conversions via API) and ERP-ready tomorrow (webhook sync). This is a greenfield project in /Users/edwinodhiambo/Documents/Y&U Affiliates — completely empty today.

The tech stack mirrors Urban Home School exactly, enabling fast ramp-up with proven, production-tested patterns. All library versions and architecture decisions are copied from UHS unless noted.

Project Root
/Users/edwinodhiambo/Documents/Y&U Affiliates — all files scaffold directly here (no subfolder wrapper).

Project Structure (Monorepo — mirrors UHS)
/Users/edwinodhiambo/Documents/Y&U Affiliates/
├── backend/                    # FastAPI Python backend
│   ├── alembic/                # DB migrations
│   ├── app/
│   │   ├── api/v1/             # Route handlers (thin)
│   │   │   ├── auth/           # login, register, refresh
│   │   │   ├── admin/          # products, campaigns, approvals, reports, payouts
│   │   │   ├── affiliate/      # dashboard, links, earnings, withdrawal
│   │   │   └── webhooks/       # store sales conversion endpoints
│   │   ├── models/             # SQLAlchemy ORM models (one per file)
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── services/           # Business logic
│   │   │   ├── auth_service.py
│   │   │   ├── tracking_service.py
│   │   │   ├── commission_service.py
│   │   │   └── payments/paystack.py
│   │   ├── middleware/         # Copy from UHS (CORS, rate limit, audit, etc.)
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   ├── tests/
│   ├── requirements.txt
│   ├── alembic.ini
│   └── Dockerfile
├── apps/
│   └── web/                    # React + TypeScript + Vite
│       ├── src/
│       │   ├── pages/
│       │   │   ├── auth/
│       │   │   ├── admin/      # products, affiliates, reports, payouts
│       │   │   ├── affiliate/  # dashboard, link gen, earnings
│       │   │   └── public/     # signup, landing
│       │   ├── components/
│       │   ├── hooks/
│       │   └── api/            # TanStack Query hooks
│       ├── package.json
│       ├── vite.config.ts
│       └── tailwind.config.js
├── packages/
│   ├── api-client/             # Generated API types
│   ├── core-types/             # Shared TS types
│   └── tsconfig/
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── package.json                # Turborepo root
├── pnpm-workspace.yaml
└── turbo.json
Database Schema (PostgreSQL — Alembic migrations)
Migration 001 — users & RBAC
users: id, email, password_hash, role (super_admin|admin|affiliate), is_active, created_at, last_login
Migration 002 — affiliate profiles
affiliate_profiles: id, user_id FK, status (pending|approved|rejected|suspended),
  full_name, phone, bio, tiktok_url, instagram_url, payout_method,
  paystack_recipient_code, approved_by FK, approved_at, created_at
Migration 003 — stores & products
stores: id, name, slug, website_url, admin_id FK, active, created_at
products: id, store_id FK, name, sku, price, currency (KES|USD), description,
  image_url, category, active, created_at
Migration 004 — campaigns (commission rules)
campaigns: id, name, product_id FK (nullable = global), store_id FK (nullable = global),
  commission_type (percent|fixed), rate DECIMAL, min_sale_amount,
  cookie_days (default 30), active, created_at, expires_at
Migration 005 — referrals (click tracking)
referral_links: id, affiliate_id FK, campaign_id FK, code VARCHAR UNIQUE,
  short_url, created_at
referral_clicks: id, link_id FK, ip_address, user_agent, referrer_url,
  country_code, clicked_at, is_flagged
Migration 006 — conversions (sales)
conversions: id, referral_link_id FK, external_order_id VARCHAR,
  sale_amount DECIMAL, commission_earned DECIMAL,
  status (pending|approved|rejected|paid), store_id FK,
  conversion_source (api|webhook|manual), created_at, approved_at
Migration 007 — earnings & payouts
affiliate_balances: id, affiliate_id FK UNIQUE, pending DECIMAL, approved DECIMAL,
  paid_out DECIMAL, updated_at
payout_requests: id, affiliate_id FK, amount DECIMAL, status (pending|processing|paid|failed),
  paystack_transfer_code, paystack_recipient_code, requested_at, paid_at, notes
Migration 008 — global settings
platform_settings: key VARCHAR PK, value TEXT, updated_by FK, updated_at
  (default_commission_rate, min_payout_threshold, cookie_days, require_approval)
Key Files to Create (Phase by Phase)
Phase 0: Scaffold (Week 1)
Backend:

backend/app/main.py — copy UHS pattern, strip edu-specific middleware, keep: CORS, rate limit, audit log, error handling
backend/app/config.py — copy UHS Pydantic Settings, adapt fields: add paystack_secret_key, default_commission_rate, min_payout_threshold, cookie_days, affiliate_require_approval
backend/app/database.py — copy UHS verbatim (async SQLAlchemy 2.0 + asyncpg)
backend/requirements.txt — copy UHS, remove: langchain/AI libs, stripe, mpesa, PayPal, elevenlabs; keep: fastapi, sqlalchemy, asyncpg, alembic, pydantic-settings, python-jose, passlib, redis, httpx, paystack (add)
backend/alembic.ini — copy UHS verbatim
docker-compose.yml — adapt UHS: postgres, redis, backend, frontend (no livekit/worker initially)
Frontend:

apps/web/package.json — copy UHS, remove: tauri, livekit, tiptap, three.js, yjs; keep: react, tanstack-query, react-router, tailwind, recharts, lucide
apps/web/vite.config.ts — copy UHS
package.json (root) — turborepo + pnpm workspaces
pnpm-workspace.yaml — copy UHS pattern
Phase 1: Auth & RBAC (Week 2–3)
Models:

backend/app/models/user.py — role Enum: super_admin, admin, affiliate
backend/app/models/affiliate_profile.py
Services:

backend/app/services/auth_service.py — adapt UHS: remove age-gating/student logic; add affiliate approval gating (affiliates start as pending until approved); keep JWT, bcrypt, refresh token pattern
API Routes:

backend/app/api/v1/auth/login.py
backend/app/api/v1/auth/register.py — public affiliate signup
backend/app/api/v1/auth/refresh.py
Frontend:

apps/web/src/pages/auth/Login.tsx
apps/web/src/pages/auth/Register.tsx — affiliate self-signup form with TikTok/Instagram fields
Phase 2: Catalog & Admin (Week 4–5)
Models: stores.py, products.py, campaigns.py

Services: catalog_service.py — CRUD for stores, products, campaigns

API Routes:

admin/stores.py, admin/products.py, admin/campaigns.py
admin/affiliates.py — approve/reject/suspend affiliates + bulk actions
Frontend:

pages/admin/ProductsPage.tsx
pages/admin/AffiliatesPage.tsx — approval queue with filters
Phase 3: Tracking & Link Gen (Week 6–7)
Models: referral_links.py, referral_clicks.py

Services:

tracking_service.py:
generate_link(affiliate_id, campaign_id) -> ReferralLink — creates unique 8-char code
record_click(code, request) -> None — logs click, sets 1st-party cookie, fraud checks (rate-limit per IP)
resolve_click(code) -> redirect_url — lookup + redirect to product page with ref param
API Routes:

GET /track/{code} — click endpoint (public, redirects)
POST /api/v1/affiliate/links — generate link
GET /api/v1/affiliate/links — list own links with click stats
Frontend:

pages/affiliate/LinkGeneratorPage.tsx — product catalog + one-click link gen + copy button
Phase 4: Conversions & Commissions (Week 8–9)
Models: conversions.py, affiliate_balances.py

Services:

commission_service.py:
record_conversion(order_id, ref_code, sale_amount, store_id) — validate ref, calc commission from campaign rule, update balance
approve_conversion(conversion_id) — moves pending→approved balance
calculate_commission(campaign, sale_amount) -> Decimal
API Routes:

POST /api/v1/webhooks/conversion — stores call this to report sales (API key auth)
GET /api/v1/admin/conversions — list + approve/reject
GET /api/v1/affiliate/earnings — own earnings breakdown
Phase 5: Payouts via Paystack (Week 10–11)
Services:

payments/paystack.py — adapt UHS Paystack service:
create_transfer_recipient(name, bank_code, account_number) → store paystack_recipient_code
initiate_transfer(recipient_code, amount, reason) → returns transfer_code
verify_transfer(transfer_code) → check status
API Routes:

POST /api/v1/affiliate/payout-request — request withdrawal (checks min threshold)
GET /api/v1/admin/payouts — queue of pending payout requests
POST /api/v1/admin/payouts/{id}/approve — triggers Paystack Transfer API
POST /api/v1/webhooks/paystack — Paystack transfer webhook (update status)
Frontend:

pages/affiliate/EarningsPage.tsx — balance + withdrawal request form
pages/admin/PayoutsPage.tsx — payout queue + bulk approve
Phase 6: Dashboards & Polish (Week 12–13)
Frontend Dashboards:

pages/affiliate/DashboardPage.tsx — summary cards (clicks, conversions, pending/approved balance), time-series chart (Recharts), top links table
pages/admin/DashboardPage.tsx — platform stats, top affiliates, conversion rate, revenue
Backend:

GET /api/v1/admin/analytics — aggregate stats (total clicks, conversions, revenue, commissions)
GET /api/v1/affiliate/stats — personal stats with date range filter
Critical Files to Reuse from UHS
File	Path	Reuse Strategy
database.py	UHS/backend/app/database.py	Copy verbatim
alembic.ini	UHS/backend/alembic.ini	Copy verbatim
middleware stack	UHS/backend/app/middleware/	Copy all, strip edu-specific
config.py pattern	UHS/backend/app/config.py	Copy Pydantic Settings structure, adapt fields
auth_service core	UHS/backend/app/services/auth_service.py	Copy JWT/bcrypt/refresh pattern
paystack.py	UHS/backend/app/services/payments/paystack.py	Copy + extend for Transfer API
exception_handlers	UHS/backend/app/	Copy verbatim
docker-compose.yml	UHS/docker-compose.yml	Adapt service names
vite.config.ts	UHS/apps/web/vite.config.ts	Copy verbatim
tailwind.config.js	UHS/apps/web/tailwind.config.js	Copy, update brand colors
pnpm-workspace.yaml	UHS/pnpm-workspace.yaml	Copy verbatim
turbo.json	UHS/turbo.json	Copy verbatim
Key Design Decisions
Affiliate approval flow: Affiliates register with pending status. Admin must approve before they can generate links. Configurable via AFFILIATE_REQUIRE_APPROVAL env var (can be auto-approve for testing).

Commission resolution order: Product-level campaign > Store-level campaign > Global default rate. Falls back to DEFAULT_COMMISSION_RATE from settings.

Conversion endpoint auth: Stores use a shared API key (X-Store-API-Key header) tied to their store record. No OAuth complexity initially.

Fraud basics from day 1: Click tracking checks: (a) same affiliate can't convert their own click, (b) same external_order_id can't convert twice, (c) IP rate-limit on click endpoint (50/hour via existing Redis rate limiter middleware).

Paystack payout flow: Affiliates provide bank details → admin creates Paystack Transfer Recipient once → stores paystack_recipient_code on profile → all future payouts use that code. Matches UHS instructor payout pattern.

Cookie tracking: ref query param is primary; first-party cookie (yu_ref, 30-day default) is backup. Server-side click record is source of truth.

Schema Additions (from review)
Migration 001 — add to users:

email_verified BOOLEAN DEFAULT false
Migration 002 — add to affiliate_profiles:

last_payout_at TIMESTAMP
Migration 009 — creative_assets:

creative_assets: id, campaign_id FK, type (banner|video|image|text),
  url TEXT, size VARCHAR, created_at
Migration 010 — terms tracking (add to affiliate_profiles):

terms_version_accepted INTEGER DEFAULT 1
Add to referral_links:

is_custom BOOLEAN DEFAULT false — for future vanity codes
Add soft-delete to users and products:

is_deleted BOOLEAN DEFAULT false
Cookie name: use yu_aff_ref (not yu_ref) to avoid conflicts with future UHS cookies.

Link code generation: use nanoid or shortuuid for collision-proof unique codes.

Additional Pages (Frontend)
/affiliate/marketplace — searchable product grid (filter by store, category, commission rate)
/ (public landing) — "Join Y&U Affiliates — Earn up to 15% per sale"
Affiliate profile page with public stats
Notifications (Phase 4 addition)
Use Celery + Redis + SMTP/Resend:

New sale → affiliate email + in-app bell
Payout approved → email with receipt
Affiliate approved/rejected → email
PostgreSQL Analytics Views (Phase 6)
Create two views instead of raw queries:

affiliate_performance — per-affiliate: clicks, conversions, total earned, conversion rate
platform_overview — total platform stats, top affiliates, top products
Additional requirements.txt lines
nanoid
celery[redis]
Additional tracking_service note
record_conversion() should accept an optional store_api_key and validate against the stores table — future-proofs multi-store security.

Environment Variables (.env.example additions)
# Platform
AFFILIATE_REQUIRE_APPROVAL=true
DEFAULT_COMMISSION_RATE=0.10
MIN_PAYOUT_THRESHOLD=500
COOKIE_DAYS=30

# Paystack
PAYSTACK_SECRET_KEY=sk_...
PAYSTACK_PUBLIC_KEY=pk_...
PAYSTACK_WEBHOOK_SECRET=...

# Stores (API key for conversion webhooks)
STORE_API_KEY=...  # or per-store keys in DB
Final Polish Details
Phase 0 seed script (backend/app/seed.py):

Run after alembic upgrade head && python -m app.seed
Creates: super_admin user + one test store + global platform_settings + one default global campaign
Creative assets usage:

Admins upload banners/videos per campaign (Phase 2 admin CRUD)
Affiliates see them on marketplace with one-click copy (HTML embed or direct link)
In-app notifications (Phase 6 addition):

notifications table: id, affiliate_id FK, title, message, read BOOLEAN, created_at
Bell icon in affiliate header — Celery handles email; this adds UI polish
Terms acceptance on Register:

Register.tsx shows modal linking to /terms (static markdown page)
On accept → saves terms_version_accepted = current_version
Additional env vars:

CELERY_BROKER_URL=redis://redis:6379/0
EMAIL_BACKEND=smtp   # or resend
Verification Plan
Unit tests (Pytest): Commission calculation edge cases (tiered, fixed, percent), link code generation uniqueness, conversion deduplication.

Integration tests: Full flow — affiliate registers → admin approves → affiliate generates link → click tracked → store POSTs conversion → commission credited → payout requested → admin approves → Paystack transfer initiated.

Manual smoke test:

Create super admin via seed script
Register affiliate via UI
Approve in admin panel
Generate link for a product
Hit /track/{code} — verify click record in DB, cookie set
POST to /api/v1/webhooks/conversion with order data
Verify balance updated in affiliate dashboard
Request payout — verify Paystack Transfer API called (staging key)
Docker Compose up: docker compose up --build — all services healthy, migrations applied, seed data loaded.