# Frontend Documentation

## Structure

`apps/web/src/`

- **pages/**: Routed views (React Router v7)
  - `auth/`: LoginPage.tsx, RegisterPage.tsx
  - `admin/`: DashboardPage, AffiliatesPage (approval), StoresPage, ProductsPage, CampaignsPage, ConversionsPage, PayoutsPage, AnalyticsPage, SettingsPage
  - `affiliate/`: DashboardPage, EarningsPage (balance/payouts), LinkGeneratorPage, MarketplacePage, PayoutsPage, ProfilePage
  - `public/`: LandingPage, AffiliateProfilePage (public stats), TermsPage

- **components/**:
  - `layout/`: AdminLayout.tsx, AffiliateLayout.tsx (sidebars, headers)
  - `ui/`: Reusable (Badge, Modal, LoadingSpinner, NotificationBell, Pagination, EmptyState)

- **hooks/**: useDebounce, useLocalStorage, useNotifications, usePagination

- **store/**: authStore.ts (Zustand – user/role/token)

- **api/**: TanStack Query hooks (admin.ts, affiliate.ts, auth.ts, client.ts)

## Tech & Patterns

- **Vite + React 18 + TS**
- **State:** Zustand (simple), TanStack Query (server state)
- **Styling:** Tailwind CSS + PostCSS
- **Charts:** Recharts
- **Icons:** Lucide React
- **Routing:** React Router DOM v7
- **Notifications:** react-hot-toast
- **Motion:** Framer Motion

## Key Pages Flow

**Affiliate Flow:**
Landing → Register → (pending) → Admin approves → Login → Marketplace → Generate Link → Copy/Share → Track clicks → Earnings

**Admin Flow:**
Login → Dashboard → Approve affiliate → Create store/product/campaign → Review conversions/payouts

Dev: `pnpm --filter @yua/web dev`