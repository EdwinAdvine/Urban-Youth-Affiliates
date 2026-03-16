import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/api/client'

const statusBadge: Record<string, string> = {
  pending: 'badge-pending',
  processing: 'badge-pending',
  paid: 'badge-paid',
  failed: 'badge-rejected',
}

export default function AdminPayoutsPage() {
  const [filter, setFilter] = useState('pending')
  const queryClient = useQueryClient()

  const { data: payouts, isLoading } = useQuery({
    queryKey: ['admin-payouts', filter],
    queryFn: () =>
      api.get('/admin/payouts', { params: { status: filter || undefined } }).then((r) => r.data),
  })

  const approve = useMutation({
    mutationFn: (id: number) => api.post(`/admin/payouts/${id}/approve`),
    onSuccess: () => {
      toast.success('Payout approved and transfer initiated!')
      queryClient.invalidateQueries({ queryKey: ['admin-payouts'] })
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.message || 'Approval failed'),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Payouts</h1>

      <div className="flex gap-2">
        {['pending', 'processing', 'paid', 'failed', ''].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
              filter === s ? 'bg-yu-black text-white' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Affiliate ID</th>
                <th className="pb-2">Amount</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Transfer Code</th>
                <th className="pb-2">Requested</th>
                <th className="pb-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {payouts?.map((p: any) => (
                <tr key={p.id}>
                  <td className="py-3 text-gray-500">#{p.affiliate_id}</td>
                  <td className="py-3 font-semibold">KES {Number(p.amount).toFixed(2)}</td>
                  <td className="py-3">
                    <span className={statusBadge[p.status] || 'badge-pending'}>{p.status}</span>
                  </td>
                  <td className="py-3 font-mono text-xs text-gray-500">
                    {p.paystack_transfer_code || '-'}
                  </td>
                  <td className="py-3 text-gray-500">
                    {new Date(p.requested_at).toLocaleDateString()}
                  </td>
                  <td className="py-3">
                    {p.status === 'pending' && (
                      <button
                        onClick={() => approve.mutate(p.id)}
                        disabled={approve.isPending}
                        className="text-xs text-green-600 hover:text-green-800 font-medium disabled:opacity-50"
                      >
                        Approve & Transfer
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
