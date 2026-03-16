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

export default function AffiliatePayoutsPage() {
  const [amount, setAmount] = useState('')
  const queryClient = useQueryClient()

  const { data: balance } = useQuery({
    queryKey: ['affiliate-balance'],
    queryFn: () => api.get('/affiliate/balance').then((r) => r.data),
  })

  const { data: payouts, isLoading } = useQuery({
    queryKey: ['affiliate-payouts'],
    queryFn: () => api.get('/affiliate/payouts').then((r) => r.data),
  })

  const requestPayout = useMutation({
    mutationFn: (amount: number) =>
      api.post('/affiliate/payouts', { amount }).then((r) => r.data),
    onSuccess: () => {
      toast.success('Payout requested! Admin will process it shortly.')
      setAmount('')
      queryClient.invalidateQueries({ queryKey: ['affiliate-payouts'] })
      queryClient.invalidateQueries({ queryKey: ['affiliate-balance'] })
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.message || 'Request failed'),
  })

  const handleRequest = (e: React.FormEvent) => {
    e.preventDefault()
    const val = parseFloat(amount)
    if (isNaN(val) || val < 500) {
      toast.error('Minimum payout is KES 500')
      return
    }
    requestPayout.mutate(val)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Payouts</h1>

      {/* Request form */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-2">Request Withdrawal</h2>
        <p className="text-sm text-gray-500 mb-4">
          Available: <span className="font-semibold text-green-600">
            KES {Number(balance?.approved ?? 0).toFixed(2)}
          </span>
          {' '}• Minimum KES 500
        </p>
        <form onSubmit={handleRequest} className="flex gap-3">
          <input
            className="input flex-1"
            type="number"
            min={500}
            step={100}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount (KES)"
          />
          <button
            type="submit"
            disabled={requestPayout.isPending}
            className="btn-primary disabled:opacity-50"
          >
            {requestPayout.isPending ? 'Requesting...' : 'Request Payout'}
          </button>
        </form>
      </div>

      {/* History */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Payout History</h2>
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : payouts?.length === 0 ? (
          <p className="text-gray-400 text-sm">No payout requests yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Amount</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Requested</th>
                <th className="pb-2">Paid</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {payouts?.map((p: any) => (
                <tr key={p.id}>
                  <td className="py-3 font-semibold">KES {Number(p.amount).toFixed(2)}</td>
                  <td className="py-3">
                    <span className={statusBadge[p.status] || 'badge-pending'}>{p.status}</span>
                  </td>
                  <td className="py-3 text-gray-500">
                    {new Date(p.requested_at).toLocaleDateString()}
                  </td>
                  <td className="py-3 text-gray-500">
                    {p.paid_at ? new Date(p.paid_at).toLocaleDateString() : '-'}
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
