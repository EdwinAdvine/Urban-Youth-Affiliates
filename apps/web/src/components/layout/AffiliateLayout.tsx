import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, ShoppingBag, Link2, TrendingUp, Wallet, User, LogOut,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { NotificationBell } from '@/components/ui/NotificationBell'

const nav = [
  { to: '/affiliate/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/affiliate/marketplace', icon: ShoppingBag, label: 'Marketplace' },
  { to: '/affiliate/links', icon: Link2, label: 'My Links' },
  { to: '/affiliate/earnings', icon: TrendingUp, label: 'Earnings' },
  { to: '/affiliate/payouts', icon: Wallet, label: 'Payouts' },
  { to: '/affiliate/profile', icon: User, label: 'Profile' },
]

export default function AffiliateLayout() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-100">
          <h1 className="text-lg font-bold text-yu-black">Y&U Affiliates</h1>
          <p className="text-xs text-gray-500 mt-1">Affiliate Portal</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-yu-gold-50 text-yu-gold-700 font-semibold border border-yu-gold-200'
                    : 'text-gray-600 hover:bg-gray-100'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-100">
          <p className="text-xs text-gray-400 mb-2 truncate">{user?.email}</p>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto flex flex-col">
        <header className="flex items-center justify-end px-8 pt-6 pb-2">
          <NotificationBell />
        </header>
        <div className="px-8 pb-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
