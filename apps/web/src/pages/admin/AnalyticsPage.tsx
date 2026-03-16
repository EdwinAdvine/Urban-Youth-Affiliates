import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { api } from '@/api/client'

export default function AdminAnalyticsPage() {
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['admin-analytics', from, to],
    queryFn: () =>
      api
        .get('/admin/analytics', { params: { from: from || undefined, to: to || undefined } })
        .then((r) => r.data),
  })

  const chartData = data
    ? [
        { name: 'Revenue', value: Number(data.total_revenue) },
        { name: 'Commissions', value: Number(data.total_commissions) },
        { name: 'Pending Payouts', value: Number(data.pending_payouts) },
      ]
    : []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics</h1>
        {/* Date range filter */}
        <div className="flex items-center gap-2 text-sm">
          <input
            type="date"
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            className="input py-1 text-sm"
            placeholder="From"
          />
          <span className="text-gray-400">–</span>
          <input
            type="date"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            className="input py-1 text-sm"
            placeholder="To"
          />
          {(from || to) && (
            <button
              onClick={() => { setFrom(''); setTo('') }}
              className="text-gray-400 hover:text-gray-600 text-xs"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Financial bar chart */}
      {!isLoading && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Financial Overview (KES)</h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(v: number) => `KES ${Number(v).toLocaleString()}`} />
              <Bar dataKey="value" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        {[
          { label: 'Total Affiliates', value: data?.total_affiliates ?? '-' },
          { label: 'Active Affiliates', value: data?.active_affiliates ?? '-' },
          { label: 'Pending Approvals', value: data?.pending_approvals ?? '-' },
          { label: 'Total Clicks', value: data?.total_clicks?.toLocaleString() ?? '-' },
          { label: 'Total Conversions', value: data?.total_conversions?.toLocaleString() ?? '-' },
          { label: 'Conv. Rate', value: data ? `${data.conversion_rate}%` : '-' },
          {
            label: 'Total Revenue',
            value: data ? `KES ${Number(data.total_revenue).toLocaleString()}` : '-',
          },
          {
            label: 'Total Commissions',
            value: data ? `KES ${Number(data.total_commissions).toLocaleString()}` : '-',
          },
          {
            label: 'Pending Payouts',
            value: data ? `KES ${Number(data.pending_payouts).toLocaleString()}` : '-',
          },
        ].map(({ label, value }) => (
          <div key={label} className="card">
            <p className="text-2xl font-bold">{isLoading ? '-' : value}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Top affiliates */}
      {data?.top_affiliates?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Top Affiliates</h2>
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
                  <td className="py-2.5 text-gray-400 font-mono text-xs">{i + 1}</td>
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

      {/* Top products */}
      {data?.top_products?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Top Products</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">#</th>
                <th className="pb-2">Product</th>
                <th className="pb-2 text-right">Conversions</th>
                <th className="pb-2 text-right">Revenue (KES)</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {data.top_products.map((p: any, i: number) => (
                <tr key={p.product_id}>
                  <td className="py-2.5 text-gray-400 font-mono text-xs">{i + 1}</td>
                  <td className="py-2.5 font-medium">{p.name}</td>
                  <td className="py-2.5 text-right">{p.conversions}</td>
                  <td className="py-2.5 text-right font-semibold text-yu-gold-600">
                    {Number(p.revenue).toLocaleString()}
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
