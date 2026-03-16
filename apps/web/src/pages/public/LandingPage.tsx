import { Link } from 'react-router-dom'
import { TrendingUp, Link2, Wallet, Users } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-yu-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-yu-gold-400">Y&U Affiliates</h1>
          <div className="flex gap-4">
            <Link to="/login" className="text-sm text-gray-300 hover:text-white">Sign In</Link>
            <Link to="/register" className="btn-primary text-sm">Join Now</Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        <h2 className="text-5xl font-bold mb-6 leading-tight">
          Earn Money Promoting<br />
          <span className="text-yu-gold-400">Youth & Urbanism</span>
        </h2>
        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Join Kenya's hottest affiliate program. Share products, earn up to 15% commission on every sale,
          and get paid directly to your bank account.
        </p>
        <Link to="/register" className="btn-primary text-lg px-8 py-4 inline-block">
          Start Earning Today
        </Link>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { icon: Link2, title: 'Generate Links', desc: 'One-click referral link generation for any product' },
            { icon: TrendingUp, title: 'Track Performance', desc: 'Real-time click and conversion analytics' },
            { icon: Wallet, title: 'Earn Commissions', desc: 'Up to 15% commission on every successful sale' },
            { icon: Users, title: 'Join Community', desc: '100+ affiliates already earning with Y&U' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-gray-900 rounded-xl p-6 border border-gray-800">
              <Icon className="text-yu-gold-400 mb-4" size={28} />
              <h3 className="text-lg font-semibold mb-2">{title}</h3>
              <p className="text-gray-400 text-sm">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-6xl mx-auto px-6 py-16 text-center border-t border-gray-800">
        <h3 className="text-3xl font-bold mb-4">Ready to start earning?</h3>
        <p className="text-gray-400 mb-8">Sign up free. Get approved. Start sharing links today.</p>
        <Link to="/register" className="btn-primary text-lg px-8 py-4 inline-block">
          Create Free Account
        </Link>
      </section>

      <footer className="border-t border-gray-800 py-8 text-center text-gray-500 text-sm">
        <p>© {new Date().getFullYear()} Youth & Urbanism. All rights reserved.</p>
        <Link to="/terms" className="text-yu-gold-500 hover:underline ml-4">Terms & Conditions</Link>
      </footer>
    </div>
  )
}
