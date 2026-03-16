import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Search, Link2, Copy, ExternalLink } from 'lucide-react'
import { api } from '@/api/client'

export default function MarketplacePage() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['marketplace', search, category],
    queryFn: () =>
      api.get('/affiliate/marketplace', { params: { search, category } }).then((r) => r.data),
  })

  const generateLink = useMutation({
    mutationFn: (campaign_id: number) =>
      api.post('/affiliate/links', { campaign_id }).then((r) => r.data),
    onSuccess: (data) => {
      const url = `${window.location.origin}/track/${data.code}`
      navigator.clipboard.writeText(url).then(() => {
        toast.success('Link copied to clipboard!')
      })
      queryClient.invalidateQueries({ queryKey: ['affiliate-links'] })
    },
    onError: () => toast.error('Failed to generate link'),
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Product Marketplace</h1>

      {/* Search */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-3 text-gray-400" />
          <input
            className="input pl-9"
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <input
          className="input w-48"
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
      </div>

      {/* Products grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="card animate-pulse h-48 bg-gray-100" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items?.map((product: any) => (
            <div key={product.id} className="card hover:shadow-yu-lg transition-shadow">
              {product.image_url && (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="w-full h-40 object-cover rounded-lg mb-3"
                />
              )}
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-sm">{product.name}</h3>
                <span className="text-xs text-gray-500">{product.store_name}</span>
              </div>
              <p className="text-lg font-bold text-yu-gold-600">
                {product.currency} {Number(product.price).toFixed(2)}
              </p>
              {product.commission_rate && (
                <p className="text-xs text-green-600 mt-1">
                  {product.commission_type === 'percent'
                    ? `${(product.commission_rate * 100).toFixed(0)}% commission`
                    : `KES ${product.commission_rate} fixed commission`}
                </p>
              )}
              <div className="flex gap-2 mt-4">
                {product.campaign_id ? (
                  <button
                    onClick={() => generateLink.mutate(product.campaign_id)}
                    disabled={generateLink.isPending}
                    className="btn-primary flex items-center gap-1 text-xs flex-1 justify-center"
                  >
                    <Copy size={14} />
                    {generateLink.isPending ? 'Generating...' : 'Get & Copy Link'}
                  </button>
                ) : (
                  <span className="text-xs text-gray-400">No campaign</span>
                )}
                {product.product_url && (
                  <a
                    href={product.product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary flex items-center gap-1 text-xs px-3"
                  >
                    <ExternalLink size={14} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
