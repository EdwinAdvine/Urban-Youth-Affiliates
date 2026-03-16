import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Users, Package, Store, Megaphone,
  ArrowRightLeft, Wallet, BarChart3, Settings, LogOut,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

const nav = [
  { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/admin/affiliates', icon: Users, label: 'Affiliates' },
  { to: '/admin/stores', icon: Store, label: 'Stores' },
  { to: '/admin/products', icon: Package, label: 'Products' },
  { to: '/admin/campaigns', icon: Megaphone, label: 'Campaigns' },
  { to: '/admin/conversions', icon: ArrowRightLeft, label: 'Conversions' },
  { to: '/admin/payouts', icon: Wallet, label: 'Payouts' },
  { to: '/admin/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/admin/settings', icon: Settings, label: 'Settings' },
]

export default function AdminLayout() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-yu-black text-white flex flex-col">
        <div className="p-6 border-b border-gray-700">
          <h1 className="text-xl font-bold text-yu-gold-400">Y&U Affiliates</h1>
          <p className="text-xs text-gray-400 mt-1">Admin Panel</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {nav.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-yu-gold-500 text-black font-semibold'
                    : 'text-gray-300 hover:bg-gray-800'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-700">
          <p className="text-xs text-gray-400 mb-2">{user?.email}</p>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
