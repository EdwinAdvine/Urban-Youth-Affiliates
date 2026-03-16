import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/api/client'

const statusBadge: Record<string, string> = {
  pending: 'badge-pending',
  approved: 'badge-approved',
  rejected: 'badge-rejected',
  paid: 'badge-paid',
}

export default function AdminConversionsPage() {
  const [filter, setFilter] = useState('pending')
  const queryClient = useQueryClient()

  const { data: conversions, isLoading } = useQuery({
    queryKey: ['admin-conversions', filter],
    queryFn: () =>
      api.get('/admin/conversions', { params: { status: filter || undefined } }).then((r) => r.data),
  })

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: number; action: string }) =>
      api.post(`/admin/conversions/${id}/action`, { action }),
    onSuccess: () => {
      toast.success('Conversion updated')
      queryClient.invalidateQueries({ queryKey: ['admin-conversions'] })
    },
    onError: () => toast.error('Action failed'),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Conversions</h1>

      <div className="flex gap-2">
        {['pending', 'approved', 'rejected', 'paid', ''].map((s) => (
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
                <th className="pb-2">Order ID</th>
                <th className="pb-2">Sale</th>
                <th className="pb-2">Commission</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Date</th>
                <th className="pb-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {conversions?.map((c: any) => (
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
                  <td className="py-3">
                    {c.status === 'pending' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => actionMutation.mutate({ id: c.id, action: 'approve' })}
                          className="text-xs text-green-600 hover:text-green-800 font-medium"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => actionMutation.mutate({ id: c.id, action: 'reject' })}
                          className="text-xs text-red-500 hover:text-red-700 font-medium"
                        >
                          Reject
                        </button>
                      </div>
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
