import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

export default function AdminCampaignsPage() {
  const { data: campaigns, isLoading } = useQuery({
    queryKey: ['admin-campaigns'],
    queryFn: () => api.get('/admin/campaigns').then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Campaigns</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Name</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Rate</th>
                <th className="pb-2">Cookie Days</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {campaigns?.map((c: any) => (
                <tr key={c.id}>
                  <td className="py-3 font-medium">{c.name}</td>
                  <td className="py-3 text-gray-500">{c.commission_type}</td>
                  <td className="py-3">
                    {c.commission_type === 'percent'
                      ? `${(Number(c.rate) * 100).toFixed(0)}%`
                      : `KES ${Number(c.rate).toFixed(2)}`}
                  </td>
                  <td className="py-3 text-gray-500">{c.cookie_days} days</td>
                  <td className="py-3">
                    <span className={c.active ? 'badge-approved' : 'badge-rejected'}>
                      {c.active ? 'Active' : 'Inactive'}
                    </span>
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
