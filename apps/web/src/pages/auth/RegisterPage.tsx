import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { X } from 'lucide-react'
import toast from 'react-hot-toast'
import { authApi } from '@/api/auth'

function TermsModal({ onClose, onAccept }: { onClose: () => void; onAccept: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
      <div className="bg-white rounded-2xl shadow-yu-lg w-full max-w-lg max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Terms and Conditions</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="overflow-y-auto px-6 py-4 text-sm text-gray-600 space-y-4 flex-1">
          <p>
            By joining Y&U Affiliates you agree to the following terms. Please read them carefully
            before creating your account.
          </p>
          <h3 className="font-semibold text-gray-800">1. Eligibility</h3>
          <p>
            You must be at least 18 years old and legally permitted to enter into contracts in your
            jurisdiction to participate in the Y&U Affiliates program.
          </p>
          <h3 className="font-semibold text-gray-800">2. Commission & Payments</h3>
          <p>
            Commissions are earned on approved sales only. Rates are set per campaign and are subject
            to change with 14 days notice. Payouts are processed via Paystack and require valid bank
            details. Minimum payout threshold is KES 500.
          </p>
          <h3 className="font-semibold text-gray-800">3. Prohibited Activities</h3>
          <p>
            You may not use spam, misleading advertising, cookie stuffing, or any fraudulent method
            to generate clicks or conversions. Violation results in immediate account suspension and
            forfeiture of pending earnings.
          </p>
          <h3 className="font-semibold text-gray-800">4. Account Approval</h3>
          <p>
            All affiliate accounts are subject to review and approval. Y&U Affiliates reserves the
            right to reject, suspend, or terminate any account at its discretion.
          </p>
          <h3 className="font-semibold text-gray-800">5. Full Terms</h3>
          <p>
            The complete terms are available at{' '}
            <Link to="/terms" target="_blank" className="text-yu-gold-600 hover:underline">
              yuaffiliates.co.ke/terms
            </Link>
            .
          </p>
        </div>
        <div className="px-6 py-4 border-t flex gap-3 justify-end">
          <button onClick={onClose} className="btn-secondary">
            Decline
          </button>
          <button
            onClick={() => { onAccept(); onClose(); }}
            className="btn-primary"
          >
            I Accept
          </button>
        </div>
      </div>
    </div>
  )
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    tiktok_url: '',
    instagram_url: '',
    terms_accepted: false,
  })
  const [loading, setLoading] = useState(false)
  const [showTerms, setShowTerms] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.terms_accepted) {
      toast.error('You must accept the terms and conditions')
      return
    }
    setLoading(true)
    try {
      await authApi.register(form)
      toast.success('Registration successful! Please check your email.')
      navigate('/login')
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-yu-black flex items-center justify-center p-4">
      {showTerms && (
        <TermsModal
          onClose={() => setShowTerms(false)}
          onAccept={() => setForm({ ...form, terms_accepted: true })}
        />
      )}

      <div className="bg-white rounded-2xl shadow-yu-lg w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold">Join Y&U Affiliates</h1>
          <p className="text-gray-500 text-sm mt-2">Earn commissions promoting Y&U products</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Full Name *</label>
            <input
              className="input"
              type="text"
              required
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className="label">Email *</label>
            <input
              className="input"
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="label">Password *</label>
            <input
              className="input"
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Min. 8 characters"
            />
          </div>
          <div>
            <label className="label">Phone</label>
            <input
              className="input"
              type="tel"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              placeholder="+254700000000"
            />
          </div>
          <div>
            <label className="label">TikTok URL</label>
            <input
              className="input"
              type="url"
              value={form.tiktok_url}
              onChange={(e) => setForm({ ...form, tiktok_url: e.target.value })}
              placeholder="https://tiktok.com/@yourhandle"
            />
          </div>
          <div>
            <label className="label">Instagram URL</label>
            <input
              className="input"
              type="url"
              value={form.instagram_url}
              onChange={(e) => setForm({ ...form, instagram_url: e.target.value })}
              placeholder="https://instagram.com/yourhandle"
            />
          </div>

          <div className="flex items-start gap-2">
            <input
              id="terms"
              type="checkbox"
              checked={form.terms_accepted}
              onChange={(e) => setForm({ ...form, terms_accepted: e.target.checked })}
              className="mt-1"
            />
            <label htmlFor="terms" className="text-sm text-gray-600">
              I agree to the{' '}
              <button
                type="button"
                onClick={() => setShowTerms(true)}
                className="text-yu-gold-600 hover:underline font-medium"
              >
                Terms and Conditions
              </button>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-yu-gold-600 font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
