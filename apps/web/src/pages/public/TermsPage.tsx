import { Link } from 'react-router-dom'

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white py-16 px-6">
      <div className="max-w-3xl mx-auto">
        <Link to="/" className="text-yu-gold-600 hover:underline text-sm mb-8 block">← Back to Home</Link>
        <h1 className="text-3xl font-bold mb-8">Affiliate Terms & Conditions</h1>

        <div className="prose max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-xl font-semibold">1. Program Overview</h2>
            <p>
              The Y&U Affiliates Program allows approved participants ("Affiliates") to earn commissions
              by referring customers to Youth & Urbanism stores.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. Eligibility</h2>
            <p>
              You must be 18+ years old, have a valid bank account, and be approved by our team to participate.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. Commission Structure</h2>
            <p>
              Commission rates vary by product and campaign. Default rate is 10% of the net sale value.
              Commissions are credited upon confirmed order completion.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. Payouts</h2>
            <p>
              Minimum payout threshold is KES 500. Payouts are processed via Paystack to your registered
              bank account within 3-5 business days of approval.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. Prohibited Activities</h2>
            <p>
              Self-referrals, cookie stuffing, spam, misleading claims about products, and any form of
              fraud will result in immediate account termination and forfeiture of earnings.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. Termination</h2>
            <p>
              Y&U reserves the right to terminate any affiliate account for violation of these terms.
              Earned commissions for approved conversions will still be paid out.
            </p>
          </section>
        </div>

        <p className="text-sm text-gray-400 mt-12">Version 1.0 — March 2026</p>
      </div>
    </div>
  )
}
