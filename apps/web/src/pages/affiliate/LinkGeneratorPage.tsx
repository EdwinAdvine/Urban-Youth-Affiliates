import { useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Copy, ExternalLink, MousePointerClick, TrendingUp, DollarSign } from 'lucide-react'
import { api } from '@/api/client'

export default function LinkGeneratorPage() {
  const { data: links, isLoading } = useQuery({
    queryKey: ['affiliate-links'],
    queryFn: () => api.get('/affiliate/links').then((r) => r.data),
  })

  const copyLink = (code: string) => {
    const url = `${window.location.origin}/track/${code}`
    navigator.clipboard.writeText(url).then(() => toast.success('Link copied!'))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">My Links</h1>
        <a href="/affiliate/marketplace" className="btn-primary text-sm">
          Generate New Link
        </a>
      </div>

      {isLoading ? (
        <div className="text-gray-400">Loading links...</div>
      ) : links?.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">No links yet. Browse the marketplace to generate your first link.</p>
          <a href="/affiliate/marketplace" className="btn-primary">Go to Marketplace</a>
        </div>
      ) : (
        <div className="space-y-3">
          {links?.map((link: any) => (
            <div key={link.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                      {window.location.origin}/track/{link.code}
                    </code>
                    <button
                      onClick={() => copyLink(link.code)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <Copy size={16} />
                    </button>
                  </div>
                  <p className="text-xs text-gray-400">
                    Created {new Date(link.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-6 text-center ml-6">
                  <div>
                    <div className="flex items-center gap-1 text-blue-600">
                      <MousePointerClick size={14} />
                      <span className="font-semibold">{link.total_clicks}</span>
                    </div>
                    <p className="text-xs text-gray-500">Clicks</p>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-green-600">
                      <TrendingUp size={14} />
                      <span className="font-semibold">{link.total_conversions}</span>
                    </div>
                    <p className="text-xs text-gray-500">Conversions</p>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-yu-gold-600">
                      <DollarSign size={14} />
                      <span className="font-semibold">{Number(link.total_earned).toFixed(0)}</span>
                    </div>
                    <p className="text-xs text-gray-500">KES Earned</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
