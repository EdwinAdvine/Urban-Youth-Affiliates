import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '@/api/client'

const statusBadge: Record<string, string> = {
  pending: 'badge-pending',
  approved: 'badge-approved',
  rejected: 'badge-rejected',
  suspended: 'badge-rejected',
}

export default function AdminAffiliatesPage() {
  const [filter, setFilter] = useState('pending')
  const queryClient = useQueryClient()

  const { data: affiliates, isLoading } = useQuery({
    queryKey: ['admin-affiliates', filter],
    queryFn: () =>
      api.get('/admin/affiliates', { params: { status: filter || undefined } }).then((r) => r.data),
  })

  const action = useMutation({
    mutationFn: ({ id, action }: { id: number; action: string }) =>
      api.post(`/admin/affiliates/${id}/action`, { action }),
    onSuccess: () => {
      toast.success('Action applied')
      queryClient.invalidateQueries({ queryKey: ['admin-affiliates'] })
    },
    onError: () => toast.error('Action failed'),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Affiliates</h1>

      {/* Filter tabs */}
      <div className="flex gap-2">
        {['pending', 'approved', 'rejected', 'suspended', ''].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === s
                ? 'bg-yu-black text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {s || 'All'}
          </button>
        ))}
      </div>

      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : affiliates?.length === 0 ? (
          <p className="text-gray-400">No affiliates found.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Name</th>
                <th className="pb-2">TikTok</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Joined</th>
                <th className="pb-2">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {affiliates?.map((a: any) => (
                <tr key={a.id}>
                  <td className="py-3">
                    <p className="font-medium">{a.full_name || 'N/A'}</p>
                  </td>
                  <td className="py-3">
                    {a.tiktok_url ? (
                      <a href={a.tiktok_url} target="_blank" rel="noopener" className="text-yu-gold-600 hover:underline text-xs">
                        TikTok
                      </a>
                    ) : '-'}
                  </td>
                  <td className="py-3">
                    <span className={statusBadge[a.status] || 'badge-pending'}>{a.status}</span>
                  </td>
                  <td className="py-3 text-gray-500">
                    {new Date(a.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-3">
                    <div className="flex gap-2">
                      {a.status === 'pending' && (
                        <>
                          <button
                            onClick={() => action.mutate({ id: a.id, action: 'approve' })}
                            className="text-xs text-green-600 hover:text-green-800 font-medium"
                          >
                            Approve
                          </button>
                          <button
                            onClick={() => action.mutate({ id: a.id, action: 'reject' })}
                            className="text-xs text-red-500 hover:text-red-700 font-medium"
                          >
                            Reject
                          </button>
                        </>
                      )}
                      {a.status === 'approved' && (
                        <button
                          onClick={() => action.mutate({ id: a.id, action: 'suspend' })}
                          className="text-xs text-orange-500 hover:text-orange-700 font-medium"
                        >
                          Suspend
                        </button>
                      )}
                    </div>
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
