import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ExternalLink, TrendingUp, Link2, MousePointer, ShoppingCart } from 'lucide-react'
import api from '@/api/client'

interface PublicAffiliateProfile {
  id: number
  full_name: string
  bio: string | null
  tiktok_url: string | null
  instagram_url: string | null
  twitter_url: string | null
  member_since: string | null
  stats: {
    total_links: number
    total_clicks: number
    total_conversions: number
    conversion_rate: number
  }
}

function StatCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-center">
      <Icon className="w-6 h-6 text-yu-gold-400 mx-auto mb-2" />
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
    </div>
  )
}

export default function AffiliateProfilePage() {
  const { affiliateId } = useParams<{ affiliateId: string }>()

  const { data: profile, isLoading, isError } = useQuery<PublicAffiliateProfile>({
    queryKey: ['public-affiliate', affiliateId],
    queryFn: async () => {
      const res = await api.get<PublicAffiliateProfile>(`/public/affiliates/${affiliateId}`)
      return res.data
    },
    retry: false,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-yu-black flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-yu-gold-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="min-h-screen bg-yu-black text-white flex flex-col items-center justify-center gap-4">
        <p className="text-xl text-gray-400">Affiliate profile not found.</p>
        <Link to="/" className="text-yu-gold-400 hover:underline text-sm">← Back to home</Link>
      </div>
    )
  }

  const memberYear = profile.member_since
    ? new Date(profile.member_since).getFullYear()
    : null

  const socialLinks = [
    { label: 'TikTok', url: profile.tiktok_url },
    { label: 'Instagram', url: profile.instagram_url },
    { label: 'Twitter / X', url: profile.twitter_url },
  ].filter((s) => s.url)

  return (
    <div className="min-h-screen bg-yu-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800">
        <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-yu-gold-400">Y&U Affiliates</Link>
          <Link to="/register" className="btn-primary text-sm">Join the Program</Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-16">
        {/* Profile card */}
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 mb-10">
          {/* Avatar placeholder */}
          <div className="w-20 h-20 rounded-full bg-yu-gold-400 flex items-center justify-center text-3xl font-bold text-black mb-6">
            {profile.full_name.charAt(0).toUpperCase()}
          </div>

          <h1 className="text-3xl font-bold mb-1">{profile.full_name}</h1>
          {memberYear && (
            <p className="text-sm text-gray-500 mb-4">Y&U Affiliate since {memberYear}</p>
          )}
          {profile.bio && (
            <p className="text-gray-300 leading-relaxed mb-6 max-w-xl">{profile.bio}</p>
          )}

          {/* Social links */}
          {socialLinks.length > 0 && (
            <div className="flex flex-wrap gap-3">
              {socialLinks.map(({ label, url }) => (
                <a
                  key={label}
                  href={url!}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-sm text-yu-gold-400 hover:text-yu-gold-300 border border-gray-700 rounded-lg px-3 py-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  {label}
                </a>
              ))}
            </div>
          )}
        </div>

        {/* Stats grid */}
        <h2 className="text-lg font-semibold text-gray-300 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-yu-gold-400" />
          Performance Stats
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-12">
          <StatCard icon={Link2} label="Active Links" value={profile.stats.total_links} />
          <StatCard icon={MousePointer} label="Total Clicks" value={profile.stats.total_clicks.toLocaleString()} />
          <StatCard icon={ShoppingCart} label="Conversions" value={profile.stats.total_conversions.toLocaleString()} />
          <StatCard icon={TrendingUp} label="Conv. Rate" value={`${profile.stats.conversion_rate}%`} />
        </div>

        {/* CTA */}
        <div className="bg-gradient-to-r from-yu-gold-400/10 to-transparent border border-yu-gold-400/20 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-3">Want to earn like {profile.full_name.split(' ')[0]}?</h3>
          <p className="text-gray-400 mb-6">Join Y&U Affiliates and start earning commissions on every sale you refer.</p>
          <Link to="/register" className="btn-primary px-8 py-3 inline-block text-base">
            Apply Now — It's Free
          </Link>
        </div>
      </main>
    </div>
  )
}
