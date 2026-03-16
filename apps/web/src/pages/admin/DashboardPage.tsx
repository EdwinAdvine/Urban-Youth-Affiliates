import { useQuery } from '@tanstack/react-query'
import { Users, TrendingUp, DollarSign, Wallet, MousePointerClick, Clock, AlertCircle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api } from '@/api/client'

export default function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => api.get('/admin/analytics').then((r) => r.data),
  })

  const stats = [
    { label: 'Total Affiliates', value: data?.total_affiliates, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { label: 'Active Affiliates', value: data?.active_affiliates, icon: Users, color: 'text-green-600 bg-green-50' },
    {
      label: 'Pending Approvals',
      value: data?.pending_approvals,
      icon: AlertCircle,
      color: 'text-orange-600 bg-orange-50',
    },
    { label: 'Total Clicks', value: data?.total_clicks?.toLocaleString(), icon: MousePointerClick, color: 'text-purple-600 bg-purple-50' },
    { label: 'Conversions', value: data?.total_conversions?.toLocaleString(), icon: TrendingUp, color: 'text-teal-600 bg-teal-50' },
    {
      label: 'Conv. Rate',
      value: data ? `${data.conversion_rate}%` : '-',
      icon: TrendingUp,
      color: 'text-indigo-600 bg-indigo-50',
    },
    {
      label: 'Total Revenue',
      value: data ? `KES ${Number(data.total_revenue).toLocaleString()}` : '-',
      icon: DollarSign,
      color: 'text-yu-gold-600 bg-yu-gold-50',
    },
    {
      label: 'Total Commissions',
      value: data ? `KES ${Number(data.total_commissions).toLocaleString()}` : '-',
      icon: Wallet,
      color: 'text-red-600 bg-red-50',
    },
    {
      label: 'Pending Payouts',
      value: data ? `KES ${Number(data.pending_payouts).toLocaleString()}` : '-',
      icon: Clock,
      color: 'text-yellow-600 bg-yellow-50',
    },
  ]

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Platform Overview</h1>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color} mb-3`}>
              <Icon size={20} />
            </div>
            <p className="text-2xl font-bold">{isLoading ? '-' : (value ?? 0)}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Top affiliates leaderboard */}
      {data?.top_affiliates?.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Top Affiliates</h2>
            <Link to="/admin/affiliates" className="text-sm text-yu-gold-600 hover:underline">
              View all →
            </Link>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">#</th>
                <th className="pb-2">Name</th>
                <th className="pb-2 text-right">Conversions</th>
                <th className="pb-2 text-right">Earned (KES)</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.top_affiliates.map((a: any, i: number) => (
                <tr key={a.affiliate_id}>
                  <td className="py-2.5 text-gray-400 font-mono">{i + 1}</td>
                  <td className="py-2.5 font-medium">{a.full_name}</td>
                  <td className="py-2.5 text-right">{a.conversions}</td>
                  <td className="py-2.5 text-right font-semibold text-green-600">
                    {Number(a.earned).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
