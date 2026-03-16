import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

export default function AdminProductsPage() {
  const { data: products, isLoading } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => api.get('/admin/products').then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Products</h1>
      </div>
      <div className="card">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Name</th>
                <th className="pb-2">Store</th>
                <th className="pb-2">Price</th>
                <th className="pb-2">Category</th>
                <th className="pb-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {products?.map((p: any) => (
                <tr key={p.id}>
                  <td className="py-3 font-medium">{p.name}</td>
                  <td className="py-3 text-gray-500">{p.store_id}</td>
                  <td className="py-3">{p.currency} {Number(p.price).toFixed(2)}</td>
                  <td className="py-3 text-gray-500">{p.category || '-'}</td>
                  <td className="py-3">
                    <span className={p.active ? 'badge-approved' : 'badge-rejected'}>
                      {p.active ? 'Active' : 'Inactive'}
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
