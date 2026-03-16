import { useQuery } from '@tanstack/react-query'
import { Link2, TrendingUp, Wallet, MousePointerClick } from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { api } from '@/api/client'

export default function AffiliateDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['affiliate-dashboard'],
    queryFn: () => api.get('/affiliate/dashboard').then((r) => r.data),
  })

  const { data: daily } = useQuery({
    queryKey: ['affiliate-stats-daily'],
    queryFn: () => api.get('/affiliate/stats/daily', { params: { days: 30 } }).then((r) => r.data),
  })

  const { data: statsData } = useQuery({
    queryKey: ['affiliate-stats'],
    queryFn: () => api.get('/affiliate/stats').then((r) => r.data),
  })

  const stats = [
    {
      label: 'Total Clicks',
      value: data?.stats?.total_clicks ?? '-',
      icon: MousePointerClick,
      color: 'text-blue-600 bg-blue-50',
    },
    {
      label: 'Conversions',
      value: data?.stats?.total_conversions ?? '-',
      icon: TrendingUp,
      color: 'text-green-600 bg-green-50',
    },
    {
      label: 'Active Links',
      value: data?.stats?.total_links ?? '-',
      icon: Link2,
      color: 'text-purple-600 bg-purple-50',
    },
    {
      label: 'Approved Balance',
      value: data ? `KES ${Number(data.balance?.approved || 0).toFixed(2)}` : '-',
      icon: Wallet,
      color: 'text-yu-gold-600 bg-yu-gold-50',
    },
  ]

  if (isLoading) {
    return <div className="animate-pulse text-gray-400">Loading dashboard...</div>
  }

  const statusColors: Record<string, string> = {
    pending: 'badge-pending',
    approved: 'badge-approved',
    rejected: 'badge-rejected',
    suspended: 'badge-rejected',
  }

  // Format dates for chart x-axis: "Mar 14"
  const chartData = daily?.series?.map((d: any) => ({
    ...d,
    date: new Date(d.date + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }),
  })) ?? []

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <span className={statusColors[data?.profile_status] || 'badge-pending'}>
          {data?.profile_status}
        </span>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color} mb-3`}>
              <Icon size={20} />
            </div>
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Balance breakdown */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Earnings Breakdown</h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Pending', amount: data?.balance?.pending ?? 0, color: 'text-yellow-600' },
            { label: 'Approved', amount: data?.balance?.approved ?? 0, color: 'text-green-600' },
            { label: 'Paid Out', amount: data?.balance?.paid_out ?? 0, color: 'text-blue-600' },
          ].map(({ label, amount, color }) => (
            <div key={label}>
              <p className={`text-xl font-bold ${color}`}>KES {Number(amount).toFixed(2)}</p>
              <p className="text-sm text-gray-500">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Time-series chart — last 30 days */}
      {chartData.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Performance — Last 30 Days</h2>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={chartData} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
              <defs>
                <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorConv" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} interval="preserveStartEnd" />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="clicks"
                stroke="#6366f1"
                fill="url(#colorClicks)"
                strokeWidth={2}
                dot={false}
                name="Clicks"
              />
              <Area
                type="monotone"
                dataKey="conversions"
                stroke="#22c55e"
                fill="url(#colorConv)"
                strokeWidth={2}
                dot={false}
                name="Conversions"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top links table */}
      {statsData?.top_links?.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Top Performing Links</h2>
            <Link to="/affiliate/links" className="text-sm text-yu-gold-600 hover:underline">
              View all →
            </Link>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Code</th>
                <th className="pb-2 text-right">Clicks</th>
                <th className="pb-2 text-right">Conversions</th>
                <th className="pb-2 text-right">Earned (KES)</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {statsData.top_links.map((link: any) => (
                <tr key={link.id}>
                  <td className="py-2.5 font-mono text-xs">{link.code}</td>
                  <td className="py-2.5 text-right">{link.clicks}</td>
                  <td className="py-2.5 text-right">{link.conversions}</td>
                  <td className="py-2.5 text-right font-semibold text-green-600">
                    {Number(link.earned).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {data?.profile_status === 'pending' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
          Your account is pending approval. You'll be able to generate links once approved.
        </div>
      )}
    </div>
  )
}
