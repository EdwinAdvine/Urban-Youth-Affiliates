import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Share2 } from 'lucide-react'
import { api } from '@/api/client'

export default function AffiliateProfilePage() {
  const queryClient = useQueryClient()
  const { data: profile, isLoading } = useQuery({
    queryKey: ['affiliate-profile'],
    queryFn: () => api.get('/affiliate/profile').then((r) => r.data),
  })

  const updateProfile = useMutation({
    mutationFn: (data: any) => api.patch('/affiliate/profile', data),
    onSuccess: () => {
      toast.success('Profile updated')
      queryClient.invalidateQueries({ queryKey: ['affiliate-profile'] })
    },
    onError: () => toast.error('Update failed'),
  })

  const updateBank = useMutation({
    mutationFn: (data: any) => api.post('/affiliate/profile/bank-details', data),
    onSuccess: () => {
      toast.success('Bank details saved!')
      queryClient.invalidateQueries({ queryKey: ['affiliate-profile'] })
    },
    onError: (err: any) =>
      toast.error(err.response?.data?.message || 'Bank update failed'),
  })

  const [profileForm, setProfileForm] = useState({ bio: '', tiktok_url: '', instagram_url: '' })
  const [bankForm, setBankForm] = useState({ bank_name: '', bank_code: '', account_number: '' })

  if (isLoading) return <div className="text-gray-400">Loading profile...</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Profile</h1>

      {/* Status */}
      <div className="card">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-yu-gold-100 rounded-full flex items-center justify-center text-yu-gold-600 font-bold text-lg">
              {profile?.full_name?.[0] || '?'}
            </div>
            <div>
              <p className="font-semibold">{profile?.full_name || 'Unknown'}</p>
              <span className={`text-xs badge-${profile?.status === 'approved' ? 'approved' : 'pending'}`}>
                {profile?.status}
              </span>
            </div>
          </div>
          {profile?.status === 'approved' && (
            <button
              onClick={() => {
                const url = `${window.location.origin}/affiliates/${profile.id}`
                navigator.clipboard.writeText(url)
                toast.success('Profile link copied!')
              }}
              className="flex items-center gap-2 text-sm text-yu-gold-500 border border-yu-gold-400/30 rounded-lg px-3 py-1.5 hover:bg-yu-gold-400/10"
            >
              <Share2 className="w-4 h-4" />
              Share Profile
            </button>
          )}
        </div>
      </div>

      {/* Social links */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Social Links</h2>
        <div className="space-y-3">
          <div>
            <label className="label">TikTok URL</label>
            <input
              className="input"
              defaultValue={profile?.tiktok_url || ''}
              onChange={(e) => setProfileForm({ ...profileForm, tiktok_url: e.target.value })}
              placeholder="https://tiktok.com/@yourhandle"
            />
          </div>
          <div>
            <label className="label">Instagram URL</label>
            <input
              className="input"
              defaultValue={profile?.instagram_url || ''}
              onChange={(e) => setProfileForm({ ...profileForm, instagram_url: e.target.value })}
              placeholder="https://instagram.com/yourhandle"
            />
          </div>
          <div>
            <label className="label">Bio</label>
            <textarea
              className="input resize-none"
              rows={3}
              defaultValue={profile?.bio || ''}
              onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
              placeholder="Tell us about yourself"
            />
          </div>
          <button
            onClick={() => updateProfile.mutate(profileForm)}
            disabled={updateProfile.isPending}
            className="btn-primary disabled:opacity-50"
          >
            {updateProfile.isPending ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>

      {/* Bank details */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-1">Bank Details</h2>
        <p className="text-sm text-gray-500 mb-4">Required for payout requests</p>
        {profile?.paystack_recipient_code && (
          <p className="text-xs text-green-600 bg-green-50 px-3 py-1.5 rounded mb-4">
            ✓ Paystack recipient registered: {profile.paystack_recipient_code}
          </p>
        )}
        <div className="space-y-3">
          <div>
            <label className="label">Bank Name</label>
            <input
              className="input"
              value={bankForm.bank_name}
              onChange={(e) => setBankForm({ ...bankForm, bank_name: e.target.value })}
              placeholder="e.g. Equity Bank"
            />
          </div>
          <div>
            <label className="label">Bank Code</label>
            <input
              className="input"
              value={bankForm.bank_code}
              onChange={(e) => setBankForm({ ...bankForm, bank_code: e.target.value })}
              placeholder="e.g. 054"
            />
          </div>
          <div>
            <label className="label">Account Number</label>
            <input
              className="input"
              value={bankForm.account_number}
              onChange={(e) => setBankForm({ ...bankForm, account_number: e.target.value })}
              placeholder="Your account number"
            />
          </div>
          <button
            onClick={() => updateBank.mutate(bankForm)}
            disabled={updateBank.isPending}
            className="btn-primary disabled:opacity-50"
          >
            {updateBank.isPending ? 'Saving...' : 'Save Bank Details'}
          </button>
        </div>
      </div>
    </div>
  )
}
