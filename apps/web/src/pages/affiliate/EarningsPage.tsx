import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

const statusBadge: Record<string, string> = {
  pending: 'badge-pending',
  approved: 'badge-approved',
  rejected: 'badge-rejected',
  paid: 'badge-paid',
}

export default function EarningsPage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('')

  const { data: balance } = useQuery({
    queryKey: ['affiliate-balance'],
    queryFn: () => api.get('/affiliate/earnings/balance').then((r) => r.data),
  })

  const { data: conversions, isLoading } = useQuery({
    queryKey: ['affiliate-earnings', page, statusFilter],
    queryFn: () =>
      api
        .get('/affiliate/earnings/conversions', {
          params: { page, page_size: 20, status: statusFilter || undefined },
        })
        .then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Earnings</h1>

      {/* Balance summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Pending', value: balance?.pending ?? 0, color: 'text-yellow-600' },
          { label: 'Approved', value: balance?.approved ?? 0, color: 'text-green-600' },
          { label: 'Total Earned', value: balance?.total_earned ?? 0, color: 'text-yu-gold-600' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card text-center">
            <p className={`text-2xl font-bold ${color}`}>KES {Number(value).toFixed(2)}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Conversions table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Conversion History</h2>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
            className="input w-40 text-sm py-1"
          >
            <option value="">All statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="paid">Paid</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>

        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : conversions?.items?.length === 0 ? (
          <p className="text-gray-400 text-sm">No conversions yet.</p>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2">Order ID</th>
                  <th className="pb-2">Sale Amount</th>
                  <th className="pb-2">Commission</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {conversions?.items?.map((c: any) => (
                  <tr key={c.id}>
                    <td className="py-3 font-mono text-xs">{c.external_order_id}</td>
                    <td className="py-3">KES {Number(c.sale_amount).toFixed(2)}</td>
                    <td className="py-3 font-semibold text-green-600">
                      KES {Number(c.commission_earned).toFixed(2)}
                    </td>
                    <td className="py-3">
                      <span className={statusBadge[c.status] || 'badge-pending'}>{c.status}</span>
                    </td>
                    <td className="py-3 text-gray-500">
                      {new Date(c.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {conversions?.pages > 1 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t text-sm">
                <p className="text-gray-500">
                  Page {conversions.page} of {conversions.pages} ({conversions.total} total)
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-3 py-1 rounded border disabled:opacity-40"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(conversions.pages, p + 1))}
                    disabled={page === conversions.pages}
                    className="px-3 py-1 rounded border disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
