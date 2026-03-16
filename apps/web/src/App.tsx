import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'

// Layouts
import AdminLayout from '@/components/layout/AdminLayout'
import AffiliateLayout from '@/components/layout/AffiliateLayout'

// Auth pages
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'

// Public pages
import LandingPage from '@/pages/public/LandingPage'
import TermsPage from '@/pages/public/TermsPage'
import AffiliateProfilePage from '@/pages/public/AffiliateProfilePage'

// Admin pages
import AdminDashboard from '@/pages/admin/DashboardPage'
import AdminAffiliates from '@/pages/admin/AffiliatesPage'
import AdminProducts from '@/pages/admin/ProductsPage'
import AdminStores from '@/pages/admin/StoresPage'
import AdminCampaigns from '@/pages/admin/CampaignsPage'
import AdminConversions from '@/pages/admin/ConversionsPage'
import AdminPayouts from '@/pages/admin/PayoutsPage'
import AdminAnalytics from '@/pages/admin/AnalyticsPage'
import AdminSettings from '@/pages/admin/SettingsPage'

// Affiliate pages
import AffiliateDashboard from '@/pages/affiliate/DashboardPage'
import AffiliateMarketplace from '@/pages/affiliate/MarketplacePage'
import AffiliateLinkGenerator from '@/pages/affiliate/LinkGeneratorPage'
import AffiliateEarnings from '@/pages/affiliate/EarningsPage'
import AffiliatePayouts from '@/pages/affiliate/PayoutsPage'
import AffiliateProfile from '@/pages/affiliate/ProfilePage'

function PrivateRoute({ children, role }: { children: JSX.Element; role?: string }) {
  const { user, isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (role === 'admin' && !['admin', 'super_admin'].includes(user?.role || '')) {
    return <Navigate to="/affiliate/dashboard" replace />
  }
  if (role === 'affiliate' && user?.role === 'super_admin') {
    return <Navigate to="/admin/dashboard" replace />
  }
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        {/* Public */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/affiliates/:affiliateId" element={<AffiliateProfilePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Admin */}
        <Route
          path="/admin"
          element={
            <PrivateRoute role="admin">
              <AdminLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="affiliates" element={<AdminAffiliates />} />
          <Route path="products" element={<AdminProducts />} />
          <Route path="stores" element={<AdminStores />} />
          <Route path="campaigns" element={<AdminCampaigns />} />
          <Route path="conversions" element={<AdminConversions />} />
          <Route path="payouts" element={<AdminPayouts />} />
          <Route path="analytics" element={<AdminAnalytics />} />
          <Route path="settings" element={<AdminSettings />} />
        </Route>

        {/* Affiliate */}
        <Route
          path="/affiliate"
          element={
            <PrivateRoute role="affiliate">
              <AffiliateLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<AffiliateDashboard />} />
          <Route path="marketplace" element={<AffiliateMarketplace />} />
          <Route path="links" element={<AffiliateLinkGenerator />} />
          <Route path="earnings" element={<AffiliateEarnings />} />
          <Route path="payouts" element={<AffiliatePayouts />} />
          <Route path="profile" element={<AffiliateProfile />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
