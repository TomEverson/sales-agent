import { Link } from 'react-router-dom'

const contactMethods = [
  {
    icon: '📞',
    label: 'Phone / WhatsApp',
    value: '+66 81 234 5678',
    href: 'https://wa.me/66812345678',
  },
  {
    icon: '✉️',
    label: 'Email',
    value: 'support@travelbase.com',
    href: 'mailto:support@travelbase.com',
  },
  {
    icon: '💬',
    label: 'Telegram',
    value: '@travelbase_support',
    href: 'https://t.me/travelbase_support',
  },
]

const issueCategories = [
  {
    icon: '🎫',
    title: 'Booking Issues',
    description: 'Problems with existing bookings, changes, or cancellations',
  },
  {
    icon: '💳',
    title: 'Payment Problems',
    description: 'Payment failures, refunds, or billing questions',
  },
  {
    icon: '✈️',
    title: 'Flight Changes',
    description: 'Schedule changes, cancellations, or rebooking',
  },
  {
    icon: '🏨',
    title: 'Hotel Issues',
    description: 'Check-in problems, room changes, or extension requests',
  },
]

export default function Support() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold text-slate-800 mb-2">Support Center</h1>
      <p className="text-slate-500 mb-8">
        Need help? Our operators are ready to assist you with any issues.
      </p>

      {/* Contact Methods */}
      <section className="mb-12">
        <h2 className="text-lg font-semibold text-slate-700 mb-4">Contact Us</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {contactMethods.map(({ icon, label, value, href }) => (
            <a
              key={label}
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white border border-slate-200 rounded-xl p-6 text-center hover:border-sky-300 hover:shadow-md transition-all"
            >
              <div className="text-3xl mb-3">{icon}</div>
              <div className="text-sm font-medium text-slate-500 mb-1">{label}</div>
              <div className="text-sky-600 font-semibold">{value}</div>
            </a>
          ))}
        </div>
      </section>

      {/* Issue Categories */}
      <section className="mb-12">
        <h2 className="text-lg font-semibold text-slate-700 mb-4">Common Issues</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {issueCategories.map(({ icon, title, description }) => (
            <div
              key={title}
              className="bg-white border border-slate-200 rounded-xl p-5"
            >
              <div className="text-2xl mb-2">{icon}</div>
              <div className="font-semibold text-slate-800 mb-1">{title}</div>
              <div className="text-sm text-slate-500">{description}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Back to Home */}
      <div className="text-center">
        <Link
          to="/"
          className="text-sky-600 hover:text-sky-700 font-medium text-sm"
        >
          ← Back to Home
        </Link>
      </div>
    </div>
  )
}