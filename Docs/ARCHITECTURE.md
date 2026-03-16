# Architecture Overview

## Tech Stack Diagram

```mermaid
graph TB
  subgraph Frontend ['Frontend (React/Vite)']
    UI[Pages: Admin/Affiliate/Public]
    RQ[TanStack Query API Hooks]
    Z[ Zustand State]
    RT[React Router]
  end

  subgraph Backend ['Backend (FastAPI)']
    API[APIs: Auth/Admin/Affiliate/Webhooks/Tracking]
    SVC[Services: Auth/Tracking/Commission/Payouts]
    DB[SQLAlchemy ORM Models]
    MW[Middleware: RateLimit/Audit/CORS]
    CEL[Tasks: Celery (Notifications)]
  end

  subgraph Infra ['Infrastructure']
    PG[Postgres]
    R[Redis (Cache/Session/RateLimit)]
    PS[Paystack API]
  end

  UI --> RQ
  RQ --> API
  API --> SVC
  SVC --> DB
  DB --> PG
  CEL --> R
  API --> R
  SVC --> PS

  classDef frontend fill:#60a5fa
  classDef backend