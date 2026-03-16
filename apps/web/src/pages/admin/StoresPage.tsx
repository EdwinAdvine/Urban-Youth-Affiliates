import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

export default function AdminStoresPage() {
  const { data: stores, isLoading } = useQuery({
    queryKey: ['admin-stores'],
    queryFn: () => api.get('/admin/stores').then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Stores</h1>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Name</th>
                <th className="pb-2">Slug</th>
                <th className="pb-2">Website</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {stores?.map((s: any) => (
                <tr key={s.id}>
                  <td className="py-3 font-medium">{s.name}</td>
                  <td className="py-3 font-mono text-xs text-gray-500">{s.slug}</td>
                  <td className="py-3">
                    {s.website_url ? (
                      <a href={s.website_url} target="_blank" rel="noopener" className="text-yu-gold-600 hover:underline text-xs">
                        Visit
                      </a>
                    ) : '-'}
                  </td>
                  <td className="py-3">
                    <span className={s.active ? 'badge-approved' : 'badge-rejected'}>
                      {s.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="py-3 text-gray-500">{new Date(s.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
